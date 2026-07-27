"""Test parsing flag CLI (--hook/--cut/--start/--ticker/--eyebrow/--privacy/--at)
di produce.py dan shorts.py.

Sebelumnya semua flag ini diambil lewat `args[args.index(flag) + 1]` tanpa
jaga-jaga: kalau flag ditulis tapi lupa diisi nilainya (jadi argumen
terakhir), atau `--cut`/`--start` diisi teks bukan angka, program crash
dengan IndexError/ValueError mentah alih-alih pesan jelas. Jalankan:
python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import produce
import shorts


class ProduceFlagValueTest(unittest.TestCase):
    def test_flag_tak_ada_kembalikan_none(self):
        self.assertIsNone(produce._flag_value(["run_dir"], "--privacy"))

    def test_flag_dengan_nilai_diambil(self):
        self.assertEqual(
            produce._flag_value(["run_dir", "--privacy", "unlisted"], "--privacy"),
            "unlisted",
        )

    def test_flag_tanpa_nilai_keluar_dengan_pesan_jelas(self):
        with self.assertRaises(SystemExit) as cm:
            produce._flag_value(["run_dir", "--privacy"], "--privacy")
        self.assertIn("--privacy", str(cm.exception))


class ProduceFlagFloatTest(unittest.TestCase):
    def test_flag_float_tak_ada_kembalikan_none(self):
        self.assertIsNone(produce._flag_float(["run_dir"], "--cut"))

    def test_flag_float_valid_dikonversi(self):
        self.assertEqual(produce._flag_float(["run_dir", "--cut", "45"], "--cut"), 45.0)

    def test_flag_float_bukan_angka_keluar_dengan_pesan_jelas(self):
        with self.assertRaises(SystemExit) as cm:
            produce._flag_float(["run_dir", "--cut", "abc"], "--cut")
        self.assertIn("--cut", str(cm.exception))

    def test_flag_float_tanpa_nilai_keluar_dengan_pesan_jelas(self):
        with self.assertRaises(SystemExit):
            produce._flag_float(["run_dir", "--cut"], "--cut")


class ShortsFlagParsingTest(unittest.TestCase):
    def test_flag_value_tak_ada_kembalikan_none(self):
        self.assertIsNone(shorts._flag_value(["run_dir"], "--hook"))

    def test_flag_value_dengan_nilai_diambil(self):
        self.assertEqual(
            shorts._flag_value(["run_dir", "--hook", "Baris 1|Baris 2"], "--hook"),
            "Baris 1|Baris 2",
        )

    def test_flag_value_tanpa_nilai_keluar_dengan_pesan_jelas(self):
        with self.assertRaises(SystemExit) as cm:
            shorts._flag_value(["run_dir", "--hook"], "--hook")
        self.assertIn("--hook", str(cm.exception))

    def test_flag_float_valid_dikonversi(self):
        self.assertEqual(shorts._flag_float(["run_dir", "--start", "9"], "--start"), 9.0)

    def test_flag_float_bukan_angka_keluar_dengan_pesan_jelas(self):
        with self.assertRaises(SystemExit) as cm:
            shorts._flag_float(["run_dir", "--start", "sembilan"], "--start")
        self.assertIn("--start", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
