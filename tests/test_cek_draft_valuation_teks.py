"""Test cek_draft.py — validasi field 'harga'/'nilai_wajar' pada blok VALUATION.

Bug yang dites di sini: cek_draft.py memanggil float(harga)/float(wajar)
langsung tanpa menangkap error. Draft yang menulis salah satu angka sebagai
TEKS (mis. penulis draft menambah catatan penjelas langsung di angka, seperti
"8000 (penutupan)", alih-alih memakai field 'catatan' yang memang disediakan
untuk itu) membuat cek_draft.py CRASH dengan traceback Python mentah di
tengah jalan — sebelum sempat mencetak blok SNAPSHOT dan ringkasan hasil
pemeriksaan, padahal cek_draft.py ada supaya masalah begini ketahuan lewat
laporan bersih SEBELUM render ~10 menit (TTS+encode), bukan lewat crash.

Ini kelas bug yang sama persis dengan yang sudah diperbaiki untuk field
'persentase' chart donut (lihat test_cek_draft_donut_persentase.py) — hanya
belum pernah diterapkan ke blok VALUATION.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DRAFT_TEMPLATE = """# DRAFT SCRIPT — Bedah BBCA: Bank Termahal, Layak Beli?
**Topic keywords:** BBCA bank BCA valuasi

## SCRIPT
### HOOK (00:00-00:15)
Seperti biasa, konten ini cuma untuk edukasi ya.
> [VISUAL/CHART: cover]

### VALUASI (00:15-01:00)
Harga BBCA sekarang delapan ribu, nilai wajarnya sekitar sembilan ribu dua ratus.
> [VISUAL/CHART: gauge]

### PENUTUP (01:00-01:15)
Jangan lupa subscribe.
---

## VALUATION:
```json
{{"harga": {harga}, "nilai_wajar": {nilai_wajar}, "catatan": "uji tipe angka"}}
```
"""


def _run_cek_draft(tmp_path, harga_json_literal, nilai_wajar_json_literal):
    draft = Path(tmp_path) / "draft.md"
    draft.write_text(
        DRAFT_TEMPLATE.format(harga=harga_json_literal, nilai_wajar=nilai_wajar_json_literal),
        encoding="utf-8",
    )
    return subprocess.run(
        [sys.executable, str(ROOT / "cek_draft.py"), str(draft)],
        cwd=ROOT, capture_output=True, text=True,
    )


class ValuationHargaTeksTidakCrash(unittest.TestCase):
    def test_harga_berbentuk_teks_dengan_catatan_menempel_tidak_crash(self):
        # "8000 (penutupan)" dulu bikin float() melempar ValueError yang tak
        # tertangkap -> traceback, seluruh sisa pemeriksaan (SNAPSHOT +
        # ringkasan) tidak pernah tercetak.
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cek(tmp, '"8000 (penutupan)"', "9200")
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("angka polos JSON", result.stdout)
        self.assertIn("harga", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_nilai_wajar_berbentuk_teks_tidak_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cek(tmp, "8000", '"9200 (estimasi)"')
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("nilai_wajar", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_masih_sampai_ke_ringkasan_akhir_walau_valuation_rusak(self):
        # Sisa pemeriksaan (kesimpulan) harus tetap tercetak, bukan berhenti
        # di tengah gara-gara valuation salah tipe.
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cek(tmp, '"delapan ribu"', "9200")
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("perbaiki sebelum render", result.stdout)

    def test_harga_nilai_wajar_angka_polos_json_tetap_lolos_bersih(self):
        # Regresi negatif: draft yang BENAR (angka JSON polos) tidak boleh
        # ikut kena tandai gara-gara perbaikan ini.
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cek(tmp, "8000", "9200")
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("valuation harga & nilai_wajar berupa angka polos JSON", result.stdout)
        self.assertIn("+13.0%", result.stdout)
        self.assertIn("TAHAN", result.stdout)

    @staticmethod
    def run_cek(tmp, harga, nilai_wajar):
        return _run_cek_draft(tmp, harga, nilai_wajar)


if __name__ == "__main__":
    unittest.main()
