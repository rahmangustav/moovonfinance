"""
render_slides.py — contoh render slide on-brand Moovon Finance v2.0 "SINYAL".

Pola acuan untuk slide baru. SELALU tarik nilai dari moovon_theme.py; jangan
hard-code warna/font/ukuran. Render di kanvas supersample 2x lalu finalize().

Jalankan langsung untuk bikin 3 slide contoh ke output/design_preview/:
    python render_slides.py
"""
from pathlib import Path
import moovon_theme as T
from PIL import ImageDraw

OUT = Path(__file__).resolve().parent / "output" / "design_preview"


# ─── util angka (format Indonesia) ────────────────────────────────────────────
def fmt_rp(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")


def fmt_pct(v: float, plus: bool = False) -> str:
    s = f"{abs(v) * 100:.1f}".replace(".", ",")
    sign = "-" if v < 0 else ("+" if plus else "")
    return f"{sign}{s}%"


def _wrap(d: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    """Bungkus teks per kata sesuai lebar piksel maksimum."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


# ─── chrome bersama (logo, ticker, status bar) ────────────────────────────────
def _logo(d: ImageDraw.ImageDraw, S: int, x: int, y: int):
    """Mark sinyal citron + wordmark MOOVON FINANCE. y = baseline tengah mark."""
    m = 40 * S
    d.rounded_rectangle([x, y, x + m, y + m], radius=10 * S, fill=T.RGB["brand"])
    # tiga bar sinyal naik (hitam) di dalam mark
    bw = m * 0.16
    gap = m * 0.10
    x0 = x + m * 0.22
    base = y + m * 0.76
    for i, hh in enumerate((0.28, 0.46, 0.66)):
        bx = x0 + i * (bw + gap)
        d.rounded_rectangle([bx, base - m * hh, bx + bw, base],
                            radius=2 * S, fill=T.RGB["black"])
    tx = x + m + 20 * S
    cy = y + m / 2
    f = T.font("title", 30 * S)
    d.text((tx, cy), T.BRAND_NAME, font=f, fill=T.RGB["text"], anchor="lm")
    w = d.textlength(T.BRAND_NAME, font=f)
    d.text((tx + w + 10 * S, cy), T.BRAND_SUB, font=f, fill=T.RGB["brand"], anchor="lm")


def _ticker_capsule(d: ImageDraw.ImageDraw, S: int, ticker: str):
    """Kapsul outline citron di kanan-atas: 'IDX : BBCA'."""
    f = T.font("mono_semi", T.SIZE["ticker"] * S)
    label = f"IDX : {ticker}"
    tw = d.textlength(label, font=f)
    padx, padh = 24 * S, 44 * S
    x1 = T.WIDTH * S - T.MARGIN_X * S
    x0 = x1 - tw - padx * 2
    y0 = T.MARGIN_Y * S - 2 * S
    d.rounded_rectangle([x0, y0, x1, y0 + padh], radius=padh // 2,
                        outline=T.RGB["brand"], width=max(2, 2 * S))
    d.text(((x0 + x1) / 2, y0 + padh / 2), label, font=f,
           fill=T.RGB["brand"], anchor="mm")


def _statusbar(d: ImageDraw.ImageDraw, S: int, left: str, right: str):
    y = (T.HEIGHT - 58) * S
    d.line([(T.MARGIN_X * S, y), ((T.WIDTH - T.MARGIN_X) * S, y)],
           fill=T.RGB["line"], width=max(1, S))
    f = T.font("mono_reg", T.SIZE["status"] * S)
    cy = y + 30 * S
    d.text((T.MARGIN_X * S, cy), "●", font=f, fill=T.RGB["brand"], anchor="lm")
    bw = d.textlength("●  ", font=f)
    d.text((T.MARGIN_X * S + bw, cy), left, font=f, fill=T.RGB["text_dim"], anchor="lm")
    d.text(((T.WIDTH - T.MARGIN_X) * S, cy), right, font=f,
           fill=T.RGB["text_dim"], anchor="rm")


def _eyebrow(d: ImageDraw.ImageDraw, S: int, x: int, y: int, text: str):
    d.line([(x, y), (x + 46 * S, y)], fill=T.RGB["brand"], width=max(2, 2 * S))
    f = T.font("mono_semi", T.SIZE["eyebrow"] * S)
    # letter-spacing manual
    tx = x + 60 * S
    for ch in text.upper():
        d.text((tx, y), ch, font=f, fill=T.RGB["brand"], anchor="lm")
        tx += d.textlength(ch, font=f) + 5 * S


def _chrome(d, S, ticker, status_left="MOOVON FINANCE // ANALISIS SAHAM", status_right=""):
    _logo(d, S, T.MARGIN_X * S, (T.MARGIN_Y - 6) * S)
    if ticker:
        _ticker_capsule(d, S, ticker)
    _statusbar(d, S, status_left, status_right)


# ─── SLIDE: COVER ─────────────────────────────────────────────────────────────
def render_cover(eyebrow, title, ticker, subtitle, tanggal):
    """`title` boleh string panjang — font judul auto-fit ke <=3 baris."""
    img, d, S = T.new_canvas()
    _chrome(d, S, ticker, status_right=tanggal)
    x = T.MARGIN_X * S
    _eyebrow(d, S, x, 330 * S, eyebrow)

    maxw = (T.WIDTH - 2 * T.MARGIN_X) * S
    for px in (T.SIZE["cover_title"], 94, 82, 72, 64):
        f = T.font("display", px * S)
        lines = _wrap(d, title, f, maxw)
        if len(lines) <= 3:
            break
    lh = int(px * 1.06) * S
    y = 384 * S
    for line in lines:
        d.text((x, y), line, font=f, fill=T.RGB["text"], anchor="lt")
        y += lh
    d.rectangle([x, y + 10 * S, x + 120 * S, y + 16 * S], fill=T.RGB["brand"])
    y += 52 * S
    fs = T.font("medium", T.SIZE["lead"] * S)
    for line in _wrap(d, subtitle, fs, int(maxw * 0.8))[:2]:
        d.text((x, y), line, font=fs, fill=T.RGB["text_soft"], anchor="lt")
        y += int(T.SIZE["lead"] * 1.35) * S
    return T.finalize(img)


# ─── SLIDE: SECTION NARATIF (satu ide, tanpa foto) ───────────────────────────
def render_section(index, total, judul, lead, ticker, eyebrow="Analisis"):
    """`judul` kosong -> mode 'statement': lead ditampilkan besar sebagai
    kutipan (dipakai slide hook, biar tak duplikat judul + lead)."""
    img, d, S = T.new_canvas()
    _chrome(d, S, ticker, status_right=f"{index:02d} / {total:02d}")
    x = T.MARGIN_X * S
    content_w = (T.WIDTH - 2 * T.MARGIN_X) * S

    # angka indeks raksasa sebagai watermark kanan-bawah (kedalaman, bukan foto)
    fg = T.font("hero", 460 * S)
    d.text(((T.WIDTH - T.MARGIN_X + 30) * S, (T.HEIGHT - 40) * S), f"{index:02d}",
           font=fg, fill=T.RGB["panel_2"], anchor="rs")

    _eyebrow(d, S, x, 296 * S, eyebrow)

    if judul:
        ft = T.font("title", T.SIZE["title"] * S)
        y = 344 * S
        for ln in _wrap(d, judul, ft, content_w):
            d.text((x, y), ln, font=ft, fill=T.RGB["text"], anchor="lt")
            y += int(T.SIZE["title"] * 1.12) * S
        d.rectangle([x, y + 10 * S, x + 110 * S, y + 16 * S], fill=T.RGB["brand"])
        y += 56 * S
        fl = T.font("body", T.SIZE["lead"] * S)
        for ln in _wrap(d, lead, fl, int(content_w * 0.80))[:6]:
            d.text((x, y), ln, font=fl, fill=T.RGB["text_soft"], anchor="lt")
            y += int(T.SIZE["lead"] * 1.4) * S
    else:
        # statement / kutipan besar
        fq = T.font("semibold", 58 * S)
        y = 372 * S
        for ln in _wrap(d, lead, fq, int(content_w * 0.86))[:6]:
            d.text((x, y), ln, font=fq, fill=T.RGB["text"], anchor="lt")
            y += int(58 * 1.34) * S
    return T.finalize(img)


# ─── SLIDE: PENUTUP / CTA ────────────────────────────────────────────────────
def render_closing(ticker, headline="Terima kasih sudah nonton."):
    img, d, S = T.new_canvas()
    _chrome(d, S, ticker, status_right="PENUTUP")
    x = T.MARGIN_X * S
    _eyebrow(d, S, x, 320 * S, "Moovon Finance")

    ft = T.font("display", 84 * S)
    y = 372 * S
    for ln in _wrap(d, headline, ft, (T.WIDTH - 2 * T.MARGIN_X) * S):
        d.text((x, y), ln, font=ft, fill=T.RGB["text"], anchor="lt")
        y += int(84 * 1.06) * S
    y += 24 * S

    # kartu CTA subscribe
    cta = "Subscribe & nyalakan lonceng  →  analisis saham berikutnya."
    fc = T.font("semibold", T.SIZE["lead"] * S)
    tw = d.textlength(cta, font=fc)
    padx, padh = 40 * S, 84 * S
    d.rounded_rectangle([x, y, x + tw + padx * 2, y + padh], radius=padh // 2,
                        fill=T.RGB["brand"])
    d.text((x + padx, y + padh / 2), cta, font=fc, fill=T.RGB["black"], anchor="lm")

    # disclaimer
    fd = T.font("body", T.SIZE["body"] * S)
    dy = (T.HEIGHT - 200) * S
    for ln in _wrap(d, T.DISCLAIMER, fd, int((T.WIDTH - 2 * T.MARGIN_X) * S * 0.72)):
        d.text((x, dy), ln, font=fd, fill=T.RGB["text_dim"], anchor="lt")
        dy += int(T.SIZE["body"] * 1.35) * S
    return T.finalize(img)


# ─── SLIDE: VALUASI + GAUGE MARGIN OF SAFETY ─────────────────────────────────
def render_valuation(ticker, harga, nilai_wajar, catatan=""):
    try:
        harga, nilai_wajar = float(harga), float(nilai_wajar)
    except (TypeError, ValueError):
        raise ValueError(
            f"harga/nilai_wajar harus angka untuk {ticker or 'ticker kosong'}, "
            f"dapat harga={harga!r} nilai_wajar={nilai_wajar!r} — "
            "cek blok ## VALUATION: di draft."
        )
    if nilai_wajar <= 0:
        raise ValueError(
            f"nilai_wajar harus > 0 untuk {ticker or 'ticker kosong'}, "
            f"dapat {nilai_wajar!r} — cek blok ## VALUATION: di draft."
        )
    img, d, S = T.new_canvas()
    _chrome(d, S, ticker, status_right="VALUASI")
    label, vcolor, mos = T.verdict(harga, nilai_wajar)
    x = T.MARGIN_X * S
    _eyebrow(d, S, x, 300 * S, "Margin of Safety")

    # dua angka hero: Harga vs Nilai Wajar
    def hero_block(hx, cap, val, col):
        fc = T.font("mono_med", T.SIZE["label"] * S)
        d.text((hx, 350 * S), cap, font=fc, fill=T.RGB["text_dim"], anchor="lt")
        fh = T.font("hero", 132 * S)
        d.text((hx, 384 * S), fmt_rp(val), font=fh, fill=col, anchor="lt")

    hero_block(x, "HARGA SEKARANG", harga, T.RGB["text"])
    hero_block((T.WIDTH // 2 + 40) * S, "NILAI WAJAR (EST.)", nilai_wajar, T.RGB["brand"])

    # ── gauge track ──
    gx0, gx1 = x, (T.WIDTH - T.MARGIN_X) * S
    gy = 660 * S
    gh = 26 * S
    lo, hi = nilai_wajar * 0.5, nilai_wajar * 1.15
    def X(v):
        return gx0 + (gx1 - gx0) * (min(max(v, lo), hi) - lo) / (hi - lo)

    # track dasar
    d.rounded_rectangle([gx0, gy, gx1, gy + gh], radius=gh // 2, fill=T.RGB["panel_2"])
    # pita nilai wajar (zona hijau) ±5%
    zx0, zx1 = X(nilai_wajar * 0.95), X(nilai_wajar * 1.05)
    d.rounded_rectangle([zx0, gy, zx1, gy + gh], radius=gh // 2, fill=T.RGB["up"])
    # arsiran citron = besarnya diskon (harga -> nilai wajar)
    if harga < nilai_wajar:
        hx0, hx1 = X(harga), X(nilai_wajar)
        step = 16 * S
        d.rectangle([hx0, gy, hx1, gy + gh], fill=T.RGB["up_bg"])
        xx = hx0 - gh
        while xx < hx1:
            d.line([(max(xx, hx0), gy + gh), (max(xx + gh, hx0), gy)],
                   fill=T.RGB["brand_dim"], width=max(1, 2 * S))
            xx += step
        d.rectangle([hx0, gy, hx0 + 2 * S, gy + gh], fill=T.RGB["brand"])
    # pin harga (citron, segitiga + garis)
    px = X(harga)
    d.rectangle([px - 2 * S, gy - 14 * S, px + 2 * S, gy + gh + 14 * S], fill=T.RGB["brand"])
    d.polygon([(px - 12 * S, gy - 14 * S), (px + 12 * S, gy - 14 * S), (px, gy + 2 * S)],
              fill=T.RGB["brand"])
    # label di bawah track
    fl = T.font("mono_med", T.SIZE["label"] * S)
    d.text((X(nilai_wajar), gy + gh + 22 * S), "NILAI WAJAR", font=fl,
           fill=T.RGB["up"], anchor="mt")
    d.text((px, gy - 30 * S), "HARGA", font=fl, fill=T.RGB["brand"], anchor="mb")

    # ── kartu verdict (kanan bawah) ──
    cw, ch = 520 * S, 150 * S
    cx1, cyy = (T.WIDTH - T.MARGIN_X) * S, 800 * S
    cx0 = cx1 - cw
    d.rounded_rectangle([cx0, cyy, cx1, cyy + ch], radius=18 * S,
                        fill=T.RGB["panel"], outline=T.RGB["line"], width=max(1, S))
    d.rounded_rectangle([cx0, cyy, cx0 + 10 * S, cyy + ch], radius=0, fill=vcolor)
    fv = T.font("hero_sub", 68 * S)
    d.text((cx0 + 44 * S, cyy + ch / 2), label, font=fv, fill=vcolor, anchor="lm")
    fm = T.font("mono", T.SIZE["body"] * S)
    d.text((cx1 - 34 * S, cyy + ch / 2 - 20 * S), fmt_pct(mos, plus=True),
           font=fm, fill=vcolor, anchor="rm")
    d.text((cx1 - 34 * S, cyy + ch / 2 + 26 * S), "margin of safety",
           font=T.font("mono_reg", T.SIZE["status"] * S), fill=T.RGB["text_dim"], anchor="rm")

    # catatan kiri bawah (per baris — PIL tak dukung anchor utk multiline)
    if catatan:
        fcat = T.font("body", T.SIZE["body"] * S)
        cyv = 828 * S
        for ln in catatan.split("\n"):
            d.text((x, cyv), ln, font=fcat, fill=T.RGB["text_soft"], anchor="lt")
            cyv += int(T.SIZE["body"] * 1.35) * S
    return T.finalize(img)


# ─── SLIDE: SNAPSHOT (grid metrik) ────────────────────────────────────────────
def render_snapshot(ticker, judul, metrics):
    """metrics = list of (label, nilai, warna_key|None)."""
    img, d, S = T.new_canvas()
    _chrome(d, S, ticker, status_right="SNAPSHOT")
    x = T.MARGIN_X * S
    _eyebrow(d, S, x, 300 * S, "Snapshot Fundamental")
    d.text((x, 344 * S), judul, font=T.font("title", T.SIZE["title"] * S),
           fill=T.RGB["text"], anchor="lt")

    cols, gutter = 2, 32 * S
    total_w = (T.WIDTH - 2 * T.MARGIN_X) * S
    cw = (total_w - gutter) // cols
    chh = 150 * S
    top = 470 * S
    for i, (lbl, val, ck) in enumerate(metrics):
        r, c = divmod(i, cols)
        cx = x + c * (cw + gutter)
        cy = top + r * (chh + 26 * S)
        d.rounded_rectangle([cx, cy, cx + cw, cy + chh], radius=16 * S,
                            fill=T.RGB["panel"], outline=T.RGB["line"], width=max(1, S))
        d.text((cx + 34 * S, cy + 34 * S), lbl.upper(),
               font=T.font("mono_med", T.SIZE["label"] * S), fill=T.RGB["text_dim"], anchor="lt")
        # `ck` datang mentah dari JSON draft (## SNAPSHOT:) — kalau ada salah
        # ketik/nilai di luar kontrak "up"/"down"/"neutral"/null (mis. "positive",
        # "green", atau tipe bukan string), JANGAN biarkan KeyError mentah
        # meledakkan render_snapshot di tengah create_video (setelah TTS
        # selesai — lihat render_valuation nilai_wajar<=0 utk pola serupa).
        # Fallback aman: warna netral (T.RGB["text"]), bukan crash.
        col = T.RGB.get(ck, T.RGB["text"]) if isinstance(ck, str) and ck else T.RGB["text"]
        d.text((cx + 34 * S, cy + chh - 34 * S), val,
               font=T.font("mono", 66 * S), fill=col, anchor="lb")
    return T.finalize(img)


# ─── contoh render ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)

    render_cover(
        eyebrow="Bedah Saham",
        title="Laba Naik, Kredit Sehat, Tapi Dibuang Asing.",
        ticker="BBCA",
        subtitle="Kenapa bank paling solid malah paling ditinggal investor asing?",
        tanggal="05 JUL 2026",
    ).save(OUT / "cover.png")

    render_valuation(
        ticker="BBCA", harga=8150, nilai_wajar=10200,
        catatan="Harga di bawah estimasi nilai wajar —\ndiskon cukup lebar secara historis.",
    ).save(OUT / "valuation.png")

    render_snapshot(
        ticker="BBCA", judul="BBCA — Kuartal I 2026",
        metrics=[
            ("Laba bersih", "14,7 T", "up"),
            ("NPL", "1,8%", "up"),
            ("PBV", "2,5x", None),
            ("PER (2026F)", "12,4x", None),
            ("ROE", "±22%", "up"),
            ("Net sell asing", "32,4 T", "down"),
        ],
    ).save(OUT / "snapshot.png")

    print("OK ->", OUT)
