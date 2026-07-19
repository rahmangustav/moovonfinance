"""Test untuk shorts._pick_window — jendela hook-first mode pakai-ulang."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shorts import _pick_window, MAX_CUT


class TestPickWindowCutOverride(unittest.TestCase):
    def test_cut_di_bawah_batas_dipakai_apa_adanya(self):
        start, end = _pick_window([], start_override=10, cut_override=30)
        self.assertEqual(start, 10.0)
        self.assertEqual(end, 40.0)

    def test_cut_persis_di_batas(self):
        start, end = _pick_window([], start_override=5, cut_override=MAX_CUT)
        self.assertEqual(end - start, MAX_CUT)

    def test_cut_melebihi_batas_dipotong_ke_max_cut_bukan_dijadikan_posisi_absolut(self):
        # Sebelum perbaikan: cut_override > MAX_CUT membuat `end` dibaca sebagai
        # posisi absolut (bukan durasi relatif ke start), sehingga akhir jendela
        # jadi jauh lebih pendek dari yang diminta.
        start, end = _pick_window([], start_override=9, cut_override=60)
        self.assertEqual(start, 9.0)
        self.assertEqual(end, 9.0 + MAX_CUT)

    def test_cut_melebihi_batas_dengan_start_besar_tidak_menghasilkan_jendela_terbalik(self):
        # Regresi utama: start=100, cut=57 (57 > MAX_CUT=56) dulu menghasilkan
        # end=57 (< start!) — jendela negatif yang akan bikin
        # AudioFileClip.subclipped(a0, a1) gagal atau merusak output.
        start, end = _pick_window([], start_override=100, cut_override=57)
        self.assertEqual(start, 100.0)
        self.assertGreater(end, start)
        self.assertEqual(end, start + MAX_CUT)

    def test_durasi_akhir_tidak_pernah_melebihi_max_cut(self):
        for start, cut in [(0, 56), (0, 57), (9, 60), (100, 57), (200, 1000)]:
            with self.subTest(start=start, cut=cut):
                s, e = _pick_window([], start_override=start, cut_override=cut)
                self.assertLessEqual(e - s, MAX_CUT)
                self.assertGreaterEqual(e, s)


class TestPickWindowStartOverride(unittest.TestCase):
    def test_start_override_negatif_dijepit_ke_nol(self):
        start, _ = _pick_window([], start_override=-5, cut_override=10)
        self.assertEqual(start, 0.0)


class TestPickWindowAutoDeteksiHook(unittest.TestCase):
    def test_tanpa_override_pakai_kalimat_tanya_pertama_setelah_detik_6(self):
        cues = [
            (0.0, 6.0, "Halo semua, ini disclaimer edukasi dulu ya."),
            (6.0, 9.5, "Kenapa bank ini masih murah?"),
            (9.5, 13.0, "Mari kita bahas."),
        ]
        start, end = _pick_window(cues)
        self.assertAlmostEqual(start, 6.0 - 0.35, places=3)
        self.assertGreater(end, start)

    def test_tanpa_kalimat_tanya_mulai_dari_nol(self):
        cues = [(0.0, 5.0, "Statement biasa."), (5.0, 10.0, "Statement lain.")]
        start, end = _pick_window(cues)
        self.assertEqual(start, 0.0)


if __name__ == "__main__":
    unittest.main()
