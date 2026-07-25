"""Test backfill_audio_lang.main() saat channels().list(mine=True) kosong.

Skenario nyata: docstring file ini menyuruh user hapus config/token.json dan
login ulang saat scope token kurang. Kalau di alur re-auth headless user
salah pilih akun Google (banyak akun login bersamaan di HP) atau memakai akun
yang belum punya channel YouTube, `channels().list(mine=True)` mengembalikan
{"items": []} -- respons API valid, bukan error -- dan kode sebelumnya
langsung IndexError di ch["items"][0]. analyze_channel.py sudah punya guard
untuk kasus identik; test ini mengunci guard yang sama di backfill_audio_lang.
Jalankan: python -m unittest discover -s tests
"""
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _install_fake_google_modules():
    """Stub minimal google-auth/google-api supaya modul bisa di-import tanpa
    paket eksternal (cryptography lewat google-auth rusak di sandbox CI ini,
    lihat test_youtube_uploader_token_perms.py untuk pola yang sama)."""
    google = types.ModuleType("google")
    google.__path__ = []

    oauth2 = types.ModuleType("google.oauth2")
    oauth2.__path__ = []
    credentials_mod = types.ModuleType("google.oauth2.credentials")

    class FakeCredentials:
        def __init__(self, valid=True):
            self.valid = valid
            self.expired = False
            self.refresh_token = None

        @classmethod
        def from_authorized_user_file(cls, path, scopes):
            return cls(valid=True)

        def to_json(self):
            return '{"token": "fake"}'

        def refresh(self, request):
            self.valid = True

    credentials_mod.Credentials = FakeCredentials

    oauthlib = types.ModuleType("google_auth_oauthlib")
    oauthlib.__path__ = []
    flow_mod = types.ModuleType("google_auth_oauthlib.flow")

    class FakeInstalledAppFlow:
        @classmethod
        def from_client_secrets_file(cls, path, scopes):
            return cls()

        def run_local_server(self, port=0):
            return credentials_mod.Credentials(valid=True)

    flow_mod.InstalledAppFlow = FakeInstalledAppFlow

    auth_mod = types.ModuleType("google.auth")
    auth_mod.__path__ = []
    transport_mod = types.ModuleType("google.auth.transport")
    transport_mod.__path__ = []
    requests_mod = types.ModuleType("google.auth.transport.requests")
    requests_mod.Request = lambda: None

    googleapiclient = types.ModuleType("googleapiclient")
    googleapiclient.__path__ = []
    discovery_mod = types.ModuleType("googleapiclient.discovery")
    discovery_mod.build = lambda *a, **k: mock.MagicMock()

    return {
        "google": google,
        "google.oauth2": oauth2,
        "google.oauth2.credentials": credentials_mod,
        "google_auth_oauthlib": oauthlib,
        "google_auth_oauthlib.flow": flow_mod,
        "google.auth": auth_mod,
        "google.auth.transport": transport_mod,
        "google.auth.transport.requests": requests_mod,
        "googleapiclient": googleapiclient,
        "googleapiclient.discovery": discovery_mod,
    }


class BackfillEmptyChannelTest(unittest.TestCase):
    def setUp(self):
        self._fake_modules = _install_fake_google_modules()
        self._patched = {}
        for name, mod in self._fake_modules.items():
            self._patched[name] = sys.modules.get(name)
            sys.modules[name] = mod
        for mod in ("youtube_uploader", "backfill_audio_lang"):
            sys.modules.pop(mod, None)

        import backfill_audio_lang as bal
        self.bal = bal

    def tearDown(self):
        for name, old in self._patched.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
        for mod in ("youtube_uploader", "backfill_audio_lang"):
            sys.modules.pop(mod, None)

    def test_channel_kosong_tidak_crash_dan_tidak_lanjut(self):
        bal = self.bal
        fake_yt = mock.MagicMock()
        fake_yt.channels.return_value.list.return_value.execute.return_value = {"items": []}

        with mock.patch.object(bal, "get_youtube_client", return_value=fake_yt):
            try:
                bal.main()
            except IndexError:
                self.fail("main() harus berhenti rapi, bukan IndexError mentah")

        fake_yt.playlistItems.assert_not_called()

    def test_channel_ada_tetap_lanjut_ambil_playlist(self):
        bal = self.bal
        fake_yt = mock.MagicMock()
        fake_yt.channels.return_value.list.return_value.execute.return_value = {
            "items": [{"contentDetails": {"relatedPlaylists": {"uploads": "PLxyz"}}}]
        }
        fake_yt.playlistItems.return_value.list.return_value.execute.return_value = {
            "items": [], "nextPageToken": None,
        }
        fake_yt.videos.return_value.list.return_value.execute.return_value = {"items": []}

        with mock.patch.object(bal, "get_youtube_client", return_value=fake_yt):
            bal.main()

        fake_yt.playlistItems.return_value.list.assert_called_with(
            part="contentDetails", playlistId="PLxyz", maxResults=50, pageToken=None,
        )


if __name__ == "__main__":
    unittest.main()
