"""Regresi: render_chart() menjanjikan di docstring-nya "Aman dipanggil
pipeline -- tidak melempar exception", tapi sebelum perbaikan hanya
menangkap (KeyError, ValueError, TypeError) di sekitar pemanggilan fungsi
render per-tipe. Dua sumber IndexError nyata lolos dari situ:

1. line_chart(): kalau salah satu series di y_dict list-nya KOSONG (draft
   riset belum lengkap/typo), `ax.annotate(_num(vals[-1]), ...)` langsung
   IndexError -- lolos dari except-clause render_chart().
2. comparison_table(): kalau satu baris di `rows` py sel lebih/kurang dari
   `headers` (kolom nyasar, salah ketik draft), `_cell_x()` mengakses
   `edges[col + 1]` di luar batas -> IndexError -- juga lolos.

create_video() (core/visuals.py) memanggil render_chart() tanpa try/except
sendiri, jadi exception yang lolos di sini mematikan seluruh proses render
video -- SETELAH TTS selesai (mahal untuk diulang).

Perbaikan: (a) render_chart() sekarang juga menangkap IndexError sebagai
jaring pengaman terakhir, dan (b) line_chart()/comparison_table() melempar
ValueError dengan pesan jelas lebih awal untuk kedua kasus di atas, supaya
kegagalannya informatif -- bukan cuma kebetulan tertangkap oleh except umum.

Jalankan: python -m pytest tests/test_render_chart_no_throw.py -v
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

try:
    from chart_templates import render_chart, line_chart, comparison_table
    MATPLOTLIB_AVAILABLE = True
except ModuleNotFoundError:
    MATPLOTLIB_AVAILABLE = False


@unittest.skipUnless(MATPLOTLIB_AVAILABLE, "matplotlib tidak terpasang di sandbox ini")
class RenderChartNoThrowTest(unittest.TestCase):
    def test_line_chart_series_kosong_raise_value_error_jelas(self):
        with self.assertRaises(ValueError) as ctx:
            line_chart(
                x=["2024"], y_dict={"BBCA": []},
                judul="Test", sumber="", nama_file="test-kosong",
            )
        self.assertIn("kosong", str(ctx.exception))

    def test_comparison_table_kolom_tak_cocok_raise_value_error_jelas(self):
        with self.assertRaises(ValueError) as ctx:
            comparison_table(
                headers=["Emiten", "Harga", "PER"],
                rows=[["BBCA", "Rp10.250", "24,1", "+18,5%"]],  # 4 sel, 3 header
                judul="Test", sumber="", nama_file="test-mismatch",
            )
        self.assertIn("kolom", str(ctx.exception))

    def test_render_chart_line_series_kosong_tidak_melempar_exception(self):
        spec = {
            "type": "line", "judul": "Test",
            "x": ["2024"], "y_dict": {"BBCA": []},
            "nama_file": "test-line-kosong",
        }
        result = render_chart(spec)  # tidak boleh raise apa pun
        self.assertIsNone(result)

    def test_render_chart_table_kolom_tak_cocok_tidak_melempar_exception(self):
        spec = {
            "type": "table", "judul": "Test",
            "headers": ["Emiten", "Harga", "PER"],
            "rows": [["BBCA", "Rp10.250", "24,1", "+18,5%"]],
            "nama_file": "test-table-mismatch",
        }
        result = render_chart(spec)  # tidak boleh raise apa pun
        self.assertIsNone(result)

    def test_render_chart_menangkap_index_error_generik(self):
        # Simulasi kelas bug ini secara umum: fungsi dispatch mana pun yang
        # melempar IndexError harus tetap ditangkap render_chart(), bukan
        # cuma dua kasus spesifik di atas.
        with mock.patch.dict(
            "chart_templates._DISPATCH",
            {"line": lambda s: (_ for _ in ()).throw(IndexError("boom"))},
        ):
            result = render_chart({"type": "line", "judul": "Test", "nama_file": "x"})
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
