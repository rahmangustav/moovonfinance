"""Test permission file token.json di core/youtube_uploader.py & auth_headless.py.

Sebelum perbaikan, token.json (refresh_token + akses penuh scope upload/manage
channel YouTube) ditulis dengan permission default (umask sistem) -> bisa
world-readable, dan tidak pernah kedaluwarsa selama refresh_token valid.
Test ini mengunci kontrak: file token SELALU 0600 (hanya owner) setelah ditulis.

Modul google-auth di-stub di sys.modules supaya test tidak bergantung pada
paket eksternal terinstal/tidak rusak di lingkungan CI.
Jalankan: python -m unittest discover -s tests
"""
import stat
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _install_fake_google_modules():
    """Pasang stub minimal google-auth/google-api agar modul bisa di-import
    tanpa paket eksternal terinstal."""
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

    modules = {
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
    return modules


class TestTokenFilePermissions(unittest.TestCase):
    def setUp(self):
        self._fake_modules = _install_fake_google_modules()
        self._patched = {}
        for name, mod in self._fake_modules.items():
            self._patched[name] = sys.modules.get(name)
            sys.modules[name] = mod
        for mod in ("core.youtube_uploader", "auth_headless"):
            sys.modules.pop(mod, None)

    def tearDown(self):
        for name, old in self._patched.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
        for mod in ("core.youtube_uploader", "auth_headless"):
            sys.modules.pop(mod, None)

    def test_get_youtube_client_writes_token_as_owner_only(self):
        import core.youtube_uploader as yu

        with tempfile.TemporaryDirectory() as tmp:
            token_path = Path(tmp) / "token.json"
            with mock.patch.object(yu, "TOKEN_FILE", token_path):
                yu.get_youtube_client()

            self.assertTrue(token_path.exists())
            mode = stat.S_IMODE(token_path.stat().st_mode)
            self.assertEqual(
                mode, 0o600,
                f"token.json harus 0600 (owner-only), didapat {oct(mode)}",
            )

    def test_auth_headless_step2_writes_token_as_owner_only(self):
        fake_flow_module = types.ModuleType("google_auth_oauthlib.flow")

        class FakeFlow:
            code_verifier = "fake-verifier"

            @classmethod
            def from_client_secrets_file(cls, path, scopes, code_verifier=None):
                return cls()

            def fetch_token(self, code):
                pass

            @property
            def credentials(self):
                fake = mock.MagicMock()
                fake.to_json.return_value = '{"token": "fake"}'
                return fake

        fake_flow_module.Flow = FakeFlow
        sys.modules["google_auth_oauthlib.flow"] = fake_flow_module

        import auth_headless as ah

        with tempfile.TemporaryDirectory() as tmp:
            token_path = Path(tmp) / "token.json"
            pending_path = Path(tmp) / ".oauth_pending.json"
            pending_path.write_text('{"code_verifier": "fake-verifier"}')
            with mock.patch.object(ah, "TOKEN_FILE", token_path), \
                 mock.patch.object(ah, "PENDING", pending_path):
                ah.step2_exchange("fake-code")

            self.assertTrue(token_path.exists())
            mode = stat.S_IMODE(token_path.stat().st_mode)
            self.assertEqual(
                mode, 0o600,
                f"token.json harus 0600 (owner-only), didapat {oct(mode)}",
            )


if __name__ == "__main__":
    unittest.main()
