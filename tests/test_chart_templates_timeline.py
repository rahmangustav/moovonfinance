"""Regresi: timeline_chart() diam-diam membuang event kalau 'events' dan
'dates' beda panjang, alih-alih gagal jelas.

Bug nyata: `xs` (posisi x tiap titik) dihitung dari `len(events)`, lalu
titik yang benar-benar digambar diambil lewat `zip(events, dates, xs)` --
zip berhenti di list TERPENDEK. Kalau draft riset salah ketik (mis. 5
peristiwa tapi cuma 4 tanggal, atau sebaliknya), event-event terakhir
dibuang TANPA peringatan apa pun, dan sisa event yang tergambar numpuk di
sisi kiri garis waktu (posisi x-nya dihitung untuk n=5 titik, padahal cuma
3-4 yang benar-benar dipakai) -- chart tayang di video dengan timeline yang
terlihat rusak/tidak lengkap, bukan cuma "kurang data".

`comparison_table()` sudah punya jaring pengaman sejenis untuk baris yang
jumlah kolomnya tak cocok dengan header (lihat test_render_chart_no_throw.py)
-- timeline_chart() belum, sampai perbaikan ini.

Jalankan: python -m pytest tests/test_chart_templates_timeline.py -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

try:
    from chart_templates import render_chart, timeline_chart
    MATPLOTLIB_AVAILABLE = True
except ModuleNotFoundError:
    MATPLOTLIB_AVAILABLE = False


@unittest.skipUnless(MATPLOTLIB_AVAILABLE, "matplotlib tidak terpasang di sandbox ini")
class TimelineChartMismatchTest(unittest.TestCase):
    def test_events_lebih_banyak_dari_dates_raise_value_error_jelas(self):
        with self.assertRaises(ValueError) as ctx:
            timeline_chart(
                events=["A", "B", "C", "D", "E"], dates=["2020", "2021", "2022"],
                judul="Test", sumber="", nama_file="test-timeline-mismatch-1",
            )
        msg = str(ctx.exception)
        self.assertIn("5", msg)
        self.assertIn("3", msg)

    def test_dates_lebih_banyak_dari_events_raise_value_error_jelas(self):
        with self.assertRaises(ValueError) as ctx:
            timeline_chart(
                events=["A", "B"], dates=["2020", "2021", "2022"],
                judul="Test", sumber="", nama_file="test-timeline-mismatch-2",
            )
        self.assertIn("2", str(ctx.exception))
        self.assertIn("3", str(ctx.exception))

    def test_jumlah_sama_tetap_lolos_seperti_sebelumnya(self):
        # Regresi negatif: guard baru tidak boleh menolak input yang sudah benar.
        path = timeline_chart(
            events=["A", "B", "C"], dates=["2020", "2021", "2022"],
            judul="Test", sumber="", nama_file="test-timeline-ok",
        )
        self.assertTrue(Path(path).exists())
        Path(path).unlink()

    def test_render_chart_timeline_mismatch_tidak_melempar_exception(self):
        # render_chart() menjanjikan "aman dipanggil pipeline -- tidak
        # melempar exception apa pun" -- ValueError baru ini pun harus
        # tertangkap di sana, sama seperti tipe chart lain.
        spec = {
            "type": "timeline", "judul": "Test",
            "events": ["A", "B", "C"], "dates": ["2020", "2021"],
            "nama_file": "test-timeline-render-chart-mismatch",
        }
        result = render_chart(spec)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
