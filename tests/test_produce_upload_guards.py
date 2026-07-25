"""Test guard metadata.json (_validate_metadata, _tags_combined_length) &
guard video.mp4 hilang di produce.py sebelum upload ke YouTube.

Sebelumnya cuma judul (>100 karakter) yang dicek sebelum upload; deskripsi
(>5000 byte UTF-8) dan total tags (>500 karakter) BELUM dicek sama sekali —
video sudah selesai diunggah puluhan MB baru YouTube menolak dengan error
generik. Test ini memastikan ketiga guard gagal cepat, bukan gagal di tengah
upload. Jalankan: python -m unittest discover -s tests

Guard tambahan: sebelum perbaikan ini, upload() tidak pernah mengecek
`video_path.exists()` (beda dengan meta_path yang sudah dicek) -- run_dir
dengan metadata.json tapi belum di-render (video.mp4 belum ada) bikin
FileNotFoundError mentah dari video_path.stat() di tengah fungsi, bukan
pesan error jelas seperti guard-guard lain di fungsi yang sama.
"""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

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


class UploadMissingVideoTest(unittest.TestCase):
    """upload() harus gagal cepat dengan pesan jelas kalau video.mp4 belum
    ada di run_dir, bukan FileNotFoundError mentah dari video_path.stat()."""

    def setUp(self):
        # produce.py mengimpor `youtube_uploader`/`googleapiclient.http` di
        # dalam upload() -- stub keduanya biar test tidak butuh paket google
        # eksternal terpasang, dan tidak pernah menyentuh jaringan.
        self._patched = {}
        for name, mod in {
            "youtube_uploader": types.SimpleNamespace(get_youtube_client=lambda: None),
            "googleapiclient": types.ModuleType("googleapiclient"),
            "googleapiclient.http": types.SimpleNamespace(MediaFileUpload=object),
        }.items():
            self._patched[name] = sys.modules.get(name)
            sys.modules[name] = mod

    def tearDown(self):
        for name, old in self._patched.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old

    def test_upload_tanpa_video_mp4_gagal_dengan_pesan_jelas(self):
        import produce

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run_test"
            run_dir.mkdir()
            (run_dir / "metadata.json").write_text(json.dumps(
                {"title": "Judul", "description": "d", "tags": ["a"]}))

            with mock.patch.object(produce, "ROOT", Path(tmp)):
                with mock.patch("builtins.print") as fake_print:
                    produce.upload("run_test", "public", "now")

            messages = " ".join(str(c.args[0]) for c in fake_print.call_args_list)
            self.assertIn("video.mp4", messages)
            self.assertIn("render", messages)


if __name__ == "__main__":
    unittest.main()
