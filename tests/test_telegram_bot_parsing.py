"""Test untuk telegram_bot.parse_topic_command — parsing perintah "mulai topik"."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# telegram_bot.py membaca env var ini di level modul (dan butuh paket
# python-telegram-bot/python-dotenv terpasang) sebelum bisa di-import.
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "12345")

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


if __name__ == "__main__":
    unittest.main()
