"""
chart_templates.py — Mesin grafik Moovon Finance.
FinanceViz AI

Kumpulan fungsi siap pakai untuk memproduksi visual channel:
    line_chart, bar_chart, donut_chart, comparison_table, timeline_chart

Semua fungsi mematuhi CLAUDE.md lewat modul moovon_style (palet warna, font,
resolusi 1920x1080 @ 300 DPI, watermark "Moovon Finance" + "Sumber: ...").
Setiap fungsi menyimpan PNG ke output/YYYY-MM-DD_nama-file.png dan mengembalikan
path file tersebut.

Test cepat:  python scripts/chart_templates.py
"""
from __future__ import annotations

import datetime as _dt
import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Pastikan moovon_style bisa diimpor baik saat dijalankan langsung
# (python scripts/chart_templates.py) maupun sebagai modul dari root proyek.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from moovon_style import (  # noqa: E402
    COLORS, OUTPUT_DIR, apply_style, add_branding, add_title, _slugify,
)

# Palet berurutan untuk kategori (donut, dst) — sesuai CLAUDE.md.
SEQUENTIAL = [
    COLORS["primary"],    # Biru Royal
    COLORS["positive"],   # Hijau Emerald
    COLORS["accent"],     # Kuning Emas
    COLORS["benchmark"],  # Abu-abu muda
    COLORS["negative"],   # Merah Crimson
]


