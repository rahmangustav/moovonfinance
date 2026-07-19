"""Test unit untuk moovon_theme.py — SUMBER KEBENARAN desain.

verdict() adalah elemen paling kritis: menentukan label BELI/TAHAN/HINDARI
yang tayang di setiap video publik (gauge Margin of Safety). Kalau logikanya
salah, video menyiarkan rekomendasi investasi yang keliru — jadi wajib
dites lepas dari rendering/PIL.
"""
import sys
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


# ─── verdict() ──────────────────────────────────────────────────────────────

def test_verdict_beli_saat_diskon_besar():
    label, color, mos = verdict(price=8500, fair=10000)
    assert label == "BELI"
    assert color == RGB["up"]
    assert mos == pytest.approx(0.15)


def test_verdict_beli_diskon_jauh_lebih_besar():
    label, color, mos = verdict(price=5000, fair=10000)
    assert label == "BELI"
    assert color == RGB["up"]
    assert mos == pytest.approx(0.5)


def test_verdict_tahan_diskon_di_bawah_ambang_belum_beli():
    # mos = 0.10, di bawah MOS_BELI (0.15) -> harus TAHAN, bukan BELI
    label, color, mos = verdict(price=9000, fair=10000)
    assert label == "TAHAN"
    assert color == RGB["neutral"]
    assert mos == pytest.approx(0.10)


def test_verdict_boundary_tepat_di_ambang_mos_beli():
    # mos persis == MOS_BELI harus lolos sebagai BELI (aturan >=, bukan >)
    price = 8500.0
    fair = 10000.0
    assert (fair - price) / fair == pytest.approx(MOS_BELI)
    label, _, _ = verdict(price=price, fair=fair)
    assert label == "BELI"


def test_verdict_boundary_sedikit_di_bawah_ambang_masih_tahan():
    label, _, mos = verdict(price=8501, fair=10000)
    assert mos < MOS_BELI
    assert label == "TAHAN"


def test_verdict_hindari_saat_harga_di_atas_nilai_wajar():
    label, color, mos = verdict(price=11000, fair=10000)
    assert label == "HINDARI"
    assert color == RGB["down"]
    assert mos < 0


def test_verdict_harga_sama_dengan_nilai_wajar_adalah_tahan():
    # mos == 0 pas: bukan diskon (belum BELI) tapi juga bukan premium (bukan HINDARI)
    label, color, mos = verdict(price=10000, fair=10000)
    assert label == "TAHAN"
    assert color == RGB["neutral"]
    assert mos == 0.0


def test_verdict_fair_nol_tidak_crash_dan_jatuh_ke_tahan():
    # Pembagian dengan nol dihindari via `if fair else 0.0` — tidak boleh raise
    label, color, mos = verdict(price=100, fair=0)
    assert mos == 0.0
    assert label == "TAHAN"
    assert color == RGB["neutral"]


def test_verdict_return_shape_selalu_tiga_elemen():
    result = verdict(price=100, fair=200)
    assert len(result) == 3
    label, color, mos = result
    assert isinstance(label, str)
    assert isinstance(color, tuple) and len(color) == 3
    assert isinstance(mos, float)


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
