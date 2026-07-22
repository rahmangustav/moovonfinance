"""Regresi: shorts.py harus membuang `short_bg.mp4` (video mentah tanpa
subtitle/progress bar) setelah dibakar jadi `short.mp4` — sama seperti
core/visuals.create_video() membuang `_bg.mp4`-nya sendiri. Sebelum
perbaikan, `short_bg.mp4` (duplikat penuh dari video final, tanpa manfaat
lanjutan — tak pernah dibaca ulang oleh shorts.py maupun produce.py) tertinggal
selamanya di tiap run_dir. Shorts adalah "top-of-funnel utama" (CLAUDE.md)
sehingga file ini menumpuk terus tiap kali diproduksi.

Test ini benar-benar menjalankan pipeline video (moviepy + ffmpeg) dengan
audio bisu pendek supaya cepat, bukan sekadar memeriksa logika string —
tepat menyasar bagian assembly yang tidak tersentuh oleh unit test parsing.
"""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import imageio_ffmpeg

from shorts import make_short


def _silent_audio(path: Path, seconds: float = 3.0):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", str(seconds), "-q:a", "9", str(path)],
        capture_output=True, check=True,
    )


class TestShortBgCleanup(unittest.TestCase):
    def test_short_bg_mp4_dibuang_setelah_burn(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            rd = Path(tmp)
            audio_p = rd / "audio.mp3"
            _silent_audio(audio_p, 3.0)
            (rd / "audio.srt").write_text(
                "1\n00:00:00,000 --> 00:00:03,000\nTes subtitle singkat.\n",
                encoding="utf-8",
            )

            out = make_short(str(rd), start=0, cut=3)

            self.assertIsNotNone(out)
            self.assertTrue(Path(out).exists(), "short.mp4 final harus ada")
            self.assertFalse(
                (rd / "short_bg.mp4").exists(),
                "short_bg.mp4 (duplikat mentah) semestinya dibuang setelah burn, "
                "sama seperti create_video() membuang _bg.mp4-nya",
            )


if __name__ == "__main__":
    unittest.main()
