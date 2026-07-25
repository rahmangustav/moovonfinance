"""Test untuk telegram_bot.parse_topic_command — parsing perintah "mulai topik"."""
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# telegram_bot.py membaca env var ini di level modul (dan butuh paket
# python-telegram-bot/python-dotenv terpasang) sebelum bisa di-import.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "12345")

import telegram_bot
from telegram_bot import parse_topic_command


class TestParseTopicCommand(unittest.TestCase):
    def test_format_titik_dua_tanpa_spasi(self):
        self.assertEqual(parse_topic_command("mulai topik:BBRI Q2"), "BBRI Q2")

    def test_format_titik_dua_dengan_spasi(self):
        self.assertEqual(parse_topic_command("mulai topik: BBRI Q2"), "BBRI Q2")

    def test_format_spasi_tanpa_titik_dua(self):
        self.assertEqual(parse_topic_command("mulai topik BBRI Q2"), "BBRI Q2")

    def test_case_insensitive_pada_prefix(self):
        self.assertEqual(parse_topic_command("MULAI TOPIK: BBCA"), "BBCA")

    def test_topik_mengandung_titik_dua_format_spasi_tidak_terpotong(self):
        # Bug asli: format "mulai topik <nama>" (tanpa ':' tepat setelah
        # "topik") tapi nama topiknya sendiri mengandung ':' di tengah kalimat
        # membuat parser lama salah split di ':' itu dan membuang bagian
        # sebelumnya ("BCA") dari topik yang tersimpan.
        self.assertEqual(
            parse_topic_command("mulai topik BCA: earning season"),
            "BCA: earning season",
        )

    def test_topik_mengandung_titik_dua_format_titik_dua(self):
        self.assertEqual(
            parse_topic_command("mulai topik: BCA: earning season"),
            "BCA: earning season",
        )

    def test_tanpa_nama_topik_menghasilkan_string_kosong(self):
        self.assertEqual(parse_topic_command("mulai topik:"), "")
        self.assertEqual(parse_topic_command("mulai topik "), "")

    def test_bukan_perintah_topik_menghasilkan_none(self):
        self.assertIsNone(parse_topic_command("data aman, lanjut render"))
        self.assertIsNone(parse_topic_command("halo"))
        self.assertIsNone(parse_topic_command(""))


class TestNewTopicEntry(unittest.TestCase):
    def test_requested_at_pakai_wib_bukan_jam_lokal_server(self):
        # 2026-07-25 16:00 UTC == 2026-07-25 23:00 WIB (GMT+7). Kalau bot
        # jalan di server UTC dan bug lama (datetime.now() naive) masih ada,
        # requested_at akan tercatat "16:00", bukan "23:00".
        fixed_utc = datetime(2026, 7, 25, 16, 0, tzinfo=timezone.utc)
        with mock.patch("telegram_bot.datetime") as mock_dt:
            mock_dt.now.side_effect = lambda tz=None: (
                fixed_utc.astimezone(tz) if tz is not None else fixed_utc
            )
            entry = telegram_bot._new_topic_entry("BBRI Q2")
        self.assertEqual(entry, {"topic": "BBRI Q2", "requested_at": "2026-07-25 23:00"})


if __name__ == "__main__":
    unittest.main()
