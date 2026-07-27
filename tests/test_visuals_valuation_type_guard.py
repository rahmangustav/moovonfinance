"""Test guard TIPE DATA harga/nilai_wajar di dict valuation yang diterima
create_video() (core/visuals.py).

Bug yang dites: blok `## VALUATION:` di draft ditulis manual sebagai JSON.
Kalau salah ketik menaruh tanda kutip di angka (mis. `{"harga": "9800", ...}`
alih-alih `{"harga": 9800, ...}` — kesalahan yang gampang terjadi karena
JSON tidak membedakan visualnya di editor teks biasa), nilai itu jadi str,
bukan int/float. create_video() (dan cek_draft.py sebelum perbaikan ini)
tidak pernah memvalidasi TIPE datanya — hanya keberadaannya (lihat PR
terpisah untuk KeyError field hilang). Nilai string itu diteruskan apa
adanya ke moovon_theme.verdict(), yang melakukan `fair - price` — operasi
aritmetika pada dua string meledak:

    TypeError: unsupported operand type(s) for -: 'str' and 'str'

...di tengah create_video(), SETELAH TTS ~10 menit selesai. Sekarang
divalidasi di awal create_video() (sebelum AudioFileClip/slide apa pun
disentuh) dengan pesan Bahasa Indonesia yang jelas.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.visuals import create_video


class ValuationTypeGuardTest(unittest.TestCase):
    def test_harga_berupa_string_ditolak_cepat(self):
        with self.assertRaises(ValueError) as cm:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"harga": "9800", "nilai_wajar": 9150},
            )
        pesan = str(cm.exception)
        self.assertIn("harga", pesan)
        self.assertIn("'9800'", pesan)

    def test_nilai_wajar_berupa_string_ditolak_cepat(self):
        with self.assertRaises(ValueError) as cm:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"harga": 9800, "nilai_wajar": "9150"},
            )
        self.assertIn("nilai_wajar", str(cm.exception))

    def test_bool_ditolak_juga_walau_subclass_int(self):
        # isinstance(True, int) True di Python -- jangan ikut lolos begitu
        # saja kalau draft khilaf menulis `true`/`false` alih-alih angka.
        with self.assertRaises(ValueError) as cm:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"harga": True, "nilai_wajar": 9150},
            )
        self.assertIn("harga", str(cm.exception))

    def test_valuation_numerik_tidak_ditolak_di_guard_ini(self):
        try:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation={"harga": 9800, "nilai_wajar": 9150},
            )
        except ValueError as e:
            self.assertNotIn("blok ## VALUATION:", str(e))
        except Exception:
            pass  # gagal di tahap lain (mis. AudioFileClip) — bukan tanggung jawab guard ini

    def test_valuation_none_tidak_ditolak(self):
        try:
            create_video(
                "BBCA: Judul", "[HOOK]isi[VALUASI]isi",
                "tidak_ada.mp3", "out/video.mp4",
                valuation=None,
            )
        except ValueError as e:
            self.assertNotIn("blok ## VALUATION:", str(e))
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
