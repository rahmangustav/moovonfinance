"""Test _donut_center_text() -- teks total di tengah lubang donut chart.

Bug nyata yang ditangkap di sini: sebelum perbaikan, kalau persentase riset
sedikit lebih dari 100 (sangat mungkin terjadi -- angka dibulatkan dari
riset web, mis. alokasi portofolio 30+25+20+15+10,4 = 100,4), teks di
tengah donut tampil TANPA tanda '%' (mis. "100,4" alih-alih "100,4%"),
beda sendiri dari semua kasus lain yang selalu berakhiran '%'. Ini tampil
langsung di video yang sudah publish (chart on-brand), jadi salah format
di sini bukan bug tersembunyi -- penonton yang melihatnya.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from chart_templates import _donut_center_text


class DonutCenterTextTest(unittest.TestCase):
    def test_total_persis_100(self):
        self.assertEqual(_donut_center_text([45, 25, 20, 10]), "100%")

    def test_total_di_bawah_100_dibulatkan_dan_pakai_persen(self):
        # 30+25+20+15 = 90 -> tetap harus diakhiri '%'
        self.assertEqual(_donut_center_text([30, 25, 20, 15]), "90%")

    def test_total_sedikit_di_atas_100_tetap_pakai_persen(self):
        # kasus nyata: alokasi riset dibulatkan, totalnya 100.4 bukan 100 --
        # sebelum perbaikan ini menghasilkan "100,4" TANPA '%'
        center = _donut_center_text([30, 25, 20, 15, 10.4])
        self.assertTrue(center.endswith("%"), f"harus diakhiri '%', dapat: {center!r}")
        self.assertEqual(center, "100,4%")

    def test_total_101_bulat_tetap_pakai_persen(self):
        center = _donut_center_text([34, 34, 33])  # sum = 101
        self.assertTrue(center.endswith("%"), f"harus diakhiri '%', dapat: {center!r}")
        self.assertEqual(center, "101%")

    def test_total_hampir_100_karena_floating_point(self):
        # 33.33+33.33+33.34 = 100.0 tapi lewat floating point bisa 99.99999999...
        center = _donut_center_text([33.33, 33.33, 33.34])
        self.assertEqual(center, "100%")

    def test_total_jauh_di_bawah_100(self):
        # breakdown parsial (mis. cuma top-3 kategori dari banyak kategori)
        self.assertEqual(_donut_center_text([40, 20, 15]), "75%")


if __name__ == "__main__":
    unittest.main()
