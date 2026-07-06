"""
core/slides.py — Render slide Moovon Finance (PIL) sesuai sistem desain.

SEMUA nilai visual diambil dari moovon_theme.py (sumber kebenaran). Modul ini
tidak boleh hard-code warna/ukuran/font. Lihat moovon-finance-slide-system.html
untuk referensi visual manusia.

Isi saat ini: chrome bersama (background, brandbar, statusbar, eyebrow) +
2 template penentu (Cover, Valuasi+Gauge). Template lain menyusul.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import moovon_theme as T

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
W, H = T.WIDTH, T.HEIGHT
MX, MY = T.MARGIN_X, T.MARGIN_Y


# ─── Font ───────────────────────────────────────────────────────────────────
_font_cache: dict = {}


def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    key = (role, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONT_DIR / T.FONT_FILES[role]), size)
    return _font_cache[key]


# ─── Teks dengan tracking (letter-spacing, tak ada bawaan di PIL) ────────────
def _tracked_width(draw, text, fnt, tracking_em) -> float:
    extra = tracking_em * fnt.size
    return sum(draw.textlength(c, font=fnt) for c in text) + extra * max(len(text) - 1, 0)


def tracked(draw, xy, text, fnt, fill, tracking_em=0.0, anchor="lm", center_w=None):
    """Gambar teks dengan jarak antar-huruf. anchor vertikal pakai 'm' (tengah)."""
    x, y = xy
    extra = tracking_em * fnt.size
    if center_w is not None:  # rata tengah dalam lebar center_w mulai dari x
        x = x + (center_w - _tracked_width(draw, text, fnt, tracking_em)) / 2
    va = anchor[1] if len(anchor) == 2 else "m"
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill, anchor="l" + va)
        x += draw.textlength(c, font=fnt) + extra
    return x - extra


# ─── Background ─────────────────────────────────────────────────────────────
def _base() -> Image.Image:
    img = Image.new("RGB", (W, H), T.RGB["navy_900"])
    # Glow radial halus di kanan-atas (navy lebih terang)
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = 0.82 * W, -0.18 * H
    d = np.hypot(xx - cx, yy - cy) / (0.62 * W)
    glow = np.clip(1 - d, 0, 1) ** 1.6
    base = np.array(img, dtype=np.float32)
    tint = np.array([16, 36, 60], dtype=np.float32)
    for k in range(3):
        base[..., k] += (tint[k] - base[..., k]) * glow * 0.55
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    # Motif grid sangat halus
    draw = ImageDraw.Draw(img)
    step = int(5.55 / 100 * W)  # 5.55cqw
    grid = tuple(min(255, c + 7) for c in T.RGB["navy_900"])
    for gx in range(0, W, step):
        draw.line([(gx, 0), (gx, H)], fill=grid, width=1)
    for gy in range(0, H, step):
        draw.line([(0, gy), (W, gy)], fill=grid, width=1)
    return img


# ─── Logo mark (kotak gold + glyph garis naik) ──────────────────────────────
def _logo_mark(img, x, y, s):
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x, y, x + s, y + s], radius=int(s * 0.22), fill=T.RGB["gold"])
    ink = T.RGB["navy_950"]
    # path zigzag naik (mengikuti SVG logo): titik dinormalkan 0..1 dalam kotak
    pts = [(0.25, 0.68), (0.41, 0.48), (0.55, 0.59), (0.75, 0.30)]
    px = [(x + a * s, y + b * s) for a, b in pts]
    draw.line(px, fill=ink, width=max(2, int(s * 0.07)), joint="curve")
    r = s * 0.07
    ex, ey = px[-1]
    draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=ink)


# ─── Brandbar (logo kiri, ticker kanan) ─────────────────────────────────────
def brandbar(img, ticker: str | None = None):
    draw = ImageDraw.Draw(img)
    s = 60
    top = MY - 6
    _logo_mark(img, MX, top, s)
    tx = MX + s + 26
    cy = top + s / 2
    wm = font("display_bold", T.SIZE["cover_title"] // 3)  # ~34
    wsub = font("mono_regular", T.SIZE["label"])
    # "MOOVON" gold + " Finance" ivory pada baris atas
    draw.text((tx, cy - 12), T.BRAND_NAME, font=wm, fill=T.RGB["gold"], anchor="lm")
    wlen = draw.textlength(T.BRAND_NAME, font=wm)
    draw.text((tx + wlen + 10, cy - 12), T.BRAND_SUB, font=wm, fill=T.RGB["ivory"], anchor="lm")
    tracked(draw, (tx, cy + 22), T.BRAND_TAGLINE, wsub, T.RGB["slate"], tracking_em=0.30)
    # Ticker tag kanan-atas
    if ticker:
        f = font("mono_regular", T.SIZE["ticker"])
        pad_x, pad_y = 22, 14
        tw = _tracked_width(draw, ticker, f, 0.12)
        bx1 = W - MX
        bx0 = bx1 - tw - pad_x * 2
        by0 = top + 4
        by1 = by0 + f.size + pad_y * 2
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=11,
                               fill=(18, 34, 53), outline=T.RGB["navy_700"], width=1)
        tracked(draw, (bx0 + pad_x, (by0 + by1) / 2), ticker, f, T.RGB["gold"], tracking_em=0.12)


# ─── Statusbar bawah (gaya terminal) ────────────────────────────────────────
def statusbar(img, left: str, right: str = ""):
    draw = ImageDraw.Draw(img)
    y = H - T.STATUSBAR_H
    draw.line([(0, y), (W, y)], fill=T.RGB["navy_700"], width=1)
    f = font("mono_regular", T.SIZE["status"])
    cy = y + T.STATUSBAR_H / 2
    # bullet gold + teks kiri
    draw.text((MX, cy), "●", font=f, fill=T.RGB["gold"], anchor="lm")
    bw = draw.textlength("●  ", font=f)
    tracked(draw, (MX + bw, cy), left, f, T.RGB["slate"], tracking_em=0.10)
    if right:
        rw = _tracked_width(draw, right, f, 0.10)
        tracked(draw, (W - MX - rw, cy), right, f, T.RGB["slate"], tracking_em=0.10)


# ─── Eyebrow (garis + label gold mono) ──────────────────────────────────────
def eyebrow(img, x, y, text: str):
    draw = ImageDraw.Draw(img)
    line_w = 46
    draw.line([(x, y), (x + line_w, y)], fill=T.RGB["gold"], width=2)
    f = font("mono_regular", T.SIZE["eyebrow"])
    tracked(draw, (x + line_w + 18, y), text.upper(), f, T.RGB["gold"], tracking_em=0.28)


# ─── Panel/kartu ────────────────────────────────────────────────────────────
def panel(draw, box, radius=16):
    draw.rounded_rectangle(box, radius=radius,
                           fill=T.RGB["navy_800"], outline=T.RGB["navy_700"], width=1)


# ═══════════════════════════════════════════════════════════════════════════
# TEMPLATE: COVER
# ═══════════════════════════════════════════════════════════════════════════
def render_cover(eyebrow_text, title_lines, sub, meta, ticker="",
                 status_left="MOOVON FINANCE", status_right=""):
    """
    title_lines: list baris; tiap baris = list of (teks, is_highlight).
    meta: list of (label, value).
    """
    img = _base()
    brandbar(img, ticker)
    statusbar(img, status_left, status_right)
    draw = ImageDraw.Draw(img)

    # Blok tengah
    title_f = font("display_bold", T.SIZE["cover_title"])
    line_h = int(T.SIZE["cover_title"] * 1.02)
    n = len(title_lines)
    block_h = n * line_h + 40 + T.SIZE["cover_sub"] + 3
    y = (H - block_h) // 2 - 20

    eyebrow(img, MX, y - 46, eyebrow_text)

    for line in title_lines:
        x = MX
        for text, hl in line:
            color = T.RGB["gold"] if hl else T.RGB["ivory"]
            draw.text((x, y), text, font=title_f, fill=color, anchor="lt")
            x += draw.textlength(text, font=title_f)
        y += line_h
    y += 26

    sub_f = font("display_regular", T.SIZE["cover_sub"])
    draw.text((MX, y), sub, font=sub_f, fill=T.RGB["ivory_dim"], anchor="lt")
    y += T.SIZE["cover_sub"] + 60

    # Meta kolom
    mx = MX
    kf = font("mono_regular", T.SIZE["ticker"])
    vf = font("display_medium", int(T.SIZE["cover_sub"] * 0.74))
    for label, value in meta:
        tracked(draw, (mx, y), label.upper(), kf, T.RGB["slate"], tracking_em=0.12, anchor="lt")
        draw.text((mx, y + 30), value, font=vf, fill=T.RGB["ivory"], anchor="lt")
        col_w = max(draw.textlength(value, font=vf),
                    _tracked_width(draw, label.upper(), kf, 0.12))
        mx += col_w + 70
    return img


# ═══════════════════════════════════════════════════════════════════════════
# TEMPLATE: VALUASI + GAUGE MARGIN OF SAFETY (elemen tanda tangan)
# ═══════════════════════════════════════════════════════════════════════════
def render_valuation(price, fair_value, low, high, ticker="VALUASI"):
    img = _base()
    brandbar(img, ticker)
    v = T.verdict(price, fair_value)
    statusbar(img, "KEPUTUSAN VALUASI",
              f"DISKON {abs(v['discount'])*100:.0f}%" if v["discount"] >= 0
              else f"PREMIUM {abs(v['discount'])*100:.0f}%")
    draw = ImageDraw.Draw(img)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # Eyebrow + judul
    top_y = MY + 70
    eyebrow(img, MX, top_y, "Harga vs Nilai Wajar")
    draw.text((MX, top_y + 24), "Margin of Safety",
              font=font("display_bold", T.SIZE["section_title"]), fill=T.RGB["ivory"], anchor="lt")

    # Layout dua kolom
    body_top, body_bot = top_y + 130, H - T.STATUSBAR_H - 70
    gap = 58
    left_w = int((1.35 / 2.35) * (W - 2 * MX - gap))
    right_x = MX + left_w + gap
    right_w = W - MX - right_x
    cy = (body_top + body_bot) // 2

    # ── Kolom kiri: gauge ──
    gx0, gx1 = MX, MX + left_w
    bar_h = 104
    bar_y0 = cy - bar_h // 2
    bar_y1 = cy + bar_h // 2
    span = high - low
    def px(val):
        return gx0 + max(0.0, min(1.0, (val - low) / span)) * (gx1 - gx0)

    # legend atas
    lf = font("mono_regular", T.SIZE["label"])
    draw.text((gx0, bar_y0 - 42), T.rupiah(low) if hasattr(T, "rupiah") else f"Rp {int(low):,}".replace(",", "."),
              font=lf, fill=T.RGB["slate"], anchor="lm")
    tracked(draw, ((gx0 + gx1) / 2 - 70, bar_y0 - 42), "ZONA NILAI WAJAR", lf, T.RGB["up"], tracking_em=0.1)
    hi_txt = f"Rp {int(high):,}".replace(",", ".")
    draw.text((gx1, bar_y0 - 42), hi_txt, font=lf, fill=T.RGB["slate"], anchor="rm")

    # bar dasar
    panel(draw, [gx0, bar_y0, gx1, bar_y1], radius=18)

    # pita nilai wajar (±5%)
    fair_lo, fair_hi = px(fair_value * 0.95), px(fair_value * 1.05)
    od.rounded_rectangle([fair_lo, bar_y0, fair_hi, bar_y1], radius=6, fill=(76, 183, 130, 40))
    for xd in (fair_lo, fair_hi):
        od.line([(xd, bar_y0), (xd, bar_y1)], fill=(76, 183, 130, 130), width=2)

    # arsiran diskon (dari harga ke wajar)
    px_price, px_fair = px(price), px(fair_value)
    lo_h, hi_h = sorted((px_price, px_fair))
    stripe = 26
    xh = lo_h
    while xh < hi_h:
        od.line([(xh, bar_y1), (min(xh + stripe // 2, hi_h), bar_y0)],
                fill=(76, 183, 130, 55), width=6)
        xh += stripe

    # label WAJAR
    draw.text((px_fair + 8, bar_y0 + 20), f"WAJAR ≈ {int(round(fair_value)):,}".replace(",", "."),
              font=font("mono_regular", T.SIZE["label"]), fill=T.RGB["up"], anchor="lm")

    # marker harga (garis gold + flag)
    od.line([(px_price, bar_y0 - 12), (px_price, bar_y1 + 12)], fill=(223, 184, 99, 255), width=6)
    flag = f"HARGA {int(round(price)):,}".replace(",", ".")
    ff = font("mono_semibold", T.SIZE["label"])
    fw = draw.textlength(flag, font=ff)
    fpx0, fpx1 = px_price - fw / 2 - 14, px_price + fw / 2 + 14
    fpy1 = bar_y0 - 20
    fpy0 = fpy1 - (ff.size + 16)
    od.rounded_rectangle([fpx0, fpy0, fpx1, fpy1], radius=8, fill=(223, 184, 99, 255))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text(((fpx0 + fpx1) / 2, (fpy0 + fpy1) / 2), flag, font=ff, fill=T.RGB["navy_950"], anchor="mm")

    # teks margin of safety
    mos_f = font("mono_regular", int(T.SIZE["label"] * 1.15))
    my0 = bar_y1 + 46
    seg1 = "Diskon terhadap nilai wajar: "
    draw.text((gx0, my0), seg1, font=mos_f, fill=T.RGB["ivory_dim"], anchor="lm")
    w1 = draw.textlength(seg1, font=mos_f)
    pct = f"≈ {abs(v['discount'])*100:.0f}%"
    draw.text((gx0 + w1, my0), pct, font=font("mono_semibold", int(T.SIZE["label"] * 1.15)),
              fill=T.RGB["up"] if v["discount"] >= 0 else T.RGB["down"], anchor="lm")

    # ── Kolom kanan: dua kartu + verdict ──
    card_h = 118
    card_gap = 22
    verdict_h = 96
    total = card_h * 2 + verdict_h + card_gap * 2
    ry = cy - total // 2
    for label, value in [("Nilai Wajar (est.)", fair_value), ("Harga Sekarang", price)]:
        panel(draw, [right_x, ry, right_x + right_w, ry + card_h], radius=14)
        tracked(draw, (right_x + 28, ry + 38), label.upper(),
                font("mono_regular", T.SIZE["label"]), T.RGB["slate"], tracking_em=0.12)
        draw.text((right_x + 28, ry + 78), f"{int(round(value)):,}".replace(",", "."),
                  font=font("mono_semibold", int(T.SIZE["metric_value"] * 0.74)),
                  fill=T.RGB["ivory"], anchor="lm")
        ry += card_h + card_gap

    # verdict badge
    vb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vbd = ImageDraw.Draw(vb)
    col = v["color"]
    vbd.rounded_rectangle([right_x, ry, right_x + right_w, ry + verdict_h], radius=14,
                          fill=col + (36,), outline=col + (150,), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), vb).convert("RGB")
    draw = ImageDraw.Draw(img)
    vf = font("mono_semibold", T.SIZE["verdict"] + 8)
    vcy = ry + verdict_h / 2
    tw = _tracked_width(draw, v["label"], vf, 0.14) + 34
    sx = right_x + (right_w - tw) / 2
    draw.ellipse([sx, vcy - 9, sx + 18, vcy + 9], fill=col)
    tracked(draw, (sx + 34, vcy), v["label"], vf, col, tracking_em=0.14)
    return img


# ─── Demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/design_preview")
    out.mkdir(parents=True, exist_ok=True)

    cover = render_cover(
        eyebrow_text="Analisis Valuasi",
        title_lines=[[("Apakah ", False), ("BBRI", True)], [("Masih Murah?", False)]],
        sub="Menghitung nilai wajar Bank Rakyat Indonesia dan mencari margin of safety untuk horizon 5–10 tahun.",
        meta=[("Ticker", "BBRI · IDX"), ("Sektor", "Perbankan"), ("Durasi", "12 menit")],
        ticker="EPISODE 042",
        status_right="IHSG 7.240 ▲   WIB 20:00",
    )
    cover.save(out / "cover.png")

    val = render_valuation(price=4720, fair_value=5900, low=3500, high=6500)
    val.save(out / "valuation.png")
    print("Saved:", out / "cover.png", "|", out / "valuation.png")
