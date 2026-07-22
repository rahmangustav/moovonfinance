"""Test untuk core.subtitle._group_words — segmentasi word-boundary whisper-fallback.

Fungsi ini dipakai transcribe() (jalur whisper-fallback saat SRT TTS-native tak
ada — lihat core/visuals.py). Sebelum perbaikan ini, satu-satunya batas
pemenggalan segmen adalah tanda baca kalimat (. ! ?) atau panjang baris > 72
karakter — TIDAK ada batas waktu. Jeda bicara panjang di tengah kalimat tanpa
tanda baca (mis. narator berhenti sejenak) membuat satu subtitle menggantung di
layar selama jeda itu. core/tts.py._boundaries_to_segments (jalur TTS utama)
sudah punya guard `too_slow` untuk kasus yang sama; _group_words kini menirunya.
"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "core"))

from subtitle import _group_words, _MAX_SECS  # noqa: E402


def _w(start, end, word):
    return SimpleNamespace(start=start, end=end, word=word)


class TestGroupWords(unittest.TestCase):
    def test_potong_di_tanda_baca_kalimat(self):
        words = [_w(0.0, 0.3, "Halo"), _w(0.3, 0.6, " dunia.")]
        segs = _group_words(words)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["text"], "Halo dunia.")
        self.assertEqual(segs[0]["start"], 0.0)
        self.assertEqual(segs[0]["end"], 0.6)

    def test_potong_saat_baris_kepanjangan(self):
        words = [_w(i * 0.2, i * 0.2 + 0.2, " kata") for i in range(20)]
        segs = _group_words(words)
        self.assertGreater(len(segs), 1)
        for s in segs:
            self.assertLessEqual(len(s["text"]), 72 + len(" kata"))

    def test_bicara_panjang_tanpa_titik_tetap_dipotong_di_batas_waktu(self):
        # Regresi utama: dulu tak ada batas waktu sama sekali — kalimat panjang
        # tanpa tanda baca dan tanpa melebihi 72 char (kata-kata pendek) akan
        # menyatu jadi SATU segmen yang tumbuh TANPA BATAS selama whisper tak
        # kunjung mendeteksi akhir kalimat. 10 kata pendek (~30 char, jauh di
        # bawah 72) berjarak 0,8 dtk, total ~7,9 dtk — harus dipotong begitu
        # rentang buffer menyentuh _MAX_SECS, bukan menunggu 72 char/titik.
        words = [_w(i * 0.8, i * 0.8 + 0.7, f" w{i}") for i in range(10)]
        segs = _group_words(words)
        self.assertGreater(len(segs), 1)
        for s in segs:
            self.assertLess(s["end"] - s["start"], _MAX_SECS + 1.0)
        # semua kata tetap tercakup, tak ada yang hilang
        self.assertEqual(segs[0]["start"], 0.0)
        self.assertEqual(segs[-1]["end"], 7.9)

    def test_jeda_persis_di_bawah_batas_tidak_dipotong(self):
        words = [_w(0.0, 0.5, "Nah"), _w(_MAX_SECS - 0.5, _MAX_SECS - 0.2, " ternyata")]
        segs = _group_words(words)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["text"], "Nah ternyata")

    def test_tanpa_titik_tanpa_jeda_panjang_tetap_satu_segmen(self):
        words = [_w(0.0, 0.3, "Halo"), _w(0.3, 0.6, " dunia")]
        segs = _group_words(words)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["text"], "Halo dunia")

    def test_sisa_buffer_di_akhir_tetap_masuk(self):
        segs = _group_words([_w(0.0, 0.3, "Halo")])
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["text"], "Halo")

    def test_list_kosong(self):
        self.assertEqual(_group_words([]), [])


if __name__ == "__main__":
    unittest.main()
