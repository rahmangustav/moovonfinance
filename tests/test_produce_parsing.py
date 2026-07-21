"""Test parser draft naskah (parse_draft) di produce.py.

Parser ini mengubah assets/draft_script_moovon.md jadi input render_slides —
kalau ada regresi di sini, render bisa salah atau crash di tengah pipeline
tanpa ketahuan sampai video sudah setengah jadi. Belum pernah punya test.
Jalankan: python -m unittest discover -s tests
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from produce import parse_draft, _fenced_json_after


DRAFT_LENGKAP = """# DRAFT SCRIPT — Bedah BBCA: Bank Termahal, Layak Beli?
**Topic keywords:** BBCA bank BCA valuasi
**Thumbnail text:** BBCA MAHAL?

## SCRIPT
### HOOK (00:00–00:15)
Kenapa BBCA selalu jadi saham termahal di bursa?
> [VISUAL/CHART: cover]

### VALUASI (00:15–01:00)
Harga BBCA sekarang 9800, nilai wajarnya sekitar 9150.
> [VISUAL/CHART: gauge]
---

## CHARTS: (opsional)
```json
[{"type": "line", "title": "Harga 5 tahun"}]
```

## VALUATION:
```json
{"harga": 9800, "nilai_wajar": 9150, "catatan": "Premium wajar bank terbaik"}
```

## SNAPSHOT:
```json
{"judul": "BBCA — Kuartal I 2026", "metrics": [["Laba bersih", "14,7 T", "up"]]}
```
"""

DRAFT_MINIMAL = """# DRAFT SCRIPT — Judul Sederhana

## SCRIPT
### INTRO (00:00–00:10)
Halo semua.
---
"""


def _write(tmp_path, text):
    p = Path(tmp_path) / "draft.md"
    p.write_text(text, encoding="utf-8")
    return p


class ParseDraftTest(unittest.TestCase):
    def test_draft_lengkap_semua_field_terisi(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = parse_draft(_write(tmp, DRAFT_LENGKAP))

        self.assertEqual(draft["title"], "Bedah BBCA: Bank Termahal, Layak Beli?")
        self.assertEqual(draft["topic"], "BBCA bank BCA valuasi")
        self.assertEqual(draft["thumbnail_text"], "BBCA MAHAL?")
        self.assertEqual(len(draft["charts"]), 1)
        self.assertEqual(draft["valuation"], {
            "harga": 9800, "nilai_wajar": 9150,
            "catatan": "Premium wajar bank terbaik",
        })
        self.assertEqual(draft["snapshot"]["judul"], "BBCA — Kuartal I 2026")
        # baris anotasi "> [VISUAL/CHART: ...]" harus dibuang dari narasi
        self.assertNotIn("VISUAL/CHART", draft["script"])
        self.assertIn("[HOOK]", draft["script"])
        self.assertIn("[VALUASI]", draft["script"])

    def test_draft_minimal_field_opsional_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = parse_draft(_write(tmp, DRAFT_MINIMAL))

        self.assertEqual(draft["title"], "Judul Sederhana")
        self.assertEqual(draft["topic"], "Judul Sederhana")  # fallback ke title
        self.assertIsNone(draft["thumbnail_text"])
        self.assertIsNone(draft["valuation"])
        self.assertIsNone(draft["snapshot"])
        self.assertEqual(draft["charts"], [])

    def test_tanpa_heading_judul_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "## SCRIPT\n### A (00:00-00:10)\nHalo\n---\n")
            with self.assertRaises(ValueError):
                parse_draft(p)

    def test_tanpa_section_script_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "# DRAFT SCRIPT — Judul\nTidak ada section script.\n")
            with self.assertRaises(ValueError):
                parse_draft(p)

    def test_tanpa_heading_dalam_script_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "# DRAFT SCRIPT — Judul\n## SCRIPT\nCuma teks polos.\n---\n")
            with self.assertRaises(ValueError):
                parse_draft(p)

    def test_ticker_none_disembunyikan(self):
        text = DRAFT_MINIMAL.replace(
            "## SCRIPT", "**Ticker:** none\n\n## SCRIPT"
        )
        with tempfile.TemporaryDirectory() as tmp:
            draft = parse_draft(_write(tmp, text))
        self.assertEqual(draft["ticker_override"], "")

    def test_ticker_biasa_dipertahankan(self):
        text = DRAFT_MINIMAL.replace(
            "## SCRIPT", "**Ticker:** BBCA\n\n## SCRIPT"
        )
        with tempfile.TemporaryDirectory() as tmp:
            draft = parse_draft(_write(tmp, text))
        self.assertEqual(draft["ticker_override"], "BBCA")


class FencedJsonAfterTest(unittest.TestCase):
    def test_json_rusak_kembalikan_none_bukan_exception(self):
        text = "## VALUATION:\n```json\n{tidak valid,,,}\n```\n"
        self.assertIsNone(_fenced_json_after(text, "VALUATION"))

    def test_heading_tak_ada_kembalikan_none(self):
        text = "## SNAPSHOT:\n```json\n{}\n```\n"
        self.assertIsNone(_fenced_json_after(text, "VALUATION"))

    def test_tidak_rebutan_dengan_blok_lain(self):
        # anchored ke heading masing-masing -> VALUATION tidak boleh menangkap
        # blok json milik SNAPSHOT yang muncul duluan di teks
        text = (
            "## SNAPSHOT:\n```json\n[1, 2, 3]\n```\n\n"
            "## VALUATION:\n```json\n{\"harga\": 100, \"nilai_wajar\": 200}\n```\n"
        )
        self.assertEqual(
            _fenced_json_after(text, "VALUATION"),
            {"harga": 100, "nilai_wajar": 200},
        )
        self.assertEqual(_fenced_json_after(text, "SNAPSHOT"), [1, 2, 3])

    def test_tidak_mencuri_blok_json_section_berikutnya(self):
        # regresi: kalau heading yang dicari TIDAK punya blok json sendiri
        # (draft belum lengkap), pencarian dulu melewati batas heading '##'
        # berikutnya dan salah mengambil blok json milik section lain.
        text = (
            "## VALUATION:\n"
            "(lupa isi json di sini)\n\n"
            "## SNAPSHOT:\n```json\n{\"judul\": \"BBCA\", \"metrics\": []}\n```\n"
        )
        self.assertIsNone(_fenced_json_after(text, "VALUATION"))
        self.assertEqual(
            _fenced_json_after(text, "SNAPSHOT"),
            {"judul": "BBCA", "metrics": []},
        )

    def test_blok_json_di_heading_terakhir_tanpa_heading_berikutnya(self):
        # heading terakhir di file (tak ada '##' sesudahnya) tetap harus
        # menemukan blok json miliknya sendiri.
        text = "## VALUATION:\n```json\n{\"harga\": 1, \"nilai_wajar\": 2}\n```\n"
        self.assertEqual(
            _fenced_json_after(text, "VALUATION"),
            {"harga": 1, "nilai_wajar": 2},
        )


if __name__ == "__main__":
    unittest.main()
