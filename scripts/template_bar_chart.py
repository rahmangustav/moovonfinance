"""
template_bar_chart.py — Template grafik batang Moovon Finance.
FinanceViz AI

Cara pakai:
  1. Copy file ini, ganti nama sesuai topik.
  2. Ubah TITLE, SUBTITLE, SOURCE, dan data di bawah (atau load dari data/*.csv).
  3. Jalankan:  python scripts/template_bar_chart.py
  4. Hasil otomatis tersimpan di output/YYYY-MM-DD_judul-grafik.png

Semua aturan desain (warna, font, watermark, format angka, no-pie/no-3D,
data label, sumbu mata uang) sudah dijamin lewat modul moovon_style.
"""
import matplotlib.pyplot as plt

from moovon_style import (
    COLORS, apply_style, add_branding, add_title, save_figure,
    label_bars, rupiah, currency_axis,
)

# ─── Konfigurasi grafik ───────────────────────────────────────────────────────
TITLE    = "Laba Bersih BBCA per Kuartal 2024"
SUBTITLE = "Dalam miliar Rupiah"
SOURCE   = "Laporan Keuangan BCA 2024"
CURRENCY = "rp"          # 'rp' → titik ribuan + prefix Rp ; 'usd' → koma + $

# Data mentah (ganti / load dari data/xxx.csv)
labels = ["Q1", "Q2", "Q3", "Q4"]
values = [12_400, 13_100, 12_900, 14_500]   # miliar Rupiah


def main() -> None:
    apply_style()
    fig, ax = plt.subplots()

    # Warna per bar: hijau kalau naik dari sebelumnya, merah kalau turun,
    # bar pertama pakai biru netral (data utama).
    bar_colors = [COLORS["primary"]]
    for i in range(1, len(values)):
        bar_colors.append(COLORS["positive"] if values[i] >= values[i - 1]
                          else COLORS["negative"])

    bars = ax.bar(labels, values, color=bar_colors, width=0.62, zorder=3)

    # Judul rata kiri (bold besar, auto-wrap) + subtitle abu-abu
    add_title(fig, TITLE, SUBTITLE)

    # Sumbu Y sebagai mata uang, data label angka pasti di tiap bar
    currency_axis(ax, currency=CURRENCY)
    label_bars(bars=bars, ax=ax, fmt=lambda v: rupiah(v))

    ax.margins(y=0.15)
    ax.tick_params(axis="x", length=0)          # rapikan tick sumbu X

    add_branding(fig, source=SOURCE, corner="right")
    fig.tight_layout(rect=(0.01, 0.07, 0.99, 0.86))   # ruang untuk judul & branding
    save_figure(fig, TITLE)


if __name__ == "__main__":
    main()
