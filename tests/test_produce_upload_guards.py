"""Test guard metadata.json (_validate_metadata, _tags_combined_length) di
produce.py sebelum upload ke YouTube.

Sebelumnya cuma judul (>100 karakter) yang dicek sebelum upload; deskripsi
(>5000 byte UTF-8) dan total tags (>500 karakter) BELUM dicek sama sekali —
video sudah selesai diunggah puluhan MB baru YouTube menolak dengan error
generik. Test ini memastikan ketiga guard gagal cepat, bukan gagal di tengah
upload. Jalankan: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from produce import _tags_combined_length, _validate_metadata


class TagsCombinedLengthTest(unittest.TestCase):
    def test_tag_tanpa_spasi_dihitung_apa_adanya(self):
        # Contoh resmi YouTube: "Foo-Baz" -> 7 karakter, tanpa tanda kutip.
        self.assertEqual(_tags_combined_length(["Foo-Baz"]), 7)

    def test_tag_berspasi_ditambah_2_utk_tanda_kutip(self):
        # Contoh resmi YouTube: "Foo Baz" -> 9 karakter (7 + 2 tanda kutip).
        self.assertEqual(_tags_combined_length(["Foo Baz"]), 9)

    def test_beberapa_tag_ditambah_koma_pemisah(self):
        # "AAA" + koma + "BBB" + koma + "CCC" = 3+1+3+1+3 = 11
        self.assertEqual(_tags_combined_length(["AAA", "BBB", "CCC"]), 11)

    def test_list_kosong_nol(self):
        self.assertEqual(_tags_combined_length([]), 0)


class ValidateMetadataTest(unittest.TestCase):
    def _meta(self, **overrides):
        base = {"title": "Judul Normal", "description": "Deskripsi biasa", "tags": ["saham"]}
        base.update(overrides)
        return base

    def test_metadata_valid_lolos(self):
        self.assertIsNone(_validate_metadata(self._meta()))

    def test_title_kosong_ditolak(self):
        err = _validate_metadata(self._meta(title=""))
        self.assertIn("title", err)

    def test_title_lebih_100_karakter_ditolak(self):
        err = _validate_metadata(self._meta(title="A" * 101))
        self.assertIn("100", err)

    def test_deskripsi_lebih_5000_byte_ditolak(self):
        err = _validate_metadata(self._meta(description="x" * 5001))
        self.assertIn("5000", err)

    def test_deskripsi_dihitung_byte_bukan_karakter(self):
        # "—" (em dash) = 3 byte UTF-8, jadi 2000 karakter em dash = 6000 byte,
        # sudah lewat batas walau char count-nya cuma 2000.
        err = _validate_metadata(self._meta(description="—" * 2000))
        self.assertIsNotNone(err)
        self.assertIn("byte", err)

    def test_tags_lebih_500_karakter_ditolak(self):
        err = _validate_metadata(self._meta(tags=["saham indonesia"] * 40))
        self.assertIn("500", err)

    def test_tags_kosong_lolos(self):
        self.assertIsNone(_validate_metadata(self._meta(tags=[])))


if __name__ == "__main__":
    unittest.main()
