"""Test entri riwayat yang ditulis upload() ke state.json['history'].

Bug nyata: upload() SELALU menulis "run_dir": None ke history, walau
run_dir_arg (folder run lokal yang baru saja diupload) tersedia di scope.
Bukti di state.json (dilihat manual): banyak entri lama masih null, dan
entri yang punya run_dir benar (mis. "output/run_20260708_234244") jelas
ditambal TANGAN belakangan -- bukan hasil otomatis dari upload().

Akibat: state.json kehilangan jejak folder run (script.txt/audio.mp3/
slide_*.png/chart) di balik tiap video yang sudah live, padahal itu satu-
satunya cara menelusuri balik sumber suatu upload untuk revisi/debug/backfill
(lihat backfill_audio_lang.py, cleanup_offniche.py yang bekerja dari
youtube_id -- run_dir jadi mata rantai yang putus ke sisi lokal).

Test ini menjalankan produce.upload() end-to-end dengan YouTube API di-stub
(tanpa jaringan/kredensial) dan memverifikasi entri history yang ditulis ke
state.json. Jalankan: python -m pytest tests/test_produce_upload_history.py
"""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import produce


class _FakeRequest:
    def __init__(self, result):
        self._result = result

    def execute(self):
        return self._result


class _FakeVideosResource:
    def insert(self, part, body, media_body):
        return _FakeRequest({"id": "FAKE_VIDEO_ID"})


class _FakeYoutubeClient:
    def videos(self):
        return _FakeVideosResource()

    def thumbnails(self):  # tak dipakai di test ini (thumbnail.jpg sengaja tak dibuat)
        raise AssertionError("thumbnails() tidak boleh dipanggil bila thumbnail.jpg tak ada")


class _FakeMediaFileUpload:
    def __init__(self, *args, **kwargs):
        pass


def _stub_youtube_modules():
    """Stub 'youtube_uploader' + 'googleapiclient.http' di sys.modules supaya
    upload() bisa dites tanpa google-api-python-client/kredensial terpasang."""
    fake_uploader = types.ModuleType("youtube_uploader")
    fake_uploader.get_youtube_client = lambda: _FakeYoutubeClient()

    fake_gac = types.ModuleType("googleapiclient")
    fake_gac_http = types.ModuleType("googleapiclient.http")
    fake_gac_http.MediaFileUpload = _FakeMediaFileUpload
    fake_gac.http = fake_gac_http

    return {
        "youtube_uploader": fake_uploader,
        "googleapiclient": fake_gac,
        "googleapiclient.http": fake_gac_http,
    }


class UploadHistoryRunDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        self.run_dir = Path(self.tmp.name) / "run_20260721_120000"
        self.run_dir.mkdir()
        (self.run_dir / "metadata.json").write_text(
            json.dumps({"title": "Judul Uji", "description": "desk", "tags": ["a"]}),
            encoding="utf-8",
        )
        (self.run_dir / "video.mp4").write_bytes(b"\x00" * 128)  # dummy, cuma butuh stat()

        self.state_path = Path(self.tmp.name) / "state.json"
        self.state_path.write_text(json.dumps({"phase": "selesai_render_menunggu_review"}),
                                    encoding="utf-8")

    def test_run_dir_tercatat_di_history_bukan_none(self):
        run_dir_arg = str(self.run_dir)  # absolut -> ROOT / run_dir_arg = run_dir_arg apa adanya
        with mock.patch.dict(sys.modules, _stub_youtube_modules()), \
             mock.patch.object(produce, "STATE_PATH", self.state_path):
            produce.upload(run_dir_arg, privacy="unlisted", at=None)

        st = json.loads(self.state_path.read_text(encoding="utf-8"))
        entry = st["history"][-1]
        self.assertEqual(entry["youtube_id"], "FAKE_VIDEO_ID")
        self.assertEqual(
            entry["run_dir"], run_dir_arg,
            "history run_dir harus mencatat folder run yang barusan diupload, bukan None -- "
            "kalau tidak, tiap video live kehilangan jejak ke script/audio/slide sumbernya."
        )


if __name__ == "__main__":
    unittest.main()
