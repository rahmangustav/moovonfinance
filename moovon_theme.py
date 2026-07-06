"""
Moovon Finance — Design System v2.0 "SINYAL"

SUMBER KEBENARAN desain. Semua skrip render WAJIB tarik nilai dari sini —
jangan hard-code warna / ukuran / nama font di tempat lain.

Identitas v2.0: latar hitam-hangat, aksen CITRON, font Archivo + JetBrains Mono.
Sinyal warna: hijau = diskon/undervalue/naik, merah = premium/turun, amber = tahan.
"""
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).resolve().parent / "fonts"

# ─── Kanvas ───────────────────────────────────────────────────────────────────
WIDTH, HEIGHT       = 1920, 1080
MARGIN_X, MARGIN_Y  = 112, 92
SUPERSAMPLE         = 2          # render 2x lalu diperkecil LANCZOS (tepi bersih)

# ─── Warna ────────────────────────────────────────────────────────────────────
HEX = {
    "bg":        "#0F1311",   # latar hitam-hangat
    "panel":     "#181E1A",   # kartu
    "panel_2":   "#1F2621",   # kartu tumpuk / header tabel
    "line":      "#2C332E",   # hairline
    "text":      "#ECEDE3",   # ivory hangat — teks utama
    "text_soft": "#AAB2A5",   # sekunder
    "text_dim":  "#6F776C",   # tersier / caption
    "brand":     "#C6F24E",   # CITRON — aksen tanda tangan (furniture saja)
    "brand_dim": "#8CA63C",   # citron redup
    "up":        "#34D399",   # hijau — diskon / undervalue / naik
    "down":      "#EF6D6A",   # merah — premium / turun
    "neutral":   "#F5B740",   # amber — TAHAN
    "up_bg":     "#13291F",   # tint pita nilai wajar
    "black":     "#0A0D0B",   # teks di atas brand/citron
}


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


RGB = {name: _rgb(val) for name, val in HEX.items()}

# ─── Font ─────────────────────────────────────────────────────────────────────
# Archivo = judul & bodi (varian Expanded utk angka/judul hero).
# JetBrains Mono = SEMUA angka & ticker.
FONT_FILES = {
    "hero":      "ArchivoExp-Black.ttf",     # angka valuasi raksasa
    "hero_sub":  "ArchivoExp-SemiBold.ttf",  # sub-hero expanded
    "display":   "Archivo-Black.ttf",        # judul cover
    "title":     "Archivo-ExtraBold.ttf",    # judul section
    "semibold":  "Archivo-SemiBold.ttf",
    "medium":    "Archivo-Medium.ttf",
    "body":      "Archivo-Regular.ttf",
    "mono":      "JetBrainsMono-Bold.ttf",   # angka kunci
    "mono_semi": "JetBrainsMono-SemiBold.ttf",
    "mono_med":  "JetBrainsMono-Medium.ttf",
    "mono_reg":  "JetBrainsMono-Regular.ttf",  # ticker, status bar
}

SIZE = {
    "hero":        224,   # angka hero (harga / nilai wajar)
    "cover_title": 108,
    "title":        60,
    "section":      46,
    "lead":         40,
    "body":         34,
    "ticker":       30,
    "label":        26,
    "eyebrow":      25,
    "status":       23,
}


@lru_cache(maxsize=256)
def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    """Ambil font by peran (lihat FONT_FILES). `size` dalam piksel FINAL —
    saat render supersample, kalikan sendiri dengan SUPERSAMPLE."""
    return ImageFont.truetype(str(FONT_DIR / FONT_FILES[role]), size)


# ─── Kanvas supersample ───────────────────────────────────────────────────────
def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    """Kanvas 2x berlatar bg. Return (img, draw, S) — S = faktor skala; semua
    koordinat & ukuran font harus dikali S. Selesai render panggil finalize()."""
    S = SUPERSAMPLE
    img = Image.new("RGB", (WIDTH * S, HEIGHT * S), RGB["bg"])
    return img, ImageDraw.Draw(img), S


def finalize(img: Image.Image) -> Image.Image:
    """Perkecil ke 1920x1080 dengan LANCZOS."""
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    return img


# ─── Verdict (elemen tanda tangan — jangan tentukan manual) ───────────────────
MOS_BELI = 0.15   # margin of safety minimum untuk BELI


def verdict(price: float, fair: float) -> tuple[str, tuple[int, int, int], float]:
    """Tentukan verdict dari harga vs nilai wajar.
    Return (label, warna_RGB, margin_of_safety).
    Aturan: BELI hanya bila diskon (margin of safety) >= 15%.
            HINDARI bila harga di atas nilai wajar (premium).
            TAHAN selebihnya."""
    mos = (fair - price) / fair if fair else 0.0
    if mos >= MOS_BELI:
        return "BELI", RGB["up"], mos
    if mos < 0:
        return "HINDARI", RGB["down"], mos
    return "TAHAN", RGB["neutral"], mos


DISCLAIMER = (
    "Konten edukasi, bukan rekomendasi. Keputusan investasi & risikonya "
    "ada di tangan kamu sendiri."
)

BRAND_NAME = "MOOVON"
BRAND_SUB  = "FINANCE"
