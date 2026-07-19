"""Test _num() & _parse_num() di core/chart_templates.py — util format angka
gaya Indonesia (titik ribuan, koma desimal) yang dipakai SETIAP chart & tabel
finansial di pipeline (donut, bar, comparison_table). Belum pernah punya test
sama sekali walau salah format di sini berarti angka riset tampil salah di
video yang sudah publish. Jalankan: python -m pytest tests/ -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from chart_templates import _num, _parse_num


class NumFormatTest(unittest.TestCase):
    def test_bilangan_bulat_pakai_titik_ribuan(self):
        self.assertEqual(_num(12500), "12.500")
        self.assertEqual(_num(1234567), "1.234.567")

    def test_float_bulat_tanpa_desimal(self):
        # 12500.0 harus tampil sebagai bilangan bulat, bukan "12.500,0"
        self.assertEqual(_num(12500.0), "12.500")

    def test_desimal_pakai_koma(self):
        self.assertEqual(_num(5.45), "5,45")
        self.assertEqual(_num(5.4), "5,4")

    def test_desimal_1_angka_bila_cukup(self):
        # aturan di docstring: "5,45 jangan jadi 5,5" -> tapi kalau cukup 1
        # desimal (mis. 5.40), jangan tampilkan 2 desimal berlebihan
        self.assertEqual(_num(5.40), "5,4")

    def test_nol(self):
        self.assertEqual(_num(0), "0")

    def test_negatif(self):
        self.assertEqual(_num(-1234.5), "-1.234,5")

    def test_nilai_non_numerik_dikembalikan_apa_adanya(self):
        self.assertEqual(_num("abc"), "abc")

    def test_none_tidak_error(self):
        # bug class yang mahal: TypeError saat astronomi/None masuk chart spec
        self.assertEqual(_num(None), "None")


class ParseNumTest(unittest.TestCase):
    def test_rupiah_dengan_ribuan(self):
        self.assertEqual(_parse_num("Rp 1.234.567"), 1234567.0)

    def test_negatif_dengan_prefix_mata_uang(self):
        self.assertEqual(_parse_num("-Rp1.234"), -1234.0)

    def test_format_indonesia_ribuan_dan_desimal(self):
        self.assertEqual(_parse_num("1.234.567,89"), 1234567.89)

    def test_persen(self):
        self.assertEqual(_parse_num("45%"), 45.0)
        self.assertEqual(_parse_num("-45%"), -45.0)

    def test_notasi_akuntansi_kurung_adalah_negatif(self):
        self.assertEqual(_parse_num("(123)"), -123.0)
        self.assertEqual(_parse_num("(1.234,56)"), -1234.56)

    def test_desimal_koma_saja(self):
        self.assertEqual(_parse_num("0,5"), 0.5)

    def test_string_kosong_mengembalikan_none(self):
        self.assertIsNone(_parse_num(""))

    def test_teks_bukan_angka_mengembalikan_none(self):
        self.assertIsNone(_parse_num("abc"))

    def test_ribuan_tanpa_desimal(self):
        self.assertEqual(_parse_num("1.234"), 1234.0)

    def test_prefix_plus(self):
        self.assertEqual(_parse_num("+12"), 12.0)

    def test_spasi_di_pinggir_dan_tengah_diabaikan(self):
        self.assertEqual(_parse_num("  1.500  "), 1500.0)

    def test_num_dan_parse_num_round_trip_untuk_ribuan(self):
        # angka yang diformat _num() harus bisa dibaca balik oleh _parse_num()
        # -- keduanya dipakai bersama di comparison_table untuk mewarnai sel
        for v in (12500, 1234567, -1234, 0):
            self.assertEqual(_parse_num(_num(v)), float(v))


if __name__ == "__main__":
    unittest.main()
