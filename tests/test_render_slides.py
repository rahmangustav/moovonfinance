"""Test render_slides.py — pola acuan render slide on-brand, dipakai untuk
SETIAP slide di SETIAP video. Modul ini belum pernah punya test: kalau ada
regresi (mis. font salah role, wrap infinite loop, ukuran kanvas geser),
video baru bisa gagal render atau keluar rusak tanpa ketahuan sampai upload.
Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw

import moovon_theme as T
from render_slides import (
    fmt_rp,
    fmt_pct,
    _wrap,
    render_cover,
    render_section,
    render_valuation,
    render_snapshot,
    render_closing,
)


class FmtRpTest(unittest.TestCase):
    def test_ribuan_pakai_titik_gaya_indonesia(self):
        self.assertEqual(fmt_rp(1234567), "1.234.567")

    def test_desimal_dibulatkan_tanpa_koma(self):
        self.assertEqual(fmt_rp(8149.6), "8.150")

    def test_nol(self):
        self.assertEqual(fmt_rp(0), "0")

    def test_negatif(self):
        self.assertEqual(fmt_rp(-1234567), "-1.234.567")


class FmtPctTest(unittest.TestCase):
    def test_positif_tanpa_plus_default(self):
        self.assertEqual(fmt_pct(0.366), "36,6%")

    def test_positif_dengan_plus(self):
        self.assertEqual(fmt_pct(0.15, plus=True), "+15,0%")

    def test_negatif_selalu_pakai_minus(self):
        self.assertEqual(fmt_pct(-0.093), "-9,3%")

    def test_negatif_plus_true_tetap_minus_bukan_plus_minus(self):
        self.assertEqual(fmt_pct(-0.05, plus=True), "-5,0%")

    def test_nol_tanpa_plus(self):
        self.assertEqual(fmt_pct(0.0), "0,0%")


class WrapTest(unittest.TestCase):
    def setUp(self):
        img = Image.new("RGB", (10, 10))
        self.d = ImageDraw.Draw(img)
        self.f = T.font("body", 34)

    def test_teks_pendek_satu_baris(self):
        lines = _wrap(self.d, "Laba naik", self.f, 2000)
        self.assertEqual(lines, ["Laba naik"])

    def test_teks_panjang_dipecah_banyak_baris(self):
        text = "Kenapa bank paling solid malah paling ditinggal investor asing?"
        lines = _wrap(self.d, text, self.f, 300)
        self.assertGreater(len(lines), 1)
        # tiap baris harus muat di max_w (toleransi kata tunggal yang overflow)
        rejoined = " ".join(lines)
        self.assertEqual(rejoined, text)

    def test_kata_tunggal_lebih_lebar_dari_max_w_tidak_infinite_loop(self):
        # `or not cur` di render_slides._wrap menjamin progres walau kata
        # pertama sendirian sudah melebihi max_w — pastikan tidak macet.
        lines = _wrap(self.d, "SUPERKALIFRAGILISTIKEKSPIALIDOSIUS", self.f, 5)
        self.assertEqual(lines, ["SUPERKALIFRAGILISTIKEKSPIALIDOSIUS"])

    def test_string_kosong(self):
        self.assertEqual(_wrap(self.d, "", self.f, 2000), [])


class RenderSlideSmokeTest(unittest.TestCase):
    """Smoke test: tiap fungsi render_* harus jalan tanpa error dan hasilkan
    kanvas 1920x1080 RGB (ukuran final wajib video 16:9), berapa pun isinya."""

    def _assert_valid_slide(self, img):
        self.assertEqual(img.size, (T.WIDTH, T.HEIGHT))
        self.assertEqual(img.mode, "RGB")

    def test_render_cover(self):
        img = render_cover(
            eyebrow="Bedah Saham",
            title="Laba Naik, Kredit Sehat, Tapi Dibuang Asing.",
            ticker="BBCA",
            subtitle="Kenapa bank paling solid malah paling ditinggal investor asing?",
            tanggal="19 JUL 2026",
        )
        self._assert_valid_slide(img)

    def test_render_cover_judul_sangat_panjang_tetap_muat(self):
        # font auto-fit turun sampai <=3 baris (px 108 -> 64) — pastikan tidak crash
        judul = " ".join(["Kata"] * 40)
        img = render_cover(
            eyebrow="Bedah Saham", title=judul, ticker="BBRI",
            subtitle="Subjudul.", tanggal="19 JUL 2026",
        )
        self._assert_valid_slide(img)

    def test_render_section_mode_naratif(self):
        img = render_section(1, 5, "Fundamental Solid", "Laba tumbuh dua digit.", "BMRI")
        self._assert_valid_slide(img)

    def test_render_section_mode_statement_judul_kosong(self):
        img = render_section(2, 5, "", "Kutipan besar tanpa judul terpisah.", "BMRI")
        self._assert_valid_slide(img)

    def test_render_section_tanpa_ticker(self):
        img = render_section(3, 5, "Ringkasan", "Tidak ada ticker spesifik.", "")
        self._assert_valid_slide(img)

    def test_render_valuation_verdict_beli(self):
        img = render_valuation("BBCA", harga=5800, nilai_wajar=9150, catatan="Diskon lebar.")
        self._assert_valid_slide(img)

    def test_render_valuation_verdict_tahan(self):
        img = render_valuation("BBRI", harga=8000, nilai_wajar=9150)
        self._assert_valid_slide(img)

    def test_render_valuation_verdict_hindari(self):
        img = render_valuation("BMRI", harga=10000, nilai_wajar=9150)
        self._assert_valid_slide(img)

    def test_render_valuation_nilai_wajar_nol_raises_valueerror(self):
        # nilai_wajar=0 (placeholder draft belum diisi/salah ketik) sebelumnya
        # bikin ZeroDivisionError mentah di gauge (lo == hi == 0) — meledak
        # SETELAH TTS selesai, membuang satu run render penuh. Harus gagal
        # cepat & jelas, bukan crash kriptik di tengah render.
        with self.assertRaises(ValueError):
            render_valuation("BBCA", harga=5800, nilai_wajar=0)

    def test_render_valuation_nilai_wajar_negatif_raises_valueerror(self):
        with self.assertRaises(ValueError):
            render_valuation("BBCA", harga=5800, nilai_wajar=-100)

    def test_render_snapshot(self):
        img = render_snapshot(
            "BBCA", "BBCA — Kuartal I 2026",
            metrics=[
                ("Laba bersih", "14,7 T", "up"),
                ("NPL", "1,8%", "up"),
                ("PBV", "2,5x", None),
                ("Net sell asing", "32,4 T", "down"),
            ],
        )
        self._assert_valid_slide(img)

    def test_render_snapshot_warna_key_tak_dikenal_tidak_crash(self):
        # Regresi: `ck` mentah dari JSON draft (## SNAPSHOT:) — kalau ada
        # salah ketik di luar kontrak "up"/"down"/"neutral"/null (mis.
        # "positive"), render_snapshot dulu melempar KeyError mentah lewat
        # T.RGB[ck], mematikan create_video SETELAH TTS selesai. Sekarang
        # harus fallback ke warna netral, bukan crash.
        img = render_snapshot(
            "BBCA", "BBCA — Kuartal I 2026",
            metrics=[("Laba bersih", "14,7 T", "positive")],
        )
        self._assert_valid_slide(img)

    def test_render_snapshot_warna_key_tipe_salah_tidak_crash(self):
        # JSON draft yang malformed bisa memuat elemen ke-3 bukan string
        # (mis. list/number) — pastikan itu juga tidak crash.
        img = render_snapshot(
            "BBCA", "BBCA — Kuartal I 2026",
            metrics=[("Laba bersih", "14,7 T", 123)],
        )
        self._assert_valid_slide(img)

    def test_render_snapshot_nilai_bukan_string_tidak_crash(self):
        # Regresi: penulis draft kadang lupa kutip angka murni di JSON
        # ## SNAPSHOT: (mis. ["ROE", 22.4, "up"] alih-alih ["ROE", "22,4%",
        # "up"]) — tetap JSON valid, lolos cek_draft.py, tapi dulu meledak
        # TypeError di PIL ImageDraw.text (butuh str, bukan float).
        img = render_snapshot(
            "BBCA", "BBCA — Kuartal I 2026",
            metrics=[("ROE", 22.4, "up")],
        )
        self._assert_valid_slide(img)

    def test_render_snapshot_label_none_tidak_crash(self):
        # Regresi: label None (mis. json.load hasil "null" bukan string)
        # dulu meledak AttributeError di lbl.upper().
        img = render_snapshot(
            "BBCA", "BBCA — Kuartal I 2026",
            metrics=[(None, "22,4%", "up")],
        )
        self._assert_valid_slide(img)

    def test_render_closing(self):
        img = render_closing("BBCA")
        self._assert_valid_slide(img)

    def test_render_closing_headline_custom(self):
        img = render_closing("BBRI", headline="Sampai jumpa di analisis berikutnya.")
        self._assert_valid_slide(img)


if __name__ == "__main__":
    unittest.main()
