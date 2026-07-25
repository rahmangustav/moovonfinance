"""
moovon_style.py — Sistem desain Moovon Finance untuk matplotlib.
FinanceViz AI · dipakai oleh semua script visualisasi di folder scripts/.

Import modul ini di setiap template, panggil apply_style() sekali,
lalu pakai COLORS, add_branding(), rupiah()/dollar() dan save_figure().
Semua aturan di CLAUDE.md sudah terkunci di sini.
"""
from __future__ import annotations

import datetime as _dt
import re as _re
import sys as _sys
from pathlib import Path

import matplotlib as _mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties
from matplotlib.ticker import FuncFormatter

# moovon_theme.py (di root proyek, satu level di atas core/) adalah SUMBER
# KEBENARAN warna (CLAUDE.md: "jangan hard-code warna ... di tempat lain").
# Tarik HEX dari sana alih-alih menyalin nilainya di sini, supaya kalau brand
# citron/sinyal up-down diubah di moovon_theme.py, chart matplotlib ikut
# berubah otomatis -- bukan diam-diam menyimpang dari slide PIL.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))
from moovon_theme import HEX as _THEME_HEX  # noqa: E402

# ─── 1. Palet warna v2.0 "SINYAL" — tema GELAP, senada slide on-brand ─────────
# Selaras dengan moovon_theme.py (latar hitam-hangat, aksen citron, sinyal
# hijau/merah/amber). Chart tampil sebagai kartu data GELAP di dalam video.
COLORS = {
    "background":  _THEME_HEX["bg"],         # hitam-hangat (= bg slide)
    "panel":       _THEME_HEX["panel"],      # kartu
    "panel_2":     _THEME_HEX["panel_2"],    # header tabel / kartu tumpuk
    "text":        _THEME_HEX["text"],       # ivory hangat
    "text_soft":   _THEME_HEX["text_soft"],  # sekunder
    "primary":     "#78A6C8",  # biru-debu — data utama / netral (chart-only, tak ada di moovon_theme)
    "positive":    _THEME_HEX["up"],         # hijau — profit / naik
    "negative":    _THEME_HEX["down"],       # merah — rugi / turun
    "benchmark":   "#3C443D",  # bar pembanding redup (chart-only, tak ada di moovon_theme)
    "accent":      _THEME_HEX["brand"],      # CITRON — highlight / header
    "gridline":    _THEME_HEX["line"],       # hairline
    "watermark":   _THEME_HEX["text_dim"],   # branding & sumber
}

# ─── Path proyek ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "output"
DATA_DIR     = PROJECT_ROOT / "data"

# ─── Output (1920x1080 @ 300 DPI) ─────────────────────────────────────────────
_DPI      = 300
FIGSIZE   = (1920 / _DPI, 1080 / _DPI)   # → tepat 1920x1080 px pada 300 DPI


_FONTS_DIR = PROJECT_ROOT / "fonts"


def _pick_font() -> str:
    """Daftarkan Archivo + JetBrains Mono (dari fonts/) ke matplotlib dan
    kembalikan nama family Archivo. Fallback ke sans default kalau folder
    fonts/ belum ada."""
    from matplotlib import font_manager
    fam = None
    for fn in ("Archivo-Regular.ttf", "Archivo-SemiBold.ttf", "Archivo-Black.ttf",
               "JetBrainsMono-Regular.ttf", "JetBrainsMono-Bold.ttf"):
        p = _FONTS_DIR / fn
        if p.exists():
            try:
                font_manager.fontManager.addfont(str(p))
                if fn == "Archivo-Regular.ttf":
                    fam = FontProperties(fname=str(p)).get_name()
            except Exception:
                pass
    return fam or "DejaVu Sans"


def apply_style() -> None:
    """Terapkan sistem desain Moovon Finance ke matplotlib. Panggil sekali di awal."""
    font = _pick_font()
    _mpl.rcParams.update({
        "figure.figsize":     FIGSIZE,
        "figure.dpi":         _DPI,
        "savefig.dpi":        _DPI,
        "figure.facecolor":   COLORS["background"],
        "axes.facecolor":     COLORS["background"],
        "savefig.facecolor":  COLORS["background"],

        "font.family":        font,
        "font.size":          11,
        "text.color":         COLORS["text"],
        "axes.labelcolor":    COLORS["text"],
        "axes.edgecolor":     COLORS["text"],
        "xtick.color":        COLORS["text"],
        "ytick.color":        COLORS["text"],

        # Judul rata kiri + bold
        "axes.titlelocation": "left",
        "axes.titleweight":   "bold",
        "axes.titlesize":     20,
        "axes.titlecolor":    COLORS["text"],
        "axes.titlepad":      16,

        # Hapus spines atas & kanan
        "axes.spines.top":    False,
        "axes.spines.right":  False,

        # Gridline horizontal tipis
        "axes.grid":          True,
        "axes.grid.axis":     "y",
        "grid.color":         COLORS["gridline"],
        "grid.linewidth":     0.8,
        "axes.axisbelow":     True,
    })


