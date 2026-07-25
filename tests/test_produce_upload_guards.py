"""Test guard metadata.json (_validate_metadata, _tags_combined_length) di
produce.py sebelum upload ke YouTube.

Sebelumnya cuma judul (>100 karakter) yang dicek sebelum upload; deskripsi
(>5000 byte UTF-8) dan total tags (>500 karakter) BELUM dicek sama sekali —
video sudah selesai diunggah puluhan MB baru YouTube menolak dengan error
generik. Test ini memastikan ketiga guard gagal cepat, bukan gagal di tengah
upload. Jalankan: python -m unittest discover -s tests

Bug nyata yang ditangkap di kelas TypeCoercionTest: metadata.json diketik
manual (lihat docstring produce.py — "Tulis output/<run_dir>/metadata.json
... setelah user approve"), jadi title/description/tags rawan salah ketik
jadi tipe bukan string (contoh realistis: tag tahun ditulis `2026` tanpa
tanda kutip alih-alih `"2026"` — tetap JSON valid). Sebelum perbaikan,
_validate_metadata() -- yang tujuannya justru "gagal cepat sebelum
mengunggah puluhan MB, biar jelas apa yang harus diperbaiki" -- malah
meledak dengan TypeError/AttributeError mentah dari .strip()/.encode()/
len() saat memvalidasi field bertipe salah, persis kebalikan dari tujuannya.
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


class TypeCoercionTest(unittest.TestCase):
    """metadata.json diketik manual -- field bisa salah ketik jadi tipe
    bukan string (angka telanjang, dsb). _validate_metadata() harus
    melaporkan itu lewat pesan jelas, bukan crash TypeError/AttributeError
    mentah sebelum sempat mencetak satu pun hasil pemeriksaan."""

    def _meta(self, **overrides):
        base = {"title": "Judul Normal", "description": "Deskripsi biasa", "tags": ["saham"]}
        base.update(overrides)
        return base

    def test_tag_angka_telanjang_dilaporkan_bukan_crash(self):
        # Kasus realistis: tag tahun ditulis 2026 (tanpa kutip) alih-alih
        # "2026" -- tetap JSON valid, tapi bikin _tags_combined_length()
        # meledak `TypeError: object of type 'int' has no len()` sebelum fix.
        err = _validate_metadata(self._meta(tags=["saham", 2026]))
        self.assertIsNotNone(err)
        self.assertIn("tags", err)

    def test_title_bukan_string_dilaporkan_bukan_crash(self):
        # Sebelum fix: (meta.get("title") or "").strip() -> AttributeError
        # kalau title tertulis sebagai angka (mis. salin tempel nomor draft).
        err = _validate_metadata(self._meta(title=12345))
        self.assertIsNotNone(err)
        self.assertIn("title", err)

    def test_description_bukan_string_dilaporkan_bukan_crash(self):
        # Sebelum fix: description.encode("utf-8") -> AttributeError kalau
        # description tertulis sebagai angka.
        err = _validate_metadata(self._meta(description=20260101))
        self.assertIsNotNone(err)
        self.assertIn("description", err)

    def test_tipe_benar_tetap_lolos_seperti_sebelumnya(self):
        # Regresi negatif: guard tipe baru tidak boleh menolak metadata yang
        # sudah benar (semua string, seperti kasus normal).
        self.assertIsNone(_validate_metadata(self._meta()))


if __name__ == "__main__":
    unittest.main()
