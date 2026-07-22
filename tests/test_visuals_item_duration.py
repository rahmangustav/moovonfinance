"""Test _item_duration() di core/visuals.py — durasi per slide item.

Bug nyata yang ditangkap: create_video() dulu memakai
`per_item = max(4.0, remaining / n_items)` — memaksa minimum 4 detik per
item walau itu bikin total durasi visual (per_item * n_items) MELEBIHI sisa
durasi audio. Video hasil concatenate_videoclips lalu dipotong balik ke
total_duration lewat `.subclipped(0, total_duration)`, yang memotong dari
EKOR — kalau overflow-nya cukup besar, itu memangkas atau menghapus total
slide penutup (CTA + DISCLAIMER, wajib per CLAUDE.md) tanpa peringatan apa
pun. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.visuals import _item_duration, ITEM_MIN_DUR


class ItemDurationTest(unittest.TestCase):
    def test_banyak_waktu_per_item_di_atas_minimum(self):
        # 10 item, 60 detik sisa -> 6 detik/item, di atas ideal 4 detik.
        self.assertAlmostEqual(_item_duration(60.0, 10), 6.0)

    def test_total_durasi_tidak_pernah_melebihi_sisa_waktu(self):
        # Regresi utama: dulu max(4.0, ...) bisa membuat total > remaining.
        for remaining, n in [(34.0, 10), (10.0, 5), (3.0, 1), (100.0, 50)]:
            with self.subTest(remaining=remaining, n=n):
                per_item = _item_duration(remaining, n)
                self.assertLessEqual(per_item * n, remaining + 1e-9)

    def test_item_dikompres_di_bawah_ideal_saat_terlalu_padat(self):
        # 10 item, 34 detik sisa -> 3.4 detik/item, di bawah ideal 4 detik —
        # sebelumnya ini dipaksa jadi 4.0 (overflow 6 detik, cukup untuk
        # menghapus habis satu slide penutup 4 detik).
        per_item = _item_duration(34.0, 10)
        self.assertAlmostEqual(per_item, 3.4)
        self.assertLess(per_item, ITEM_MIN_DUR)

    def test_nol_item_tidak_pembagian_nol(self):
        self.assertEqual(_item_duration(50.0, 0), 50.0)


if __name__ == "__main__":
    unittest.main()
