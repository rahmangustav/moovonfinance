"""Test cek_draft.py — validasi field 'persentase' pada chart donut.

Bug yang dites di sini: cek_draft.py memanggil float(x) langsung pada tiap
nilai `persentase` tanpa menangkap error. Draft yang menulis nilai persentase
sebagai TEKS (format lazim kanal ini — angka Indonesia pakai koma desimal,
mis. "45,5", atau ada sufiks "%") membuat cek_draft.py CRASH dengan traceback
Python mentah di tengah jalan, sebelum sempat mencetak ringkasan hasil
pemeriksaan — padahal justru cek_draft.py ada supaya masalah begini ketahuan
lewat laporan bersih SEBELUM render ~10 menit (TTS+encode), bukan lewat crash.

Nilai teks itu juga bukan cuma soal gaya: chart_templates.donut_chart()
meneruskan `persentase` apa adanya ke matplotlib ax.pie(), yang menolak
elemen non-numerik (int/float) — jadi draft begini akan membuat chart donut
gagal render dan DIAM-DIAM hilang dari video kalau lolos sampai situ tanpa
ketahuan di sini.
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
[{{"type": "donut", "judul": "Alokasi Portofolio", "labels": ["Saham", "Obligasi"], "persentase": {persentase}, "nama_file": "alokasi"}}]
```
"""


def _run_cek_draft(tmp_path, persentase_json_literal):
    draft = Path(tmp_path) / "draft.md"
    draft.write_text(
        DRAFT_TEMPLATE.format(persentase=persentase_json_literal), encoding="utf-8"
    )
    return subprocess.run(
        [sys.executable, str(ROOT / "cek_draft.py"), str(draft)],
        cwd=ROOT, capture_output=True, text=True,
    )


class DonutPersentaseTeksTidakCrash(unittest.TestCase):
    def test_persentase_koma_desimal_indonesia_tidak_crash(self):
        # "45,5" (format angka Indonesia lazim di draft kanal ini) dulu bikin
        # float("45,5") melempar ValueError yang tak tertangkap -> traceback.
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, '["45,5", "54,5"]')
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        # Harus tetap sampai ke ringkasan akhir, melaporkan masalah dgn bersih.
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("bukan string", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_persentase_dengan_sufiks_persen_tidak_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, '["45%", "55%"]')
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("MASALAH", result.stdout)

    def test_persentase_angka_polos_json_tetap_lolos_bersih(self):
        # Regresi negatif: draft yang BENAR (angka JSON polos, bukan teks)
        # tidak boleh ikut kena tandai gara-gara perbaikan ini.
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, "[45.5, 54.5]")
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("chart 1 donut persentase berupa angka polos JSON", result.stdout)
        self.assertIn("chart 1 donut berjumlah ~100 (kini 100)", result.stdout)
        self.assertIn("siap dirender", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_persentase_angka_bulat_json_tetap_lolos_bersih(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, "[45, 55]")
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("siap dirender", result.stdout)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