# ─── Util internal ────────────────────────────────────────────────────────────
def _num(v) -> str:
    """Format angka gaya Indonesia: pemisah ribuan titik. 12500 → '12.500'."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v == int(v):
        return f"{int(v):,}".replace(",", ".")
    # 1 desimal bila cukup, 2 desimal bila perlu (5,45 jangan jadi "5,5")
    dec = 1 if round(v, 1) == round(v, 2) else 2
    s = f"{v:,.{dec}f}"                                # gaya en: 1,234.56
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def _parse_num(text) -> float | None:
    """Ekstrak nilai numerik dari sel tabel (mendukung Rp/$/%/+/-/(...))."""
    t = str(text).strip()
    if not t:
        return None
    neg = False
    if t.startswith("(") and t.endswith(")"):          # notasi akuntansi (123)
        neg, t = True, t[1:-1]
    for sym in ("Rp", "rp", "$", "%", " "):
        t = t.replace(sym, "")
    if t[:1] in ("+", "-"):
        neg = neg or t[0] == "-"
        t = t[1:]
    if not t:
        return None
    if "," in t and "." in t:                          # 1.234,56 (ID)
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    else:
        parts = t.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            t = t.replace(".", "")                     # 1.234.567 → ribuan
    try:
        val = float(t)
    except ValueError:
        return None
    return -val if neg else val


# Folder output dapat di-override sementara (mis. oleh pipeline video yang
# menyimpan tiap chart ke folder run output/<timestamp>/). Lihat render_chart().
_OUTPUT_OVERRIDE: str | None = None


def _save(fig, nama_file: str) -> str:
    """Simpan ke <output>/YYYY-MM-DD_nama-file.png (PNG @ 300 DPI). Return path str."""
    out = Path(_OUTPUT_OVERRIDE) if _OUTPUT_OVERRIDE else OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    date = _dt.date.today().isoformat()
    path = out / f"{date}_{_slugify(nama_file)}.png"
    fig.savefig(path, dpi=300, facecolor=COLORS["background"])
    plt.close(fig)
    print(f"✅ Tersimpan: {path}")
    return str(path)


# ─── 1. Line chart ────────────────────────────────────────────────────────────
def line_chart(x, y_dict, judul, sumber, nama_file):
    """Grafik garis. Data pertama biru, sisanya abu-abu (garis dibedakan pola).
    Data label ditampilkan di titik terakhir tiap garis.
    """
    apply_style()
    fig, ax = plt.subplots()

    gray_dashes = ["--", ":", "-.", (0, (3, 1, 1, 1))]
    for name, vals in y_dict.items():
        if not vals:
            raise ValueError(f"line_chart: series {name!r} kosong (tidak ada data)")
    for i, (name, vals) in enumerate(y_dict.items()):
        if i == 0:
            color, lw, ls = COLORS["primary"], 3.0, "-"
        else:
            color, lw = COLORS["benchmark"], 2.4
            ls = gray_dashes[(i - 1) % len(gray_dashes)]
        ax.plot(x, vals, color=color, linewidth=lw, linestyle=ls,
                marker="o", markersize=5, label=name, zorder=3)
        # Data label di titik terakhir
        ax.annotate(_num(vals[-1]), xy=(x[-1], vals[-1]),
                    xytext=(9, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=10, fontweight="bold",
                    color=color, zorder=4)

    add_title(fig, judul)
    ax.set_xmargin(0.10)                                # ruang untuk label kanan
    ax.margins(y=0.12)
    ax.tick_params(axis="x", length=0)
    if len(y_dict) > 1:
        ax.legend(frameon=False, fontsize=11, labelcolor=COLORS["text"], loc="best")

    add_branding(fig, source=sumber, corner="right")
    fig.tight_layout(rect=(0.01, 0.07, 0.99, 0.86))
    return _save(fig, nama_file)


# ─── 2. Bar chart ─────────────────────────────────────────────────────────────
def bar_chart(kategori, nilai, judul, sumber, nama_file, horizontal=False):
    """Grafik batang. Hijau bila nilai positif, merah bila negatif.
    Angka pasti di atas batang (atau di samping bila horizontal).
    """
    apply_style()
    fig, ax = plt.subplots()

    colors = [COLORS["positive"] if v >= 0 else COLORS["negative"] for v in nilai]
    ax.grid(False)

    if horizontal:
        bars = ax.barh(kategori, nilai, color=colors, zorder=3)
        ax.xaxis.grid(True, color=COLORS["gridline"], linewidth=0.8)
        ax.invert_yaxis()                               # kategori pertama di atas
        ax.tick_params(axis="y", length=0)
        for bar, v in zip(bars, nilai):
            w = bar.get_width()
            ha = "left" if v >= 0 else "right"
            off = 5 if v >= 0 else -5
            ax.annotate(_num(v), xy=(w, bar.get_y() + bar.get_height() / 2),
                        xytext=(off, 0), textcoords="offset points",
                        va="center", ha=ha, fontsize=10, fontweight="bold",
                        color=COLORS["text"], zorder=4)
        ax.margins(x=0.14)
    else:
        bars = ax.bar(kategori, nilai, color=colors, width=0.62, zorder=3)
        ax.yaxis.grid(True, color=COLORS["gridline"], linewidth=0.8)
        ax.tick_params(axis="x", length=0)
        for bar, v in zip(bars, nilai):
            h = bar.get_height()
            va = "bottom" if v >= 0 else "top"
            off = 5 if v >= 0 else -5
            ax.annotate(_num(v), xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, off), textcoords="offset points",
                        ha="center", va=va, fontsize=10, fontweight="bold",
                        color=COLORS["text"], zorder=4)
        ax.margins(y=0.16)

    add_title(fig, judul)
    add_branding(fig, source=sumber, corner="right")
    fig.tight_layout(rect=(0.01, 0.07, 0.99, 0.86))
    return _save(fig, nama_file)


# ─── 3. Donut chart ───────────────────────────────────────────────────────────
def _donut_center_text(persentase) -> str:
    """Teks di tengah lubang donut: total persentase, SELALU diakhiri '%'.
    Angka bulat (mis. '100%') kalau totalnya ~100 atau kurang; format ID
    dengan desimal (mis. '100,4%') kalau total lebih dari 100 (data belum
    dinormalisasi/salah ketik riset)."""
    total = sum(persentase)
    if abs(total - 100) < 1e-6 or total <= 100:
        return f"{round(total)}%"
    return f"{_num(total)}%"


def donut_chart(labels, persentase, judul, sumber, nama_file):
    """Donut chart (pengganti pie). Warna berurutan dari palet CLAUDE.md.
    Total ditampilkan di tengah lubang donut.
    """
    apply_style()
    fig, ax = plt.subplots()

    colors = [SEQUENTIAL[i % len(SEQUENTIAL)] for i in range(len(labels))]
    wedges, _t, autotexts = ax.pie(
        persentase, colors=colors, startangle=90, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor=COLORS["background"], linewidth=3),
        autopct=lambda p: f"{p:.0f}%", pctdistance=0.79,
    )
    for t in autotexts:
        t.set_color(COLORS["background"])
        t.set_fontweight("bold")
        t.set_fontsize(11)

    center = _donut_center_text(persentase)
    ax.text(0, 0, center, ha="center", va="center",
            fontsize=22, fontweight="bold", color=COLORS["text"])

    add_title(fig, judul)
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=11, labelcolor=COLORS["text"])
    ax.set_aspect("equal")

    add_branding(fig, source=sumber, corner="left")
    fig.tight_layout(rect=(0.01, 0.07, 0.99, 0.86))
    return _save(fig, nama_file)


# ─── 4. Comparison table (gaya Bloomberg/Stripe) ──────────────────────────────
def comparison_table(headers, rows, judul, sumber, nama_file):
    """Tabel perbandingan bergaya Bloomberg/Stripe. Angka positif hijau,
    negatif merah. Kolom pertama diperlakukan sebagai label (rata kiri).
    """
    apply_style()
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    n_cols = len(headers)
    for r, row in enumerate(rows):
        if len(row) != n_cols:
            raise ValueError(
                f"comparison_table: baris ke-{r} punya {len(row)} kolom, "
                f"header punya {n_cols} kolom — jumlah harus sama"
            )
    n_rows = len(rows) + 1                              # + header
    x0, x1 = 0.035, 0.965
    weights = [1.7] + [1.0] * (n_cols - 1) if n_cols > 1 else [1.0]
    tot_w = sum(weights)
    edges = [x0]
    for w in weights:
        edges.append(edges[-1] + (x1 - x0) * w / tot_w)

    y_top, y_bot = 0.82, 0.14
    row_h = (y_top - y_bot) / n_rows
    pad = 0.012

    def _cell_x(col):
        return (edges[col] + pad, "left") if col == 0 else (edges[col + 1] - pad, "right")

    # Header band panel gelap, teks citron
    hy = y_top - row_h
    ax.add_patch(Rectangle((x0, hy), x1 - x0, row_h,
                           facecolor=COLORS["panel_2"], edgecolor="none", zorder=1))
    # Header panjang di-wrap agar tak menabrak kolom sebelahnya
    col_chars = [max(8, int(38 * w / tot_w * n_cols / 2)) for w in weights]
    for c, h in enumerate(headers):
        lx, ha = _cell_x(c)
        ax.text(lx, hy + row_h / 2, textwrap.fill(str(h), width=col_chars[c]),
                color=COLORS["accent"],
                fontweight="bold", fontsize=12.5, va="center", ha=ha, zorder=3)

    # Baris data (zebra striping tipis + warna angka)
    for r, row in enumerate(rows):
        ry = y_top - row_h * (r + 2)
        if r % 2 == 1:
            ax.add_patch(Rectangle((x0, ry), x1 - x0, row_h,
                                   facecolor=COLORS["gridline"], alpha=0.55,
                                   edgecolor="none", zorder=1))
        for c, cell in enumerate(row):
            lx, ha = _cell_x(c)
            if c == 0:
                color, weight = COLORS["text"], "bold"
            else:
                val = _parse_num(cell)
                if val is None:
                    color, weight = COLORS["text"], "normal"
                elif val > 0:
                    color, weight = COLORS["positive"], "bold"
                elif val < 0:
                    color, weight = COLORS["negative"], "bold"
                else:
                    color, weight = COLORS["text"], "normal"
            # Sel data di-wrap sesuai lebar kolomnya (seperti header) supaya teks
            # panjang di tabel >2 kolom tak meluber & bertabrakan dgn kolom sebelah.
            txt = textwrap.fill(str(cell), width=col_chars[c]) if n_cols > 2 else str(cell)
            ax.text(lx, ry + row_h / 2, txt, color=color,
                    fontweight=weight, fontsize=12, va="center", ha=ha, zorder=3)
        ax.plot([x0, x1], [ry, ry], color=COLORS["gridline"], lw=0.8, zorder=2)

    ax.plot([x0, x1], [hy, hy], color=COLORS["text"], lw=1.4, zorder=2)

    add_title(fig, judul)
    add_branding(fig, source=sumber, corner="right")
    return _save(fig, nama_file)


# ─── 5. Timeline chart ────────────────────────────────────────────────────────
def timeline_chart(events, dates, judul, sumber, nama_file):
    """Timeline peristiwa keuangan (krisis, regulasi, dsb). Label berselang
    di atas & bawah garis waktu agar tidak bertabrakan.
    """
    apply_style()
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    n = len(events)
    x0, x1 = 0.13, 0.87                                 # ruang tepi agar label tak terpotong
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)] if n > 1 else [(x0 + x1) / 2]
    baseline = 0.44                                     # agak turun agar tak tabrak judul

    ax.plot([x0, x1], [baseline, baseline], color=COLORS["primary"],
            lw=3, solid_capstyle="round", zorder=2)

    for i, (ev, dt, x) in enumerate(zip(events, dates, xs)):
        up = i % 2 == 0
        stem_y = baseline + (0.14 if up else -0.14)
        va = "bottom" if up else "top"
        ax.plot([x, x], [baseline, stem_y], color=COLORS["benchmark"], lw=1.6, zorder=2)
        ax.scatter([x], [baseline], s=190, color=COLORS["accent"],
                   edgecolor=COLORS["background"], linewidth=2, zorder=4)
        ax.text(x, stem_y + (0.02 if up else -0.02), str(dt), ha="center", va=va,
                fontsize=13, fontweight="bold", color=COLORS["primary"], zorder=5)
        ax.text(x, stem_y + (0.075 if up else -0.075),
                textwrap.fill(str(ev), width=14), ha="center", va=va,
                fontsize=10, color=COLORS["text"], zorder=5)

    add_title(fig, judul)
    add_branding(fig, source=sumber, corner="right")
    return _save(fig, nama_file)


# ─── Dispatcher untuk pipeline (render dari spec dict) ────────────────────────
_DISPATCH = {
    "line":     lambda s: line_chart(s["x"], s["y_dict"], s["judul"], s.get("sumber", ""), s["nama_file"]),
    "bar":      lambda s: bar_chart(s["kategori"], s["nilai"], s["judul"], s.get("sumber", ""), s["nama_file"], bool(s.get("horizontal", False))),
    "donut":    lambda s: donut_chart(s["labels"], s["persentase"], s["judul"], s.get("sumber", ""), s["nama_file"]),
    "table":    lambda s: comparison_table(s["headers"], s["rows"], s["judul"], s.get("sumber", ""), s["nama_file"]),
    "timeline": lambda s: timeline_chart(s["events"], s["dates"], s["judul"], s.get("sumber", ""), s["nama_file"]),
}


def render_chart(spec: dict, out_dir=None) -> str | None:
    """Render satu chart dari spec dict ke folder out_dir (default: output/).

    spec wajib punya 'type' (line|bar|donut|table|timeline), 'judul', dan
    field data sesuai fungsinya. 'sumber' & 'nama_file' opsional. Mengembalikan
    path PNG, atau None bila tipe tak dikenal / data kurang / render gagal.
    Aman dipanggil pipeline — tidak melempar exception.
    """
    global _OUTPUT_OVERRIDE
    spec = dict(spec)
    fn = _DISPATCH.get(str(spec.get("type", "")).strip().lower())
    if fn is None:
        print(f"   ⚠️  Tipe chart tak dikenal: {spec.get('type')!r}")
        return None
    spec.setdefault("nama_file", _slugify(spec.get("judul", "chart")))
    _OUTPUT_OVERRIDE = str(out_dir) if out_dir else None
    try:
        return fn(spec)
    except (KeyError, ValueError, TypeError, IndexError) as e:
        print(f"   ⚠️  Chart '{spec.get('type')}' gagal dirender: {e}")
        return None
    finally:
        _OUTPUT_OVERRIDE = None


# ─── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🎬 Demo chart_templates.py — Moovon Finance\n")

    line_chart(
        x=["2020", "2021", "2022", "2023", "2024"],
        y_dict={"IHSG": [5979, 6581, 6851, 7273, 7580],
                "Emas (indeks)": [5000, 5400, 5600, 6100, 6900]},
        judul="Kinerja IHSG vs Emas 2020–2024",
        sumber="BEI & Antam",
        nama_file="line-ihsg-vs-emas",
    )

    bar_chart(
        kategori=["BBCA", "BBRI", "BMRI", "TLKM", "ASII"],
        nilai=[18.5, 12.3, 9.8, -4.2, -1.5],
        judul="Return Saham Blue Chip YTD 2024 (%)",
        sumber="RTI Business",
        nama_file="bar-return-bluechip",
    )

    bar_chart(
        kategori=["Properti", "Teknologi", "Energi", "Konsumsi", "Perbankan"],
        nilai=[7.1, -3.4, 11.9, 4.2, 6.0],
        judul="Pertumbuhan Sektor (%)",
        sumber="Bloomberg",
        nama_file="bar-sektor-horizontal",
        horizontal=True,
    )

    donut_chart(
        labels=["Saham Blue Chip", "Obligasi", "Reksa Dana", "Emas"],
        persentase=[45, 25, 20, 10],
        judul="Alokasi Portofolio Ideal Investor Pemula",
        sumber="Riset Internal Moovon Finance",
        nama_file="donut-alokasi-portofolio",
    )

    comparison_table(
        headers=["Emiten", "Harga", "PER", "Div. Yield", "YTD"],
        rows=[
            ["BBCA", "Rp10.250", "24.1", "2.1%", "+18.5%"],
            ["BBRI", "Rp4.680", "12.7", "6.3%", "+12.3%"],
            ["TLKM", "Rp2.910", "13.5", "5.4%", "-4.2%"],
            ["ASII", "Rp4.520", "8.9", "10.2%", "-1.5%"],
        ],
        judul="Perbandingan Saham Blue Chip Indonesia",
        sumber="RTI Business, per 30 Jun 2024",
        nama_file="tabel-perbandingan-bluechip",
    )

    timeline_chart(
        events=["Krisis Moneter Asia", "Krisis Finansial Global",
                "Taper Tantrum", "Pandemi COVID-19", "Kenaikan Suku Bunga The Fed"],
        dates=["1998", "2008", "2013", "2020", "2022"],
        judul="Timeline Krisis Ekonomi & Dampaknya ke Pasar",
        sumber="Kompilasi Moovon Finance",
        nama_file="timeline-krisis-ekonomi",
    )

    print("\n✨ Semua demo selesai. Cek folder output/.")
