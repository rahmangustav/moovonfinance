"""Test untuk core.subtitle — format timestamp SRT & penulisan file."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.subtitle import _ts, to_srt


class TestTimestampFormat(unittest.TestCase):
    def test_nol_detik(self):
        self.assertEqual(_ts(0), "00:00:00,000")

    def test_pecahan_detik_dibulatkan_ke_bawah_ke_milidetik(self):
        self.assertEqual(_ts(1.5), "00:00:01,500")

    def test_lewat_satu_menit(self):
        self.assertEqual(_ts(61.25), "00:01:01,250")

    def test_lewat_satu_jam(self):
        self.assertEqual(_ts(3661.5), "01:01:01,500")

    def test_milidetik_tidak_pernah_membawa_ke_detik_berikutnya(self):
        # 0.9999 dtk -> ms harus 999, bukan dibulatkan jadi 1000/'01:00,000'
        self.assertEqual(_ts(0.9999), "00:00:00,999")


class TestToSrt(unittest.TestCase):
    def test_menulis_format_srt_standar(self):
        segments = [
            {"start": 0.0, "end": 1.5, "text": "Halo semua."},
            {"start": 1.5, "end": 3.2, "text": "Ini disclaimer edukasi."},
        ]
        path = Path("/tmp/_test_subtitle.srt")
        try:
            to_srt(segments, str(path))
            content = path.read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "1\n00:00:00,000 --> 00:00:01,500\nHalo semua.\n\n"
                "2\n00:00:01,500 --> 00:00:03,200\nIni disclaimer edukasi.\n\n",
            )
        finally:
            path.unlink(missing_ok=True)

    def test_daftar_kosong_menulis_file_kosong(self):
        path = Path("/tmp/_test_subtitle_empty.srt")
        try:
            to_srt([], str(path))
            self.assertEqual(path.read_text(encoding="utf-8"), "")
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
