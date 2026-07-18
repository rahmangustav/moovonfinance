"""Test slot upload otomatis (17:30 WIB Sel/Rab/Kam) di produce.py.

Logika ini menentukan kapan video benar-benar tayang publik (--at next),
tapi belum pernah punya test. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import produce
from produce import _next_upload_slot, _parse_slot, _to_publish_at, WIB


def _fake_now(fixed_dt):
    """Ganti produce.datetime dengan subclass yang now() mengembalikan fixed_dt,
    tapi strptime/replace dkk tetap perilaku datetime asli."""
    class FakeDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_dt if tz is None else fixed_dt.astimezone(tz)

    return mock.patch.object(produce, "datetime", FakeDateTime)


class NextUploadSlotTest(unittest.TestCase):
    def test_senin_lompat_ke_selasa(self):
        # Senin (weekday 0) bukan hari yang diizinkan -> slot berikutnya Selasa
        now = datetime(2026, 7, 6, 10, 0, tzinfo=WIB)  # Senin
        with _fake_now(now):
            slot = _next_upload_slot()
        self.assertEqual(slot.weekday(), 1)  # Selasa
        self.assertEqual((slot.hour, slot.minute), (17, 30))
        self.assertEqual(slot.date(), now.date() + timedelta(days=1))

    def test_kurang_15_menit_dari_slot_hari_ini_dilewati(self):
        # Selasa 17:15 -> slot Selasa 17:30 cuma 15 menit lagi (bukan > 15 menit),
        # jadi harus dilewati ke slot Rabu berikutnya
        now = datetime(2026, 7, 7, 17, 15, tzinfo=WIB)  # Selasa
        with _fake_now(now):
            slot = _next_upload_slot()
        self.assertEqual(slot.weekday(), 2)  # Rabu
        self.assertEqual(slot.date(), now.date() + timedelta(days=1))

    def test_lebih_dari_15_menit_dari_slot_hari_ini_dipakai(self):
        # Selasa 17:00 -> slot Selasa 17:30 masih 30 menit lagi -> dipakai hari ini
        now = datetime(2026, 7, 7, 17, 0, tzinfo=WIB)  # Selasa
        with _fake_now(now):
            slot = _next_upload_slot()
        self.assertEqual(slot.date(), now.date())
        self.assertEqual((slot.hour, slot.minute), (17, 30))

    def test_setelah_kamis_lompat_ke_selasa_pekan_depan(self):
        # Kamis malam, sesudah slot terakhir minggu ini -> harus lompati
        # Jumat/Sabtu/Minggu/Senin dan mendarat di Selasa pekan berikutnya
        now = datetime(2026, 7, 9, 20, 0, tzinfo=WIB)  # Kamis malam
        with _fake_now(now):
            slot = _next_upload_slot()
        self.assertEqual(slot.weekday(), 1)  # Selasa
        self.assertGreater(slot, now)
        self.assertEqual(slot.date(), now.date() + timedelta(days=5))


class ParseSlotTest(unittest.TestCase):
    def test_next_delegasi_ke_next_upload_slot(self):
        now = datetime(2026, 7, 6, 10, 0, tzinfo=WIB)
        with _fake_now(now):
            slot = _parse_slot("next")
        self.assertEqual(slot.weekday(), 1)

    def test_tanggal_spesifik_dianggap_wib(self):
        slot = _parse_slot("2026-07-07 17:30")
        self.assertEqual(slot, datetime(2026, 7, 7, 17, 30, tzinfo=WIB))

    def test_whitespace_dan_case_next_dimaafkan(self):
        now = datetime(2026, 7, 6, 10, 0, tzinfo=WIB)
        with _fake_now(now):
            slot = _parse_slot("  NEXT  ")
        self.assertEqual(slot.weekday(), 1)


class ToPublishAtTest(unittest.TestCase):
    def test_konversi_wib_ke_utc(self):
        # WIB = UTC+7, jadi 17:30 WIB -> 10:30 UTC
        dt_wib = datetime(2026, 7, 7, 17, 30, tzinfo=WIB)
        self.assertEqual(_to_publish_at(dt_wib), "2026-07-07T10:30:00Z")

    def test_lewat_tengah_malam_utc(self):
        # 02:00 WIB -> hari sebelumnya 19:00 UTC
        dt_wib = datetime(2026, 7, 7, 2, 0, tzinfo=WIB)
        self.assertEqual(_to_publish_at(dt_wib), "2026-07-06T19:00:00Z")


if __name__ == "__main__":
    unittest.main()
