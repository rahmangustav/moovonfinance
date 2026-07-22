"""Test core/moovon_style.py — sistem desain matplotlib untuk chart video.

Modul ini dipakai core/chart_templates.py (apply_style, add_title, add_branding,
COLORS, _slugify) untuk SETIAP chart yang tampil di video panjang, tapi belum
pernah punya test sama sekali. Jalankan: python -m pytest tests/test_moovon_style.py
"""
import sys
import unittest
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from core import moovon_style as ms


class RupiahTest(unittest.TestCase):
    def test_ribuan_pakai_titik(self):
        self.assertEqual(ms.rupiah(1250000), "Rp1.250.000")

    def test_nol_desimal_default(self):
        self.assertEqual(ms.rupiah(1234.9), "Rp1.235")

    def test_decimals_pakai_koma(self):
        self.assertEqual(ms.rupiah(1234.5, decimals=2), "Rp1.234,50")

    def test_nol(self):
        self.assertEqual(ms.rupiah(0), "Rp0")

    def test_negatif_tanda_minus_tetap_ada(self):
        # 'Rp' selalu di depan, tanda minus ikut angka di belakangnya
        self.assertEqual(ms.rupiah(-1250000), "Rp-1.250.000")


class DollarTest(unittest.TestCase):
    def test_ribuan_pakai_koma(self):
        self.assertEqual(ms.dollar(1250000), "$1,250,000")

    def test_decimals(self):
        self.assertEqual(ms.dollar(1234.5, decimals=2), "$1,234.50")

    def test_negatif(self):
        self.assertEqual(ms.dollar(-500), "$-500")


class CurrencyAxisTest(unittest.TestCase):
    def setUp(self):
        self.fig, self.ax = plt.subplots()

    def tearDown(self):
        plt.close(self.fig)

    def test_default_rp_pasang_di_sumbu_y(self):
        ms.currency_axis(self.ax)
        formatter = self.ax.yaxis.get_major_formatter()
        self.assertEqual(formatter(1250000, 0), "Rp1.250.000")

    def test_usd_pasang_di_sumbu_x(self):
        ms.currency_axis(self.ax, currency="usd", axis="x")
        formatter = self.ax.xaxis.get_major_formatter()
        self.assertEqual(formatter(1250000, 0), "$1,250,000")

    def test_idr_alias_juga_dianggap_rupiah(self):
        ms.currency_axis(self.ax, currency="IDR")
        formatter = self.ax.yaxis.get_major_formatter()
        self.assertEqual(formatter(500, 0), "Rp500")


class SlugifyTest(unittest.TestCase):
    def test_spasi_jadi_strip(self):
        self.assertEqual(ms._slugify("Laba Bersih 2025"), "laba-bersih-2025")

    def test_karakter_spesial_dibuang(self):
        self.assertEqual(ms._slugify("PER & PBV: BBRI!"), "per-pbv-bbri")

    def test_underscore_jadi_strip(self):
        self.assertEqual(ms._slugify("laba_bersih_q1"), "laba-bersih-q1")

    def test_string_kosong_fallback_grafik(self):
        self.assertEqual(ms._slugify(""), "grafik")

    def test_hanya_karakter_spesial_fallback_grafik(self):
        self.assertEqual(ms._slugify("!!!"), "grafik")


class AddTitleTest(unittest.TestCase):
    def setUp(self):
        self.fig = plt.figure()

    def tearDown(self):
        plt.close(self.fig)

    def test_judul_ditempel_ke_figure(self):
        ms.add_title(self.fig, "Judul Chart")
        texts = [t.get_text() for t in self.fig.texts]
        self.assertIn("Judul Chart", texts)

    def test_tanpa_subtitle_hanya_satu_text(self):
        ms.add_title(self.fig, "Judul Saja")
        self.assertEqual(len(self.fig.texts), 1)

    def test_dengan_subtitle_dua_text(self):
        ms.add_title(self.fig, "Judul", subtitle="Subjudul")
        texts = [t.get_text() for t in self.fig.texts]
        self.assertIn("Judul", texts)
        self.assertIn("Subjudul", texts)


class AddBrandingTest(unittest.TestCase):
    def setUp(self):
        self.fig = plt.figure()

    def tearDown(self):
        plt.close(self.fig)

    def test_tanpa_source_hanya_watermark_brand(self):
        ms.add_branding(self.fig)
        texts = [t.get_text() for t in self.fig.texts]
        self.assertEqual(texts, ["Moovon Finance"])

    def test_dengan_source_tambah_baris_sumber(self):
        ms.add_branding(self.fig, source="BEI")
        texts = [t.get_text() for t in self.fig.texts]
        self.assertIn("Moovon Finance", texts)
        self.assertIn("Sumber: BEI", texts)

    def test_corner_kanan_default(self):
        ms.add_branding(self.fig)
        self.assertEqual(self.fig.texts[0].get_ha(), "right")

    def test_corner_kiri(self):
        ms.add_branding(self.fig, corner="left")
        self.assertEqual(self.fig.texts[0].get_ha(), "left")


class LabelBarsTest(unittest.TestCase):
    def setUp(self):
        self.fig, self.ax = plt.subplots()

    def tearDown(self):
        plt.close(self.fig)

    def test_satu_anotasi_per_bar(self):
        bars = self.ax.bar(["A", "B", "C"], [10, 20, 30])
        ms.label_bars(self.ax, bars)
        self.assertEqual(len(self.ax.texts), 3)

    def test_format_custom_dipakai(self):
        bars = self.ax.bar(["A"], [1250000])
        ms.label_bars(self.ax, bars, fmt=ms.rupiah)
        self.assertEqual(self.ax.texts[0].get_text(), "Rp1.250.000")


class ApplyStyleTest(unittest.TestCase):
    def tearDown(self):
        matplotlib.rcdefaults()

    def test_warna_latar_sesuai_palet(self):
        ms.apply_style()
        self.assertEqual(matplotlib.rcParams["figure.facecolor"], ms.COLORS["background"])
        self.assertEqual(matplotlib.rcParams["axes.facecolor"], ms.COLORS["background"])

    def test_ukuran_figure_1920x1080_pada_300dpi(self):
        ms.apply_style()
        w, h = matplotlib.rcParams["figure.figsize"]
        dpi = matplotlib.rcParams["figure.dpi"]
        self.assertAlmostEqual(w * dpi, 1920, delta=1)
        self.assertAlmostEqual(h * dpi, 1080, delta=1)

    def test_spine_atas_kanan_dimatikan(self):
        ms.apply_style()
        self.assertFalse(matplotlib.rcParams["axes.spines.top"])
        self.assertFalse(matplotlib.rcParams["axes.spines.right"])


class SaveFigureTest(unittest.TestCase):
    def setUp(self):
        self.fig = plt.figure()
        self._orig_output_dir = ms.OUTPUT_DIR

    def tearDown(self):
        plt.close(self.fig)
        ms.OUTPUT_DIR = self._orig_output_dir

    def test_file_tersimpan_dengan_nama_bertanggal(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ms.OUTPUT_DIR = Path(tmp)
            path = ms.save_figure(self.fig, "Laba Bersih 2025")
            self.assertTrue(path.exists())
            self.assertTrue(path.name.endswith("_laba-bersih-2025.png"))
            date_part = path.name.split("_", 1)[0]
            self.assertEqual(len(date_part), 10)  # YYYY-MM-DD


if __name__ == "__main__":
    unittest.main()
