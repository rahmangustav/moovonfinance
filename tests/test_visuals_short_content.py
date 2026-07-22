"""Test _short_content() di core/visuals.py — ringkasan narasi utk caption
di layar tiap slide.

Bug nyata yang ditangkap di sini: guard "kalimat pembuka pendek dipaksa
gandeng kalimat berikutnya" (lihat komentar di core/visuals.py) tidak pernah
aktif karena dihitung dari iterasi yang salah — akibatnya caption bisa
berakhir HANYA berisi basa-basi pembuka tanpa isi sama sekali kalau kalimat
kedua melebihi budget karakter. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.visuals import _short_content


KALIMAT_ISI_PANJANG = (
    "Laba bersih BBCA naik sepuluh persen jadi empat puluh triliun rupiah "
    "pada kuartal pertama tahun ini setelah pertumbuhan kredit yang solid "
    "di segmen korporasi maupun ritel domestik yang terus membaik sepanjang "
    "tahun berjalan ini secara konsisten."
)


class ShortContentOpenerPendekTest(unittest.TestCase):
    def test_pembuka_pendek_tidak_boleh_sendirian_walau_kalimat_isi_panjang(self):
        content = f"Nah, ini bagian intinya. {KALIMAT_ISI_PANJANG}"
        result = _short_content(content, max_sentences=3, max_chars=100)
        self.assertIn("Laba bersih BBCA", result,
                      "caption berakhir cuma basa-basi pembuka tanpa isi")

    def test_pembuka_pendek_lain_juga_dipaksa_gandeng(self):
        content = f"Oke, lanjut ke bagian berikutnya. {KALIMAT_ISI_PANJANG}"
        result = _short_content(content, max_sentences=3, max_chars=80)
        self.assertIn("Laba bersih BBCA", result)

    def test_budget_karakter_tetap_berlaku_setelah_kalimat_kedua(self):
        # Guard cuma berlaku SEKALI (tepat setelah pembuka pendek) — kalimat
        # ketiga dan seterusnya tetap harus dihormati budget karakternya,
        # bukan lolos terus-terusan.
        content = (
            "Nah, ini bagian intinya. "
            "Laba bersih naik signifikan tahun ini. "
            "Pertumbuhan kredit korporasi maupun ritel domestik terus "
            "membaik sepanjang tahun berjalan secara konsisten dan "
            "berkelanjutan hingga akhir periode pelaporan kuartalan."
        )
        result = _short_content(content, max_sentences=3, max_chars=60)
        self.assertNotIn("Pertumbuhan kredit", result)

    def test_pembuka_tidak_pendek_perilaku_normal_tak_berubah(self):
        content = (
            "Kalimat pertama yang sudah cukup panjang untuk lolos budget "
            "karakter awal. Kalimat kedua juga panjang lumayan sekali ini."
        )
        result = _short_content(content, max_sentences=3, max_chars=60)
        self.assertEqual(
            result,
            "Kalimat pertama yang sudah cukup panjang untuk lolos budget karakter awal.",
        )


if __name__ == "__main__":
    unittest.main()
