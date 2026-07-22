"""Test cek_draft.py — khusus baris margin of safety di blok VALUATION.

Bug yang dites di sini: cek_draft.py sempat menghitung MoS dengan rumus
sendiri (dibagi harga), berbeda dari moovon_theme.verdict() (dibagi
nilai_wajar) yang benar-benar dipakai render_valuation() untuk menentukan
label BELI/TAHAN/HINDARI di video. Untuk harga=8000, nilai_wajar=9200:
  - rumus lama (salah): (9200-8000)/8000 = +15.0% -> tepat di ambang BELI
  - verdict() resmi:    (9200-8000)/9200 = +13.0% -> TAHAN
cek_draft.py dipakai sebagai gerbang persetujuan sebelum render ~10 menit
(TTS+encode), jadi angkanya wajib sama persis dengan yang dirender.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DRAFT_MOS_AMBANG = """# DRAFT SCRIPT — Bedah BBCA: Bank Termahal, Layak Beli?
**Topic keywords:** BBCA bank BCA valuasi

## SCRIPT
### HOOK (00:00–00:15)
Seperti biasa, konten ini cuma untuk edukasi ya.
> [VISUAL/CHART: cover]

### VALUASI (00:15–01:00)
Harga BBCA sekarang delapan ribu, nilai wajarnya sekitar sembilan ribu dua ratus.
> [VISUAL/CHART: gauge]

### PENUTUP (01:00–01:15)
Jangan lupa subscribe.
---

## VALUATION:
```json
{"harga": 8000, "nilai_wajar": 9200, "catatan": "uji ambang MoS"}
```
"""


def _run_cek_draft(tmp_path, text):
    draft = Path(tmp_path) / "draft.md"
    draft.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(ROOT / "cek_draft.py"), str(draft)],
        cwd=ROOT, capture_output=True, text=True,
    )


class MarginOfSafetySamaDenganVerdictResmi(unittest.TestCase):
    def test_mos_dan_label_ikut_rumus_verdict_bukan_rumus_lokal(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_cek_draft(tmp, DRAFT_MOS_AMBANG)
        out = result.stdout
        # verdict(8000, 9200) resmi: mos = (9200-8000)/9200 = +13.0%, label TAHAN
        self.assertIn("+13.0%", out)
        self.assertIn("TAHAN", out)
        # rumus lama yang salah (dibagi harga) akan mencetak +15.0% dan
        # menyiratkan ambang BELI (MOS_BELI=0.15) tercapai -- tidak boleh muncul.
        self.assertNotIn("+15.0%", out)


if __name__ == "__main__":
    unittest.main()
