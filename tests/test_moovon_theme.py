"""Test elemen tanda tangan verdict() — aturan BELI/TAHAN/HINDARI di moovon_theme.py.

Ini logika bisnis inti (dipakai render_valuation di setiap slide valuasi),
tapi belum pernah punya test. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from moovon_theme import verdict, RGB, MOS_BELI


class VerdictTest(unittest.TestCase):
    def test_beli_saat_diskon_besar(self):
        # harga 5800 vs nilai wajar 9150 -> margin of safety ~36.6%, jauh di atas 15%
        label, color, mos = verdict(5800, 9150)
        self.assertEqual(label, "BELI")
        self.assertEqual(color, RGB["up"])
        self.assertAlmostEqual(mos, (9150 - 5800) / 9150)

    def test_tahan_saat_diskon_di_bawah_ambang(self):
        # margin of safety 12.57% < 15% -> harus TAHAN, bukan BELI
        label, color, mos = verdict(8000, 9150)
        self.assertLess(mos, MOS_BELI)
        self.assertEqual(label, "TAHAN")
        self.assertEqual(color, RGB["neutral"])

    def test_tahan_saat_harga_sama_nilai_wajar(self):
        label, color, mos = verdict(9150, 9150)
        self.assertEqual(mos, 0.0)
        self.assertEqual(label, "TAHAN")

    def test_hindari_saat_harga_di_atas_nilai_wajar(self):
        label, color, mos = verdict(10000, 9150)
        self.assertLess(mos, 0)
        self.assertEqual(label, "HINDARI")
        self.assertEqual(color, RGB["down"])

    def test_batas_tepat_15_persen_masuk_beli(self):
        # aturan CLAUDE.md: "BELI hanya bila margin of safety >= 15%" -> batas
        # inklusif, harus dites tepat di angka 0.15 (bukan cuma di atas/bawahnya)
        price, fair = 850, 1000  # mos == 0.15 persis
        label, _, mos = verdict(price, fair)
        self.assertEqual(mos, 0.15)
        self.assertEqual(label, "BELI")

    def test_nilai_wajar_nol_tidak_membagi_nol(self):
        # guard di verdict(): `if fair else 0.0` — pastikan tidak ZeroDivisionError
        label, _, mos = verdict(100, 0)
        self.assertEqual(mos, 0.0)
        self.assertEqual(label, "TAHAN")


if __name__ == "__main__":
    unittest.main()
