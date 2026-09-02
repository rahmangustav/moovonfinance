"""Test caption track diunggah dari video.srt saat upload().

Bug/celah nyata: create_video() sudah membuat video.srt (dipakai buat burn-in
subtitle), tapi upload() sebelumnya tak pernah mengunggahnya sebagai caption
track YouTube lewat captions().insert(). Akibatnya video panjang tak punya CC
yang bisa dicari/diindeks/diterjemahkan otomatis oleh YouTube, padahal file
SRT-nya sudah ada gratis di run_dir sejak render(). Test ini memastikan:
1. video.srt yang ada ikut diunggah sebagai caption 'id' setelah videos().insert().
2. run tanpa video.srt tidak meledak (captions() tak dipanggil sama sekali).
Jalankan: python -m pytest tests/test_produce_upload_captions.py
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


class _FakeCaptionsResource:
    def __init__(self):
        self.calls = []

    def insert(self, part, body, media_body):
        self.calls.append(body)
        return _FakeRequest({"id": "FAKE_CAPTION_ID"})


class _FakeYoutubeClient:
    def __init__(self):
        self.captions_resource = _FakeCaptionsResource()

    def videos(self):
        return _FakeVideosResource()

    def thumbnails(self):
        raise AssertionError("thumbnails() tidak boleh dipanggil bila thumbnail.jpg tak ada")

    def captions(self):
        return self.captions_resource


class _FakeMediaFileUpload:
    def __init__(self, *args, **kwargs):
        pass


def _stub_youtube_modules(fake_client):
    fake_uploader = types.ModuleType("youtube_uploader")
    fake_uploader.get_youtube_client = lambda: fake_client

    fake_gac = types.ModuleType("googleapiclient")
    fake_gac_http = types.ModuleType("googleapiclient.http")
    fake_gac_http.MediaFileUpload = _FakeMediaFileUpload
    fake_gac.http = fake_gac_http

    return {
        "youtube_uploader": fake_uploader,
        "googleapiclient": fake_gac,
        "googleapiclient.http": fake_gac_http,
    }


class UploadCaptionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        self.run_dir = Path(self.tmp.name) / "run_20260721_120000"
        self.run_dir.mkdir()
        (self.run_dir / "metadata.json").write_text(
            json.dumps({"title": "Judul Uji", "description": "desk", "tags": ["a"]}),
            encoding="utf-8",
        )
        (self.run_dir / "video.mp4").write_bytes(b"\x00" * 128)

        self.state_path = Path(self.tmp.name) / "state.json"
        self.state_path.write_text(json.dumps({"phase": "selesai_render_menunggu_review"}),
                                    encoding="utf-8")

    def test_video_srt_ada_diunggah_sebagai_caption_id(self):
        (self.run_dir / "video.srt").write_text(
            "1\n00:00:00,000 --> 00:00:01,000\nHalo\n", encoding="utf-8"
        )
        fake_client = _FakeYoutubeClient()
        with mock.patch.dict(sys.modules, _stub_youtube_modules(fake_client)), \
             mock.patch.object(produce, "STATE_PATH", self.state_path):
            produce.upload(str(self.run_dir), privacy="unlisted", at=None)

        calls = fake_client.captions_resource.calls
        self.assertEqual(len(calls), 1, "captions().insert() harus dipanggil persis sekali")
        self.assertEqual(calls[0]["snippet"]["videoId"], "FAKE_VIDEO_ID")
        self.assertEqual(calls[0]["snippet"]["language"], "id")

    def test_tanpa_video_srt_tidak_memanggil_captions(self):
        fake_client = _FakeYoutubeClient()
        with mock.patch.dict(sys.modules, _stub_youtube_modules(fake_client)), \
             mock.patch.object(produce, "STATE_PATH", self.state_path):
            produce.upload(str(self.run_dir), privacy="unlisted", at=None)

        self.assertEqual(fake_client.captions_resource.calls, [],
                          "tanpa video.srt, captions().insert() tak boleh dipanggil")


if __name__ == "__main__":
    unittest.main()
