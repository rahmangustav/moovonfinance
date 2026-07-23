"""Test untuk shorts._fmt — format timestamp SRT 'HH:MM:SS,mmm'.

Bug nyata yang ditangkap di sini: implementasi lama memakai `f"{s:06.3f}"`
(pembulatan) pada detik pecahan, jadi nilai mepet ke atas seperti 59,9999
detik dibulatkan jadi "60,000" -- field detik SRT semestinya 00-59, jadi
timestamp seperti "00:00:60,000" atau "00:01:60,000" TIDAK VALID dan bisa
membuat ffmpeg gagal/salah menafsirkan subtitle saat di-burn ke video Short
(mode pakai-ulang, lihat shorts._write_sub_srt). Perbaikan memotong (bukan
membulatkan) ke milidetik, sama seperti core/subtitle._ts.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shorts import _fmt, _ts


class FmtTimestampTest(unittest.TestCase):
    def test_nol_detik(self):
        self.assertEqual(_fmt(0.0), "00:00:00,000")

    def test_pecahan_detik_biasa(self):
        self.assertEqual(_fmt(1.5), "00:00:01,500")

    def test_lewat_satu_menit(self):
        self.assertEqual(_fmt(61.25), "00:01:01,250")

    def test_lewat_satu_jam(self):
        self.assertEqual(_fmt(3661.5), "01:01:01,500")

    def test_detik_mepet_60_tidak_membulat_ke_atas(self):
        # Regresi utama: sebelum perbaikan, 59.9999 -> "00:00:60,000" (field
        # detik SRT harus 00-59, "60" tidak valid).
        out = _fmt(59.9999)
        self.assertEqual(out, "00:00:59,999")
        self.assertNotIn("60,000", out)

    def test_menit_mepet_60_ikut_tidak_membulat_ke_atas(self):
        # 119.9996 dulu menghasilkan "00:01:60,000" (menit tak ikut naik jadi
        # 2 karena `m` dihitung sebelum `s` dibulatkan).
        out = _fmt(119.9996)
        self.assertEqual(out, "00:01:59,999")

    def test_jam_mepet_60_menit_tidak_membulat_ke_atas(self):
        out = _fmt(3599.9997)
        self.assertEqual(out, "00:59:59,999")

    def test_roundtrip_dengan_ts_parser(self):
        # _ts (parser) & _fmt (formatter) dipakai berpasangan di
        # shorts._parse_srt / shorts._write_sub_srt -- pastikan nilai wajar
        # bisa bolak-balik tanpa drift signifikan.
        for sec in (0.0, 1.5, 61.25, 3661.5, 45.123):
            self.assertAlmostEqual(_ts(_fmt(sec).replace(",", ".")), sec, places=3)


if __name__ == "__main__":
    unittest.main()
