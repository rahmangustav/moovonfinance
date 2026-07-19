"""Test fungsi murni parsing/label di core/visuals.py — dipakai di setiap
render video panjang untuk memecah naskah jadi section, memilih label layar,
meringkas narasi untuk slide, dan mencocokkan chart ke section-nya. Kalau ada
regresi di sini, section bisa salah dikelompokkan atau caption di layar jadi
kacau tanpa ketahuan sampai video sudah setengah dirender. Belum pernah
punya test. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from visuals import (
    parse_sections,
    _clean_label,
    _short_content,
    _slide_type,
    _match_charts_to_sections,
    _guess_ticker,
    _first_sentence,
    _id_date,
)


class ParseSectionsTest(unittest.TestCase):
    def test_pecah_berdasarkan_label_kurung_siku(self):
        script = "[HOOK]Kenapa BBCA mahal?[VALUASI]Harga 9800 nilai wajar 9150."
        sections = parse_sections(script)
        self.assertEqual(
            sections,
            [
                {"label": "HOOK", "content": "Kenapa BBCA mahal?"},
                {"label": "VALUASI", "content": "Harga 9800 nilai wajar 9150."},
            ],
        )

    def test_label_dinormalisasi_ke_uppercase(self):
        sections = parse_sections("[hook]isi")
        self.assertEqual(sections[0]["label"], "HOOK")

    def test_section_kosong_dibuang(self):
        sections = parse_sections("[HOOK]isi[KOSONG][ISI]lagi")
        labels = [s["label"] for s in sections]
        self.assertNotIn("KOSONG", labels)

    def test_fallback_potong_per_500_karakter_bila_tanpa_label(self):
        script = "a" * 1200
        sections = parse_sections(script)
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]["label"], "BAGIAN 1")
        self.assertEqual(len(sections[0]["content"]), 500)
        self.assertEqual(len(sections[2]["content"]), 200)

    def test_string_kosong_fallback_tidak_menghasilkan_section(self):
        self.assertEqual(parse_sections(""), [])


class CleanLabelTest(unittest.TestCase):
    def test_label_dipetakan_lewat_display_map(self):
        self.assertEqual(_clean_label("HOOK"), "TERKINI")
        self.assertEqual(_clean_label("ISI UTAMA"), "PEMBAHASAN")
        self.assertEqual(_clean_label("KESIMPULAN"), "KESIMPULAN")

    def test_judul_deskriptif_dipakai_dibanding_kode_section(self):
        self.assertEqual(
            _clean_label("SECTION 1 - Fundamentalnya Masih Bagus"),
            "FUNDAMENTALNYA MASIH BAGUS",
        )

    def test_durasi_dibuang_sebelum_dipetakan(self):
        self.assertEqual(_clean_label("KESIMPULAN - 30 DETIK"), "KESIMPULAN")
        self.assertEqual(_clean_label("SECTION 1 - 15 DETIK"), "SECTION 1")

    def test_hyphen_kata_majemuk_tidak_terpotong(self):
        self.assertEqual(_clean_label("Baik-Baik Saja"), "BAIK-BAIK SAJA")


class ShortContentTest(unittest.TestCase):
    def test_ambil_maksimal_tiga_kalimat(self):
        content = (
            "Kalimat satu cukup panjang untuk lolos budget karakter awal. "
            "Kalimat dua juga cukup panjang untuk lolos budget karakter kedua. "
            "Kalimat tiga lumayan panjang juga sekali ini. "
            "Kalimat empat seharusnya tidak pernah muncul di hasil akhir."
        )
        result = _short_content(content)
        self.assertNotIn("Kalimat empat", result)
        self.assertIn("Kalimat satu", result)

    def test_pembuka_pendek_dipaksa_gandeng_kalimat_berikut(self):
        content = "Nah, ini bagian intinya. Ini kalimat kedua yang menjelaskan isi."
        result = _short_content(content)
        self.assertIn("Nah, ini bagian intinya.", result)
        self.assertIn("Ini kalimat kedua", result)

    def test_bold_italic_markdown_dibuang(self):
        result = _short_content("Ini **tebal** dan *miring* dalam satu kalimat.")
        self.assertNotIn("*", result)
        self.assertIn("tebal", result)

    def test_content_kosong_mengembalikan_string_kosong(self):
        self.assertEqual(_short_content(""), "")

    def test_kalimat_tunggal_tanpa_tanda_baca_tetap_dikembalikan(self):
        result = _short_content("Satu kalimat saja tanpa titik")
        self.assertEqual(result, "Satu kalimat saja tanpa titik")

    def test_kalimat_pertama_selalu_masuk_walau_lewat_budget_karakter(self):
        long_first = "Kalimat pertama sangat panjang sekali " * 6 + "selesai."
        result = _short_content(long_first, max_chars=50)
        self.assertTrue(result.startswith("Kalimat pertama sangat panjang"))


class SlideTypeTest(unittest.TestCase):
    def test_hook_terdeteksi(self):
        self.assertEqual(_slide_type("HOOK"), "hook")

    def test_cta_terdeteksi(self):
        self.assertEqual(_slide_type("CTA - Ajakan"), "cta")

    def test_default_content(self):
        self.assertEqual(_slide_type("ISI UTAMA"), "content")

    def test_case_insensitive(self):
        self.assertEqual(_slide_type("kesimpulan"), "content")
        self.assertEqual(_slide_type("cta akhir"), "cta")


class MatchChartsToSectionsTest(unittest.TestCase):
    def setUp(self):
        self.sections = [
            {"label": "HOOK", "content": "x"},
            {"label": "ISI UTAMA", "content": "y"},
            {"label": "KESIMPULAN", "content": "z"},
        ]

    def test_chart_dengan_section_cocok_dilekatkan_ke_section_itu(self):
        charts = [{"section": "isi utama", "type": "line"}]
        result = _match_charts_to_sections(self.sections, charts)
        self.assertEqual(result, [[], charts, []])

    def test_chart_tanpa_section_jatuh_ke_isi_utama(self):
        charts = [{"type": "donut"}]
        result = _match_charts_to_sections(self.sections, charts)
        self.assertEqual(result[1], charts)

    def test_chart_dengan_section_tak_dikenal_jatuh_ke_isi_utama(self):
        charts = [{"section": "tidak ada", "type": "bar"}]
        result = _match_charts_to_sections(self.sections, charts)
        self.assertEqual(result[1], charts)

    def test_tanpa_isi_utama_fallback_ke_section_terakhir(self):
        sections = [{"label": "HOOK", "content": "x"}, {"label": "KESIMPULAN", "content": "z"}]
        charts = [{"type": "donut"}]
        result = _match_charts_to_sections(sections, charts)
        self.assertEqual(result, [[], charts])

    def test_sections_kosong_mengembalikan_list_kosong(self):
        self.assertEqual(_match_charts_to_sections([], [{"type": "donut"}]), [])

    def test_charts_none_tidak_crash(self):
        result = _match_charts_to_sections(self.sections, None)
        self.assertEqual(result, [[], [], []])


class GuessTickerTest(unittest.TestCase):
    def test_temukan_ticker_4_huruf_kapital(self):
        self.assertEqual(_guess_ticker("Bedah BBCA: Bank Termahal"), "BBCA")

    def test_fallback_idx_bila_tak_ada(self):
        self.assertEqual(_guess_ticker("tidak ada ticker di sini"), "IDX")

    def test_cek_beberapa_teks_berurutan(self):
        self.assertEqual(_guess_ticker("", "ICBP naik terus"), "ICBP")


class FirstSentenceTest(unittest.TestCase):
    def test_ambil_kalimat_pertama_saja(self):
        result = _first_sentence("Ini kalimat pertama. Ini kalimat kedua.")
        self.assertEqual(result, "Ini kalimat pertama.")

    def test_dipotong_dan_diberi_ellipsis_bila_lewat_batas(self):
        result = _first_sentence("x" * 150, max_chars=120)
        self.assertTrue(result.endswith("…"))
        self.assertLessEqual(len(result), 121)

    def test_string_kosong(self):
        self.assertEqual(_first_sentence(""), "")

    def test_none_tidak_crash(self):
        self.assertEqual(_first_sentence(None), "")

    def test_markdown_dibuang(self):
        result = _first_sentence("**#Judul** [catatan] biasa.")
        self.assertNotIn("#", result)
        self.assertNotIn("[", result)


class IdDateTest(unittest.TestCase):
    def test_format_tanggal_indonesia(self):
        import datetime
        self.assertEqual(_id_date(datetime.datetime(2026, 7, 19)), "19 JUL 2026")

    def test_bulan_januari(self):
        import datetime
        self.assertEqual(_id_date(datetime.datetime(2026, 1, 1)), "01 JAN 2026")


if __name__ == "__main__":
    unittest.main()
