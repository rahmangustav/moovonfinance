"""Test unit untuk moovon_theme.py — SUMBER KEBENARAN desain.

verdict() adalah elemen paling kritis: menentukan label BELI/TAHAN/HINDARI
yang tayang di setiap video publik (gauge Margin of Safety). Kalau logikanya
salah, video menyiarkan rekomendasi investasi yang keliru — jadi wajib
dites lepas dari rendering/PIL. Cakupan verdict() ada di VerdictTest di
bawah; sisanya (_rgb/RGB, new_canvas/finalize, font) memakai gaya pytest.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from moovon_theme import (
    RGB,
    HEX,
    WIDTH,
    HEIGHT,
    SUPERSAMPLE,
    MOS_BELI,
    FONT_FILES,
    _rgb,
    verdict,
    new_canvas,
    finalize,
    font,
)


class VerdictTest(unittest.TestCase):
    def test_beli_saat_diskon_besar(self):
        # harga 5800 vs nilai wajar 9150 -> margin of safety ~36.6%, jauh di atas 15%
        label, color, mos = verdict(5800, 9150)
        self.assertEqual(label, "BELI")
        self.assertEqual(color, RGB["up"])
        self.assertAlmostEqual(mos, (9150 - 5800) / 9150)

    def test_tahan_saat_diskon_di_bawah_ambang(self):
        # margin of safety 12.57% < 15% -> harus TAHAN, bukan BELI
        label, color, mos = verdict(8000, 9150)
        self.assertLess(mos, MOS_BELI)
        self.assertEqual(label, "TAHAN")
        self.assertEqual(color, RGB["neutral"])

    def test_tahan_saat_harga_sama_nilai_wajar(self):
        label, color, mos = verdict(9150, 9150)
        self.assertEqual(mos, 0.0)
        self.assertEqual(label, "TAHAN")

    def test_hindari_saat_harga_di_atas_nilai_wajar(self):
        label, color, mos = verdict(10000, 9150)
        self.assertLess(mos, 0)
        self.assertEqual(label, "HINDARI")
        self.assertEqual(color, RGB["down"])

    def test_batas_tepat_15_persen_masuk_beli(self):
        # aturan CLAUDE.md: "BELI hanya bila margin of safety >= 15%" -> batas
        # inklusif, harus dites tepat di angka 0.15 (bukan cuma di atas/bawahnya)
        price, fair = 850, 1000  # mos == 0.15 persis
        label, _, mos = verdict(price, fair)
        self.assertEqual(mos, 0.15)
        self.assertEqual(label, "BELI")

    def test_nilai_wajar_nol_tidak_membagi_nol(self):
        # guard di verdict(): `if fair else 0.0` — pastikan tidak ZeroDivisionError
        label, _, mos = verdict(100, 0)
        self.assertEqual(mos, 0.0)
        self.assertEqual(label, "TAHAN")

    def test_harga_nilai_wajar_berbentuk_teks_angka_tetap_jalan(self):
        # draft naskah ditulis manual manusia — "5800"/"9150" berkutip (typo
        # umum) sebelumnya bikin TypeError str - str, harus tetap jalan sama
        # seperti versi angka (int/float).
        label, color, mos = verdict("5800", "9150")
        self.assertEqual(label, "BELI")
        self.assertEqual(color, RGB["up"])
        self.assertAlmostEqual(mos, (9150 - 5800) / 9150)

    def test_harga_atau_nilai_wajar_bukan_angka_raise_valueerror_jelas(self):
        # bukan traceback TypeError mentah di tengah render — pesan jelas
        # menyebut nilai mentah supaya penulis draft tahu apa yang salah.
        with self.assertRaises(ValueError):
            verdict("abc", 9150)
        with self.assertRaises(ValueError):
            verdict(5800, "xyz")


# ─── _rgb() / RGB ───────────────────────────────────────────────────────────

def test_rgb_konversi_hex_dengan_pagar():
    assert _rgb("#0F1311") == (15, 19, 17)


def test_rgb_konversi_hex_tanpa_pagar():
    assert _rgb("C6F24E") == (198, 242, 78)


def test_rgb_hitam_dan_putih():
    assert _rgb("#000000") == (0, 0, 0)
    assert _rgb("#FFFFFF") == (255, 255, 255)


def test_rgb_dict_mencakup_semua_key_hex():
    assert set(RGB.keys()) == set(HEX.keys())
    for name, hexval in HEX.items():
        assert RGB[name] == _rgb(hexval)


def test_rgb_signal_up_down_neutral_berbeda():
    # Sinyal warna tidak boleh bentrok satu sama lain (dipakai bedakan BELI/HINDARI/TAHAN)
    assert RGB["up"] != RGB["down"]
    assert RGB["up"] != RGB["neutral"]
    assert RGB["down"] != RGB["neutral"]


# ─── new_canvas() / finalize() ─────────────────────────────────────────────

def test_new_canvas_ukuran_sesuai_supersample():
    img, draw, s = new_canvas()
    assert s == SUPERSAMPLE
    assert img.size == (WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE)


def test_new_canvas_latar_warna_bg():
    img, _, _ = new_canvas()
    assert img.getpixel((0, 0)) == RGB["bg"]


def test_finalize_perkecil_ke_ukuran_final():
    img, _, _ = new_canvas()
    out = finalize(img)
    assert out.size == (WIDTH, HEIGHT)


def test_finalize_idempoten_saat_sudah_ukuran_final():
    from PIL import Image
    img = Image.new("RGB", (WIDTH, HEIGHT), RGB["bg"])
    out = finalize(img)
    assert out.size == (WIDTH, HEIGHT)
    assert out is img


# ─── font() ─────────────────────────────────────────────────────────────────

def test_font_role_tidak_dikenal_raise_keyerror():
    with pytest.raises(KeyError):
        font("role-tidak-ada", 40)


def test_font_semua_role_termuat():
    for role in FONT_FILES:
        f = font(role, 32)
        assert f.size == 32


def test_font_cache_return_objek_sama_untuk_argumen_sama():
    a = font("body", 34)
    b = font("body", 34)
    assert a is b


if __name__ == "__main__":
    unittest.main()
