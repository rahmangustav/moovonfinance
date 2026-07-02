"""
template_donut_chart.py — Template Donut Chart Moovon Finance.
FinanceViz AI

Pengganti Pie Chart (Pie Chart DILARANG di sistem desain). Dipakai untuk
komposisi/porsi: alokasi portofolio, pangsa pasar, struktur pendapatan, dll.

Cara pakai:
  1. Copy file ini, ganti TITLE, SOURCE, dan data.
  2. Jalankan:  python scripts/template_donut_chart.py
"""
import matplotlib.pyplot as plt

from moovon_style import (
    COLORS, apply_style, add_branding, add_title, save_figure,
)

TITLE  = "Alokasi Portofolio Ideal Investor Pemula"
SOURCE = "Riset Internal Moovon Finance"

# Data komposisi (label, persentase). Total sebaiknya 100.
labels = ["Saham Blue Chip", "Obligasi", "Reksa Dana Pasar Uang", "Emas"]
values = [45, 25, 20, 10]

# Urutan warna dari palet (data utama → highlight → pembanding)
SLICE_COLORS = [COLORS["primary"], COLORS["positive"],
                COLORS["accent"], COLORS["benchmark"]]


def main() -> None:
    apply_style()
    fig, ax = plt.subplots()

    wedges, _texts, autotexts = ax.pie(
        values,
        colors=SLICE_COLORS[:len(values)],
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor=COLORS["background"], linewidth=3),
        autopct=lambda p: f"{p:.0f}%",           # data label angka pasti
        pctdistance=0.79,
    )
    for t in autotexts:
        t.set_color(COLORS["background"])
        t.set_fontweight("bold")
        t.set_fontsize(11)

    # Total di tengah donut
    ax.text(0, 0, "100%", ha="center", va="center",
            fontsize=22, fontweight="bold", color=COLORS["text"])

    add_title(fig, TITLE)
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=11, labelcolor=COLORS["text"])
    ax.set_aspect("equal")

    add_branding(fig, source=SOURCE, corner="left")
    fig.tight_layout(rect=(0.01, 0.07, 0.99, 0.86))
    save_figure(fig, TITLE)


if __name__ == "__main__":
    main()
