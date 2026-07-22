"""Test logika murni cleanup_offniche.py (classify_target, build_unlist_body).

Skrip ini mengubah privacyStatus video PUBLIK di channel asli (unlist) —
tanpa test, salah baca status bisa berarti video yang seharusnya tetap
publik ikut ter-unlist, atau sebaliknya video off-niche gagal ke-unlist.

cleanup_offniche.py mengimpor core.youtube_uploader di level modul, yang
butuh paket google-auth/google-api-python-client. Paket itu tidak selalu
terpasang di lingkungan CI/dev, jadi modul google di-stub minimal di
sys.modules sebelum impor (pola yang sama dipakai test lain di repo ini).
"""
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _install_fake_google_modules():
    google = types.ModuleType("google")
    google.__path__ = []
    oauth2 = types.ModuleType("google.oauth2")
    oauth2.__path__ = []
    credentials_mod = types.ModuleType("google.oauth2.credentials")
    credentials_mod.Credentials = object

    oauthlib = types.ModuleType("google_auth_oauthlib")
    oauthlib.__path__ = []
    flow_mod = types.ModuleType("google_auth_oauthlib.flow")
    flow_mod.InstalledAppFlow = object

    auth_mod = types.ModuleType("google.auth")
    auth_mod.__path__ = []
    transport_mod = types.ModuleType("google.auth.transport")
    transport_mod.__path__ = []
    requests_mod = types.ModuleType("google.auth.transport.requests")
    requests_mod.Request = object

    googleapiclient = types.ModuleType("googleapiclient")
    googleapiclient.__path__ = []
    discovery_mod = types.ModuleType("googleapiclient.discovery")
    discovery_mod.build = lambda *a, **k: None

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


class TestCleanupOffniche(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._patched = {}
        for name, mod in _install_fake_google_modules().items():
            cls._patched[name] = sys.modules.get(name)
            sys.modules[name] = mod
        sys.modules.pop("cleanup_offniche", None)
        sys.modules.pop("core.youtube_uploader", None)
        import cleanup_offniche as co
        cls.co = co

    @classmethod
    def tearDownClass(cls):
        for name, old in cls._patched.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
        sys.modules.pop("cleanup_offniche", None)
        sys.modules.pop("core.youtube_uploader", None)

    def _video(self, privacy="public", **status_extra):
        status = {"privacyStatus": privacy, **status_extra}
        return {"id": "vid1", "snippet": {"title": "Judul"}, "status": status}

    # --- classify_target ---------------------------------------------------

    def test_keep_set_takes_priority_even_if_present_in_info(self):
        v = self._video()
        action, video = self.co.classify_target("vid1", {"vid1": v}, {"vid1"})
        self.assertEqual(action, "keep")
        self.assertIsNone(video)

    def test_missing_when_not_in_info(self):
        action, video = self.co.classify_target("ghost", {}, set())
        self.assertEqual(action, "missing")
        self.assertIsNone(video)

    def test_skip_when_already_unlisted(self):
        v = self._video(privacy="unlisted")
        action, video = self.co.classify_target("vid1", {"vid1": v}, set())
        self.assertEqual(action, "skip")
        self.assertIs(video, v)

    def test_skip_when_private(self):
        v = self._video(privacy="private")
        action, video = self.co.classify_target("vid1", {"vid1": v}, set())
        self.assertEqual(action, "skip")

    def test_unlist_when_public(self):
        v = self._video(privacy="public")
        action, video = self.co.classify_target("vid1", {"vid1": v}, set())
        self.assertEqual(action, "unlist")
        self.assertIs(video, v)

    # --- build_unlist_body ---------------------------------------------------

    def test_build_unlist_body_sets_privacy_and_preserves_fields(self):
        status = {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,
            "embeddable": False,
            "publicStatsViewable": False,
            "license": "creativeCommon",
        }
        body = self.co.build_unlist_body("vid1", status)
        self.assertEqual(body["id"], "vid1")
        self.assertEqual(body["status"]["privacyStatus"], "unlisted")
        self.assertTrue(body["status"]["selfDeclaredMadeForKids"])
        self.assertFalse(body["status"]["embeddable"])
        self.assertFalse(body["status"]["publicStatsViewable"])
        self.assertEqual(body["status"]["license"], "creativeCommon")

    def test_build_unlist_body_defaults_missing_optional_fields(self):
        body = self.co.build_unlist_body("vid1", {"privacyStatus": "public"})
        self.assertEqual(body["status"]["privacyStatus"], "unlisted")
        self.assertFalse(body["status"]["selfDeclaredMadeForKids"])
        self.assertTrue(body["status"]["embeddable"])
        self.assertTrue(body["status"]["publicStatsViewable"])
        self.assertEqual(body["status"]["license"], "youtube")


if __name__ == "__main__":
    unittest.main()
