"""Test untuk shorts.parse_short_script — parsing skrip Short mandiri +
auto-deteksi ticker (tanpa field TICKER eksplisit)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shorts import parse_short_script


class TestParseShortScriptTickerEksplisit(unittest.TestCase):
    def test_ticker_eksplisit_dipakai_apa_adanya(self):
        info = parse_short_script(
            "TICKER: bbri\nHOOK: Laba anjlok.\nBODY: Tapi asing memborong."
        )
        self.assertEqual(info["ticker"], "BBRI")


class TestParseShortScriptAutoDeteksiTicker(unittest.TestCase):
    def test_akronim_generik_sebelum_ticker_asli_tidak_ikut_terpilih(self):
        # Sebelum perbaikan: regex ambil kecocokan 4-huruf kapital PERTAMA di
        # teks, jadi "BUMN" (istilah umum channel ini, lihat CLAUDE.md) salah
        # kepilih jadi ticker, padahal ticker asli "BBRI" muncul setelahnya.
        info = parse_short_script(
            "HOOK: Laba BUMN raksasa ini anjlok 21 persen.\n"
            "BODY: Tapi asing malah memborong saham BBRI dalam sepekan terakhir."
        )
        self.assertEqual(info["ticker"], "BBRI")

    def test_ihsg_disebut_sebelum_ticker_asli_tidak_ikut_terpilih(self):
        info = parse_short_script(
            "HOOK: IHSG hari ini merah.\n"
            "BODY: Tapi TLKM justru naik lawan arus."
        )
        self.assertEqual(info["ticker"], "TLKM")

    def test_hanya_akronim_generik_tanpa_ticker_asli_jatuh_ke_strip(self):
        info = parse_short_script(
            "HOOK: BUMN kompak menguat pekan ini.\n"
            "BODY: IHSG dan APBN juga jadi sorotan analis."
        )
        self.assertEqual(info["ticker"], "-")

    def test_tanpa_kecocokan_4_huruf_kapital_jatuh_ke_strip(self):
        info = parse_short_script(
            "HOOK: Harga saham ini turun terus.\nBODY: Kenapa masih ditahan investor?"
        )
        self.assertEqual(info["ticker"], "-")

    def test_ticker_asli_tunggal_tetap_terdeteksi(self):
        info = parse_short_script(
            "HOOK: BBCA balik ke level tertinggi.\nBODY: Ini alasannya."
        )
        self.assertEqual(info["ticker"], "BBCA")


if __name__ == "__main__":
    unittest.main()
