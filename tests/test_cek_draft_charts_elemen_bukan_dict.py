"""Test cek_draft.py — entri 'charts' yang bukan objek JSON {...}.

Bug yang dites di sini: blok ## CHARTS: ditulis manual sebagai JSON array.
Sintaksnya bisa tetap VALID (lolos json.loads di parse_draft) walau salah
satu elemennya bukan objek — misalnya penulis draft khilaf menaruh string
atau lupa kurung kurawal untuk salah satu chart. cek_draft.py lalu langsung
memanggil `c.get("type", "?")` pada tiap elemen tanpa memvalidasi tipe dulu,
jadi begitu ada elemen non-dict, AttributeError mentah meledak di tengah
pemeriksaan — padahal cek_draft.py ada justru supaya masalah begini ketahuan
lewat laporan bersih SEBELUM render ~10 menit (TTS+encode), bukan lewat
traceback. Kalau validasi ini terlewat (langsung produce.py render), crash
yang sama terjadi lagi di core/visuals.py _match_charts_to_sections(),
setelah TTS selesai — jauh lebih mahal.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DRAFT_TEMPLATE = """# DRAFT SCRIPT — Contoh Alokasi Portofolio

## SCRIPT
### HOOK (00:00-00:15)
Kenapa alokasi portofolio ini penting untuk edukasi investasi?

### ISI UTAMA (00:15-01:00)
Ini pembahasan inti soal alokasi aset.

### PENUTUP (01:00-01:10)
Terima kasih sudah nonton, jangan lupa subscribe.
---

## CHARTS: (opsional)
```json
{charts}
```
"""


def _run_cek_draft(tmp_path, charts_json_literal):
    draft = Path(tmp_path) / "draft.md"
    draft.write_text(DRAFT_TEMPLATE.format(charts=charts_json_literal), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(ROOT / "cek_draft.py"), str(draft)],
        cwd=ROOT, capture_output=True, text=True,
    )


class ChartsElemenBukanDictTidakCrash(unittest.TestCase):
    def test_elemen_string_di_antara_chart_tidak_crash(self):
        # Elemen pertama string, bukan objek {...} -> dulu meledak di c.get().
        charts = (
            '["oops_bukan_objek", '
            '{"type": "bar", "judul": "Laba Bersih", "labels": ["2023", "2024"], '
            '"nilai": [10, 12], "nama_file": "laba"}]'
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, charts)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("bukan objek", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_semua_elemen_objek_tetap_lolos_bersih(self):
        # Regresi negatif: draft yang benar tidak boleh ikut kena tandai.
        charts = (
            '[{"type": "bar", "judul": "Laba Bersih", "labels": ["2023", "2024"], '
            '"nilai": [10, 12], "nama_file": "laba"}]'
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, charts)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("bukan objek", result.stdout)
        self.assertIn("siap dirender", result.stdout)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