# ─── 2. Format angka ──────────────────────────────────────────────────────────
def rupiah(value: float, decimals: int = 0) -> str:
    """Format Rupiah: pemisah ribuan pakai titik, awali 'Rp'. Contoh: Rp1.250.000"""
    s = f"{value:,.{decimals}f}"                     # 1,250,000.00 (gaya en)
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")  # tukar ke gaya ID
    return f"Rp{s}"


def dollar(value: float, decimals: int = 0) -> str:
    """Format Dollar: pemisah ribuan pakai koma, awali '$'. Contoh: $1,250,000"""
    return f"${value:,.{decimals}f}"


def currency_axis(ax, currency: str = "rp", axis: str = "y", decimals: int = 0) -> None:
    """Pasang format mata uang pada sumbu (Rp/$ + pemisah ribuan). currency: 'rp'|'usd'."""
    fmt = rupiah if currency.lower() in ("rp", "idr", "rupiah") else dollar
    formatter = FuncFormatter(lambda v, _pos: fmt(v, decimals))
    target = ax.yaxis if axis == "y" else ax.xaxis
    target.set_major_formatter(formatter)


# ─── Judul (rata kiri, bold, auto-wrap agar tidak terpotong) ──────────────────
def add_title(fig, title: str, subtitle: str = "") -> None:
    """Judul bold rata kiri di level figure — otomatis wrap kalau kepanjangan.

    Dipakai menggantikan ax.set_title() supaya judul panjang tidak terpotong
    di tepi kanan (mis. pada donut chart dengan legend di kanan).
    """
    t = fig.text(0.045, 0.965, title, ha="left", va="top",
                 fontsize=20, fontweight="bold", color=COLORS["text"])
    t.set_wrap(True)
    if subtitle:
        fig.text(0.045, 0.905, subtitle, ha="left", va="top",
                 fontsize=12, color=COLORS["watermark"])


# ─── 3. Branding & sumber (WAJIB di setiap gambar) ────────────────────────────
def add_branding(fig, source: str = "", corner: str = "right") -> None:
    """Tempel watermark 'Moovon Finance' + 'Sumber: ...' di pojok bawah.

    corner: 'right' (pojok kanan bawah) atau 'left' (pojok kiri bawah).
    """
    x, ha = (0.985, "right") if corner == "right" else (0.015, "left")
    fig.text(x, 0.045, "Moovon Finance",
             ha=ha, va="bottom", fontsize=10, fontweight="bold",
             color=COLORS["watermark"])
    if source:
        fig.text(x, 0.018, f"Sumber: {source}",
                 ha=ha, va="bottom", fontsize=8,
                 color=COLORS["watermark"])


# ─── 4. Label data ────────────────────────────────────────────────────────────
def label_bars(ax, bars, fmt=str, offset: float = 0.0, color: str | None = None) -> None:
    """Tempel data label (angka pasti) di atas setiap bar. fmt: fungsi format angka."""
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            fmt(h),
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4 + offset), textcoords="offset points",
            ha="center", va="bottom", fontsize=9, fontweight="bold",
            color=color or COLORS["text"],
        )


# ─── 5. Simpan ────────────────────────────────────────────────────────────────
def _slugify(text: str) -> str:
    text = _re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return _re.sub(r"[\s_]+", "-", text) or "grafik"


def save_figure(fig, title: str) -> Path:
    """Simpan ke output/ dengan nama YYYY-MM-DD_judul-grafik.png (PNG @ 300 DPI)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date = _dt.date.today().isoformat()
    path = OUTPUT_DIR / f"{date}_{_slugify(title)}.png"
    fig.savefig(path, dpi=_DPI, bbox_inches=None, facecolor=COLORS["background"])
    print(f"✅ Tersimpan: {path}  (1920x1080 @ {_DPI} DPI)")
    return path
