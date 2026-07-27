"""Test guard field wajib di dict valuation/snapshot yang diterima
create_video() (core/visuals.py). Kedua dict berasal langsung dari JSON
mentah blok `## VALUATION:` / `## SNAPSHOT:` di draft — ditulis manual,
tanpa validasi skema di jalur produksi (telegram_bot.py memanggil
`produce.py render` langsung setelah persetujuan "Data aman, lanjut
render", TANPA lewat cek_draft.py). Sebelum perbaikan ini, draft yang lupa
menulis field "harga"/"nilai_wajar" (VALUATION) atau "metrics" (SNAPSHOT)
lolos sampai render_valuation()/render_snapshot() dipanggil lewat akses
dict bracket telanjang (v["harga"], s["metrics"]) di dalam create_video(),
melempar KeyError mentah SETELAH TTS dan sebagian slide sudah dirender.
Sekarang gagal cepat dengan ValueError yang jelas, sebelum audio/slide apa
pun disentuh. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.visuals import create_video


class ValuationGuardTest(unittest.TestCase):
    def test_valuation_tanpa_harga_ditolak_cepat(self):
        with self.assertRaises(ValueError) as cm:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"nilai_wajar": 9150, "catatan": "x"},
            )
        self.assertIn("harga", str(cm.exception))

    def test_valuation_tanpa_nilai_wajar_ditolak_cepat(self):
        with self.assertRaises(ValueError) as cm:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"harga": 9800, "catatan": "x"},
            )
        self.assertIn("nilai_wajar", str(cm.exception))

    def test_valuation_lengkap_tidak_ditolak_di_guard_ini(self):
        # Field lengkap -> guard lolos, error berikutnya (kalau ada) berasal
        # dari tahap lain (mis. file audio tidak ada), bukan dari guard ini.
        try:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"harga": 9800, "nilai_wajar": 9150},
            )
        except ValueError as e:
            self.assertNotIn("blok ## VALUATION:", str(e))
        except Exception:
            pass  # gagal di tahap lain (mis. AudioFileClip) — bukan tanggung jawab guard ini


class SnapshotGuardTest(unittest.TestCase):
    def test_snapshot_tanpa_metrics_ditolak_cepat(self):
        with self.assertRaises(ValueError) as cm:
            create_video(
                "BBCA: Judul", "[HOOK]isi[SNAPSHOT]isi",
                "tidak_ada.mp3", "out/video.mp4",
                snapshot={"judul": "Kinerja"},
            )
        self.assertIn("metrics", str(cm.exception))

    def test_snapshot_lengkap_tidak_ditolak_di_guard_ini(self):
        try:
            create_video(
                "BBCA: Judul", "[HOOK]isi[SNAPSHOT]isi",
                "tidak_ada.mp3", "out/video.mp4",
                snapshot={"judul": "Kinerja", "metrics": [["Laba", "14,7 T", "up"]]},
            )
        except ValueError as e:
            self.assertNotIn("blok ## SNAPSHOT:", str(e))
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
