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
from pathlib import Path

import matplotlib as _mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties
from matplotlib.ticker import FuncFormatter

# ─── 1. Palet warna (WAJIB — hanya gunakan warna ini) ─────────────────────────
COLORS = {
    "background":  "#F9FAFB",  # abu-abu sangat muda
    "text":        "#1F2937",  # abu-abu gelap (bukan hitam pekat)
    "primary":     "#2563EB",  # Biru Royal — data utama / netral
    "positive":    "#10B981",  # Hijau Emerald — profit / pertumbuhan
    "negative":    "#EF4444",  # Merah Crimson — rugi / utang
    "benchmark":   "#D1D5DB",  # Abu-abu muda — data pembanding
    "accent":      "#F59E0B",  # Kuning Emas — highlight
    "gridline":    "#E5E7EB",
    "watermark":   "#6B7280",  # abu-abu untuk branding & sumber
}

# ─── Path proyek ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "output"
DATA_DIR     = PROJECT_ROOT / "data"

# ─── Output (1920x1080 @ 300 DPI) ─────────────────────────────────────────────
_DPI      = 300
FIGSIZE   = (1920 / _DPI, 1080 / _DPI)   # → tepat 1920x1080 px pada 300 DPI


def _pick_font() -> str:
    """Pilih font pertama yang tersedia: Inter → Helvetica → Arial → sans default."""
    for name in ("Inter", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"):
        try:
            if Path(findfont(FontProperties(family=name), fallback_to_default=False)).exists():
                return name
        except Exception:
            continue
    return "DejaVu Sans"  # selalu tersedia di matplotlib


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
