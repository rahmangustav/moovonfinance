"""Test unit untuk analyze_channel.py: parsing durasi ISO 8601 & klasifikasi Short.

Sebelum perbaikan ini, `is_short` di analyze_channel.py memakai heuristik string
kasar (`"S" in dur and "M" not in dur and "H" not in dur`, ambang < 1 menit) —
sudah tidak sesuai syarat Shorts YouTube saat ini (<= 3 menit, berlaku sejak
Okt 2024). Modul ini sebelumnya tidak punya test sama sekali. `analyze_channel`
mengimpor `core.youtube_uploader` di level modul (butuh paket `google-auth`),
jadi modul google di-stub dulu sebelum import — pola sama dengan
`test_youtube_uploader_token_perms.py`.
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
    requests_mod.Request = lambda: None

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


class AnalyzeChannelDurationTest(unittest.TestCase):
    def setUp(self):
        self._fake_modules = _install_fake_google_modules()
        self._patched = {}
        for name, mod in self._fake_modules.items():
            self._patched[name] = sys.modules.get(name)
            sys.modules[name] = mod
        for mod in ("core.youtube_uploader", "analyze_channel"):
            sys.modules.pop(mod, None)

        import analyze_channel as ac
        self.ac = ac

    def tearDown(self):
        for name, old in self._patched.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
        for mod in ("core.youtube_uploader", "analyze_channel"):
            sys.modules.pop(mod, None)

    def test_parse_seconds_only(self):
        self.assertEqual(self.ac.parse_duration_seconds("PT45S"), 45)

    def test_parse_minutes_only_no_seconds(self):
        self.assertEqual(self.ac.parse_duration_seconds("PT3M"), 180)

    def test_parse_minutes_and_seconds(self):
        self.assertEqual(self.ac.parse_duration_seconds("PT8M11S"), 491)

    def test_parse_hours_minutes_seconds(self):
        self.assertEqual(self.ac.parse_duration_seconds("PT1H2M3S"), 3723)

    def test_parse_hours_only(self):
        self.assertEqual(self.ac.parse_duration_seconds("PT10H"), 36000)

    def test_parse_unrecognized_format_returns_zero(self):
        self.assertEqual(self.ac.parse_duration_seconds("bukan-durasi"), 0)
        self.assertEqual(self.ac.parse_duration_seconds(""), 0)
        self.assertEqual(self.ac.parse_duration_seconds(None), 0)

    def test_is_short_59_seconds(self):
        self.assertTrue(self.ac.is_short("PT59S"))

    def test_is_short_exactly_3_minutes_is_short(self):
        # Regresi kunci: heuristik lama ("M" not in dur) mengklasifikasikan
        # "PT3M" sebagai video panjang — padahal 3 menit persis masih Short
        # sesuai aturan YouTube saat ini.
        self.assertTrue(self.ac.is_short("PT3M"))

    def test_is_short_2m30s_is_short(self):
        # Kasus lain yang salah di heuristik lama: durasi ber-"M" dan ber-"S"
        # sekaligus (mis. 2:30) dulu langsung gugur jadi LONG walau < 3 menit.
        self.assertTrue(self.ac.is_short("PT2M30S"))

    def test_is_short_over_3_minutes_is_long(self):
        self.assertFalse(self.ac.is_short("PT3M1S"))

    def test_is_short_long_video_is_long(self):
        self.assertFalse(self.ac.is_short("PT8M11S"))

    def test_is_short_unrecognized_duration_defaults_to_long(self):
        self.assertFalse(self.ac.is_short("bukan-durasi"))


if __name__ == "__main__":
    unittest.main()
