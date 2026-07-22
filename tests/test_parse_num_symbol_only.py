"""Regresi: _parse_num() di core/chart_templates.py crash IndexError kalau sel
tabel cuma berisi simbol mata uang/persen tanpa angka (mis. "Rp", "%", "rp",
"$" sebagai placeholder data belum tersedia).

Alur bug: setelah simbol "Rp"/"rp"/"$"/"%"/spasi dibuang, t jadi string kosong.
Baris berikutnya `if t[:1] in "+-":` memeriksa keanggotaan SUBSTRING, dan
string kosong selalu dianggap "in" string apa pun — jadi cabang itu tetap
masuk lalu mengakses t[0] pada string kosong -> IndexError.

Ini bukan sekadar teoretis: comparison_table() (dipanggil tiap render chart
tipe "table" di pipeline video) memanggil _parse_num(cell) untuk SETIAP sel
non-kolom-pertama guna menentukan warna angka. render_chart() menjanjikan di
docstring-nya "Aman dipanggil pipeline — tidak melempar exception" dan hanya
menangkap (KeyError, ValueError, TypeError) -- IndexError lolos dan bikin
seluruh render video crash di tengah jalan.

Jalankan: python -m pytest tests/test_parse_num_symbol_only.py -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from chart_templates import _parse_num  # noqa: E402


class ParseNumSymbolOnlyTest(unittest.TestCase):
    def test_rupiah_saja_tanpa_angka_tidak_crash(self):
        self.assertIsNone(_parse_num("Rp"))

    def test_rupiah_lowercase_saja_tidak_crash(self):
        self.assertIsNone(_parse_num("rp"))

    def test_persen_saja_tidak_crash(self):
        self.assertIsNone(_parse_num("%"))

    def test_dolar_saja_tidak_crash(self):
        self.assertIsNone(_parse_num("$"))

    def test_kombinasi_simbol_tanpa_angka_tidak_crash(self):
        self.assertIsNone(_parse_num("Rp%"))

    def test_minus_saja_tetap_none_bukan_crash(self):
        # kasus ini sudah lolos sebelum fix (t jadi "" tapi lewat cabang
        # +/- dulu) -- dipertahankan di sini biar regresi ke arah lain
        # (mis. jadi 0.0 alih-alih None) ikut ketahuan.
        self.assertIsNone(_parse_num("-"))

    def test_plus_saja_tetap_none(self):
        self.assertIsNone(_parse_num("+"))

    def test_rupiah_dengan_angka_tetap_benar(self):
        # perilaku untuk input valid tidak boleh berubah oleh fix ini
        self.assertEqual(_parse_num("Rp 1.234"), 1234.0)
        self.assertEqual(_parse_num("-Rp1.234"), -1234.0)
        self.assertEqual(_parse_num("45%"), 45.0)


if __name__ == "__main__":
    unittest.main()
