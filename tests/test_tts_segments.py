"""Test untuk fungsi murni core/tts.py — pembersih naskah & pemenggal
segmen subtitle dari word-boundary TTS (edge-tts & ElevenLabs)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.tts import (
    clean_script,
    _boundaries_to_segments,
    _split_for_tts,
    _chars_to_words,
    _MAX_CHARS,
    _MAX_SECS,
    _ELEVEN_MAX,
)


class TestCleanScript(unittest.TestCase):
    def test_buang_anotasi_kurung_siku(self):
        self.assertEqual(clean_script("Halo [jeda 1 detik] dunia"), "Halo  dunia")

    def test_buang_markdown_heading(self):
        self.assertEqual(clean_script("### Judul Besar"), "Judul Besar")

    def test_buang_penanda_tebal_dan_miring_pertahankan_isi(self):
        self.assertEqual(clean_script("Ini **tebal** dan *miring*"), "Ini tebal dan miring")

    def test_rapikan_baris_kosong_berlebih(self):
        self.assertEqual(clean_script("Baris satu\n\n\n\n\nBaris dua"), "Baris satu\n\nBaris dua")

    def test_strip_spasi_di_pinggir(self):
        self.assertEqual(clean_script("  naskah bersih  "), "naskah bersih")

    def test_kombinasi_semua_aturan(self):
        naskah = "# Judul\n\n\n\n**Tebal** [catatan produksi] biasa saja"
        self.assertEqual(clean_script(naskah), "Judul\n\nTebal  biasa saja")


class TestBoundariesToSegments(unittest.TestCase):
    def test_daftar_kosong_hasil_kosong(self):
        self.assertEqual(_boundaries_to_segments([]), [])

    def test_satu_kalimat_pendek_jadi_satu_segmen(self):
        words = [(0.0, 0.3, "Halo"), (0.3, 0.8, "dunia.")]
        segs = _boundaries_to_segments(words)
        self.assertEqual(segs, [{"start": 0.0, "end": 0.8, "text": "Halo dunia."}])

    def test_dipenggal_saat_tanda_baca_kalimat(self):
        words = [
            (0.0, 0.3, "Satu."), (0.3, 0.6, "Dua!"), (0.6, 0.9, "Tiga?"),
        ]
        segs = _boundaries_to_segments(words)
        self.assertEqual([s["text"] for s in segs], ["Satu.", "Dua!", "Tiga?"])

    def test_dipenggal_saat_teks_terlalu_panjang_tanpa_titik(self):
        # 68 karakter = _MAX_CHARS: kata-kata pendek berulang tanpa tanda baca
        # kalimat harus tetap terpenggal begitu ambang panjang terlampaui.
        # Pengecekan terjadi SETELAH kata ditambahkan, jadi segmen boleh
        # melampaui _MAX_CHARS sebanyak-banyaknya panjang satu kata terakhir.
        words = [(i * 0.2, i * 0.2 + 0.1, "kata") for i in range(20)]
        segs = _boundaries_to_segments(words)
        self.assertGreater(len(segs), 1)
        total_kata = sum(s["text"].count("kata") for s in segs)
        self.assertEqual(total_kata, 20)
        for s in segs[:-1]:
            self.assertGreaterEqual(len(s["text"]), _MAX_CHARS)

    def test_dipenggal_saat_durasi_terlalu_lama_walau_teks_pendek(self):
        # Buffer menumpuk beberapa kata dulu (belum ada tanda baca kalimat),
        # lalu terpenggal begitu rentang waktu buffer >= _MAX_SECS — kata
        # berikutnya sesudahnya mulai buffer baru.
        words = [
            (0.0, 0.5, "Satu"), (0.6, 1.0, "dua"),
            (_MAX_SECS + 0.5, _MAX_SECS + 1.0, "tiga"),
            (_MAX_SECS + 1.1, _MAX_SECS + 1.5, "lagi"),
        ]
        segs = _boundaries_to_segments(words)
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0]["text"], "Satu dua tiga")
        self.assertGreaterEqual(segs[0]["end"] - segs[0]["start"], _MAX_SECS)
        self.assertEqual(segs[1]["text"], "lagi")

    def test_sisa_buffer_tanpa_tanda_baca_tetap_dikeluarkan(self):
        words = [(0.0, 0.3, "belum"), (0.3, 0.6, "selesai")]
        segs = _boundaries_to_segments(words)
        self.assertEqual(segs, [{"start": 0.0, "end": 0.6, "text": "belum selesai"}])

    def test_kata_digabung_dengan_satu_spasi(self):
        words = [(0.0, 0.1, "a"), (0.1, 0.2, "b"), (0.2, 0.3, "c.")]
        segs = _boundaries_to_segments(words)
        self.assertEqual(segs[0]["text"], "a b c.")


class TestSplitForTts(unittest.TestCase):
    def test_string_kosong_hasil_kosong(self):
        self.assertEqual(_split_for_tts(""), [])

    def test_teks_pendek_jadi_satu_potongan(self):
        self.assertEqual(_split_for_tts("Satu kalimat saja."), ["Satu kalimat saja."])

    def test_gabung_kalimat_sampai_mendekati_batas(self):
        chunks = _split_for_tts("Kalimat satu. Kalimat dua. Kalimat tiga.", limit=15)
        self.assertEqual(chunks, ["Kalimat satu.", "Kalimat dua.", "Kalimat tiga."])
        for c in chunks:
            self.assertLessEqual(len(c), 15)

    def test_dua_kalimat_pendek_digabung_jadi_satu_potongan(self):
        chunks = _split_for_tts("Hai. Apa kabar?", limit=100)
        self.assertEqual(chunks, ["Hai. Apa kabar?"])

    def test_satu_kalimat_melebihi_batas_tetap_utuh_tak_terpotong(self):
        # Perilaku saat ini: pemenggalan hanya terjadi di batas kalimat, jadi
        # satu kalimat tunggal yang lebih panjang dari limit dibiarkan lolos
        # utuh (bukan bug baru — didokumentasikan lewat test ini).
        kalimat_panjang = ("kata " * 500).strip() + "."
        chunks = _split_for_tts(kalimat_panjang, limit=_ELEVEN_MAX)
        self.assertEqual(len(chunks), 1)
        self.assertGreater(len(chunks[0]), _ELEVEN_MAX)


class TestCharsToWords(unittest.TestCase):
    def test_dua_kata_dipisah_spasi(self):
        chars = list("hi lo")
        starts = [0.0, 0.1, 0.2, 0.3, 0.4]
        ends = [0.1, 0.2, 0.3, 0.4, 0.5]
        words = _chars_to_words(chars, starts, ends)
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0][2], "hi")
        self.assertEqual(words[1][2], "lo")
        self.assertEqual(words[0][0], 0.0)
        self.assertEqual(words[1][1], 0.5)

    def test_kata_tunggal_tanpa_spasi_penutup(self):
        chars = list("ok")
        starts = [1.0, 1.1]
        ends = [1.1, 1.2]
        words = _chars_to_words(chars, starts, ends)
        self.assertEqual(words, [(1.0, 1.2, "ok")])

    def test_spasi_beruntun_tidak_hasilkan_kata_kosong(self):
        chars = list("a  b")
        starts = [0.0, 0.1, 0.2, 0.3]
        ends = [0.1, 0.2, 0.3, 0.4]
        words = _chars_to_words(chars, starts, ends)
        self.assertEqual([w[2] for w in words], ["a", "b"])

    def test_offset_diterapkan_ke_semua_waktu(self):
        chars = list("hai")
        starts = [0.0, 0.1, 0.2]
        ends = [0.1, 0.2, 0.3]
        words = _chars_to_words(chars, starts, ends, offset=10.0)
        self.assertEqual(words, [(10.0, 10.3, "hai")])

    def test_input_kosong_hasil_kosong(self):
        self.assertEqual(_chars_to_words([], [], []), [])


if __name__ == "__main__":
    unittest.main()
