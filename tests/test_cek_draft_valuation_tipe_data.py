"""Test cek_draft.py — validasi TIPE DATA field 'harga'/'nilai_wajar' pada
blok VALUATION.

Bug yang dites: cek_draft.py hanya mengecek harga/nilai_wajar *truthy* lalu
langsung memanggil float(harga) untuk keperluan tampilan MoS di layar. Kalau
draft menulis angka itu sebagai TEKS berkutip (mis. `"harga": "9800"` —
kesalahan ketik JSON yang gampang terjadi), float("9800") tetap berhasil
tanpa error, jadi gerbang ini melaporkan "aman" -- padahal jalur render
sungguhan (core/visuals.create_video -> moovon_theme.verdict) memakai
nilainya APA ADANYA tanpa konversi, dan meledak TypeError di tengah render,
SETELAH TTS ~10 menit selesai. Persis kelas bug yang sama dengan "persentase
donut ditulis sebagai teks" (lihat test_cek_draft_donut_persentase.py), cuma
di field yang berbeda.
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

### VALUASI (00:15-01:00)
Harga BBCA sekarang segini, nilai wajarnya segitu.

### PENUTUP (01:00-01:15)
Jangan lupa subscribe.
---

## VALUATION:
```json
{valuation_json}
```
"""


def _run_cek_draft(tmp_path, valuation_json_literal):
    draft = Path(tmp_path) / "draft.md"
    draft.write_text(
        DRAFT_TEMPLATE.format(valuation_json=valuation_json_literal), encoding="utf-8"
    )
    return subprocess.run(
        [sys.executable, str(ROOT / "cek_draft.py"), str(draft)],
        cwd=ROOT, capture_output=True, text=True,
    )


class ValuationTipeDataTeksTertangkap(unittest.TestCase):
    def test_harga_berkutip_string_tertangkap_sebagai_masalah(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, '{"harga": "9800", "nilai_wajar": 9150}')
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("berbentuk teks", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_nilai_wajar_berkutip_string_tertangkap_sebagai_masalah(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, '{"harga": 9800, "nilai_wajar": "9150"}')
        self.assertIn("MASALAH", result.stdout)
        self.assertIn("berbentuk teks", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_valuation_angka_polos_json_tetap_lolos_bersih(self):
        # Regresi negatif: draft yang BENAR tidak boleh ikut kena tandai.
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, '{"harga": 9800, "nilai_wajar": 9150, "catatan": "x"}')
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("valuation harga & nilai_wajar berupa angka JSON polos", result.stdout)
        self.assertNotIn("MASALAH", result.stdout)


if __name__ == "__main__":
    unittest.main()
