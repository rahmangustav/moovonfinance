import re
import textwrap
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from moviepy import AudioFileClip, VideoClip, ImageClip, concatenate_videoclips, vfx

# Brand palette
DARK_BG = (8, 12, 28)
BLUE    = (40, 110, 230)
ACCENT  = (0, 210, 160)
WHITE   = (255, 255, 255)
GRAY    = (128, 148, 180)

WIDTH, HEIGHT = 1920, 1080
FPS    = 24
FADE   = 0.6
ZOOM   = 0.07        # Ken Burns zoom headroom (7%) — dipakai hanya untuk title slide


# ─── Fonts ────────────────────────────────────────────────────────────────────

def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    )
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ─── Shared draw helpers ──────────────────────────────────────────────────────

def _fill_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    r = img.width / img.height
    if r > w / h:
        nw, nh = int(h * r), h
    else:
        nw, nh = w, int(w / r)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def _draw_header(draw: ImageDraw.ImageDraw, num: int = 0, total: int = 0):
    draw.rectangle([(0, 0), (WIDTH, 68)], fill=(10, 15, 35))
    draw.rectangle([(0, 66), (WIDTH, 70)], fill=BLUE)
    draw.text((38, 34), "MOOVON FINANCE", fill=ACCENT, font=_font(30), anchor="lm")
    if total > 1:
        draw.text((WIDTH - 38, 34), f"{num} / {total}", fill=GRAY, font=_font(26, False), anchor="rm")


def _draw_footer(draw: ImageDraw.ImageDraw, num: int = 0, total: int = 0):
    draw.rectangle([(0, HEIGHT - 58), (WIDTH, HEIGHT)], fill=(10, 15, 35))
    draw.text((38, HEIGHT - 29),
              "Subscribe untuk update analisis saham terbaru  |  @MoovonFinance",
              fill=GRAY, font=_font(22, False), anchor="lm")
    if total > 1:
        bw, bh, bx = 260, 8, WIDTH - 298
        by = HEIGHT - 29
        draw.rounded_rectangle([bx, by - bh // 2, bx + bw, by + bh // 2], radius=4, fill=(28, 38, 72))
        filled = int(bw * num / total)
        if filled > 0:
            draw.rounded_rectangle([bx, by - bh // 2, bx + filled, by + bh // 2], radius=4, fill=ACCENT)


def _radial_mask(size: tuple, inner: float = 0.0, outer: float = 1.0) -> Image.Image:
    """Smooth radial gradient mask (0 at center*inner .. 255 at edge*outer),
    computed with numpy so it has no ring/banding artifacts."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    max_r  = max(np.hypot(cx, cy), 1e-6)
    d      = np.hypot(xx - cx, yy - cy) / max_r
    d      = np.clip((d - inner) / max(outer - inner, 1e-6), 0, 1)
    return Image.fromarray((d * 255).astype(np.uint8), mode="L")


def _add_corner_glow(img: Image.Image, xy: tuple, radius: int = 420,
                      color: tuple = BLUE, intensity: float = 0.5):
    """Soft blurred glow, brightest at `xy` fading smoothly to nothing."""
    size   = radius * 2
    mask   = ImageOps.invert(_radial_mask((size, size)))
    layer  = Image.new("RGB", (size, size), tuple(int(c * intensity) for c in color))
    img.paste(layer, (xy[0] - radius, xy[1] - radius), mask)


# ─── Ken Burns (dipakai hanya untuk title slide) ──────────────────────────────

def _ken_burns_clip(slide_path: str, duration: float, style: str = "zoom_in") -> VideoClip:
    orig_pil = Image.open(slide_path).convert("RGB")
    W, H = orig_pil.size
    orig = np.array(orig_pil)

    def zoom_frame(t):
        p = min(t / duration, 1.0)
        scale = (1.0 + ZOOM * p) if style == "zoom_in" else (1.0 + ZOOM * (1 - p))
        cw = int(W / scale)
        ch = int(H / scale)
        x  = (W - cw) // 2
        y  = (H - ch) // 2
        crop = orig[y: y + ch, x: x + cw]
        return np.array(Image.fromarray(crop).resize((W, H), Image.NEAREST))

    return VideoClip(zoom_frame, duration=duration).with_fps(FPS)


# ─── Slide renderers ──────────────────────────────────────────────────────────

def draw_title_slide(title: str, bg_image_path: str | None = None) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    if bg_image_path:
        try:
            bg = _fill_crop(Image.open(bg_image_path).convert("RGB"), WIDTH, HEIGHT)
            bg = bg.filter(ImageFilter.GaussianBlur(10))
            bg = ImageEnhance.Brightness(bg).enhance(0.35)
            img.paste(bg, (0, 0))
        except Exception:
            pass

    draw = ImageDraw.Draw(img)

    for x in range(WIDTH // 2 + 40):
        t = max(0.0, 1 - x / (WIDTH // 2 + 40))
        draw.line([(x, 0), (x, HEIGHT)], fill=(int(DARK_BG[0] + 4 * t),
                                                int(DARK_BG[1] + 5 * t),
                                                int(DARK_BG[2] + 18 * t)))

    _add_corner_glow(img, (WIDTH - 80, -80), radius=420, color=BLUE, intensity=0.45)

    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT)
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=BLUE)
    draw.text((38, 52), "MOOVON FINANCE", fill=ACCENT, font=_font(34), anchor="lm")
    draw.rectangle([(38, 78), (340, 82)], fill=ACCENT)

    font_big = _font(88)
    font_sm  = _font(70)
    wrapped  = textwrap.wrap(title, width=24)
    use_f    = font_sm if len(title) > 32 else font_big
    line_h   = 106 if use_f is font_big else 88
    total_h  = len(wrapped) * line_h
    y        = (HEIGHT - total_h) // 2 - 20

    for line in wrapped:
        draw.text((55 + 3, y + 3), line, fill=(0, 0, 0), font=use_f)
        draw.text((55, y), line, fill=WHITE, font=use_f)
        y += line_h

    draw.rounded_rectangle([55, y + 16, 400, y + 22], radius=3, fill=ACCENT)
    draw.text((55, y + 48), "Analisis Saham & Keuangan Indonesia", fill=GRAY, font=_font(36, False))
    draw.text((55, y + 98), datetime.now().strftime("%d %B %Y"), fill=ACCENT, font=_font(28, False))

    _draw_footer(draw)
    return img


def draw_fullphoto_slide(
    caption: str,
    bg_image_path: str | None = None,
    badge_text: str = "TERKINI",
    title: str | None = None,
    num: int = 0,
    total: int = 0,
) -> Image.Image:
    """Full-bleed photo + short caption at bottom (breaking-news/story style).
    Satu bahasa visual dipakai untuk SEMUA slide non-CTA (dulu section biasa
    pakai panel teks+foto terpisah yang kebanyakan teks; sekarang seragam
    foto penuh + judul singkat + 1-2 kalimat highlight saja)."""
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    if bg_image_path:
        try:
            bg = _fill_crop(Image.open(bg_image_path).convert("RGB"), WIDTH, HEIGHT)
            bg = bg.filter(ImageFilter.GaussianBlur(4))
            bg = ImageEnhance.Brightness(bg).enhance(0.5)
            img.paste(bg, (0, 0))
        except Exception:
            pass
    else:
        _add_corner_glow(img, (WIDTH - 100, 60), radius=520, color=BLUE, intensity=0.35)
        _add_corner_glow(img, (140, HEIGHT - 700), radius=380, color=ACCENT, intensity=0.18)

    mid      = HEIGHT // 2
    t        = np.clip((np.arange(HEIGHT) - mid) / (HEIGHT - mid), 0, 1)
    grad     = (225 * (t ** 1.5)).astype(np.uint8)
    grad_img = Image.fromarray(np.tile(grad.reshape(-1, 1), (1, WIDTH)), mode="L")
    img = Image.composite(Image.new("RGB", (WIDTH, HEIGHT), DARK_BG), img, grad_img)

    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT)
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=BLUE)
    _draw_header(draw, num, total)

    # Badge (angka slide / label pendek — lebar menyesuaikan teksnya)
    font_badge = _font(28)
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw   = bbox[2] - bbox[0]
    block_h   = 450 if title else 370
    badge_top = HEIGHT - block_h
    draw.rounded_rectangle([38, badge_top, 38 + bw + 40, badge_top + 38], radius=5, fill=ACCENT)
    draw.text((38 + (bw + 40) // 2, badge_top + 19), badge_text,
               fill=DARK_BG, font=font_badge, anchor="mm")

    y = badge_top + 54
    if title:
        font_title = _font(50)
        for wl in textwrap.wrap(title, width=42):
            if y > HEIGHT - 150:
                break
            draw.text((42, y), wl, fill=WHITE, font=font_title)
            y += 58
        y += 10

    # Caption: hanya gambar baris yang MUAT PENUH di atas bar footer. Jangan
    # sampai baris terakhir nabrak bar bawah (HEIGHT-64) / status bar dan putus
    # di tengah kalimat. Kalau kepanjangan → potong di batas baris + elipsis.
    font_t   = _font(40, bold=False)
    LINE_H   = 48
    CAP_LIMIT = HEIGHT - 88            # sisakan jarak aman dari bar footer (HEIGHT-64)
    wrapped_caption: list[str] = []
    for line in caption.split("\n"):
        stripped = re.sub(r"[#*\[\]]", "", line.strip())
        if stripped:
            wrapped_caption.extend(textwrap.wrap(stripped, width=66))
    max_lines = max(1, (CAP_LIMIT - y) // LINE_H)
    if len(wrapped_caption) > max_lines:
        wrapped_caption = wrapped_caption[:max_lines]
        wrapped_caption[-1] = wrapped_caption[-1].rstrip(" .,;:—–-") + "…"
    for wl in wrapped_caption:
        draw.text((42, y), wl, fill=WHITE, font=font_t)
        y += LINE_H

    draw.rectangle([(0, HEIGHT - 64), (WIDTH, HEIGHT - 58)], fill=ACCENT)
    _draw_footer(draw, num, total)
    return img


def draw_cta_slide(content: str, bg_image_path: str | None = None) -> Image.Image:
    """Full-background CTA slide with subscribe call-to-action."""
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    if bg_image_path:
        try:
            bg = _fill_crop(Image.open(bg_image_path).convert("RGB"), WIDTH, HEIGHT)
            bg = bg.filter(ImageFilter.GaussianBlur(8))
            bg = ImageEnhance.Brightness(bg).enhance(0.30)
            img.paste(bg, (0, 0))
        except Exception:
            pass

    vignette = _radial_mask((WIDTH, HEIGHT), inner=0.3, outer=1.05)
    img = Image.composite(Image.new("RGB", (WIDTH, HEIGHT), (2, 3, 10)), img, vignette)

    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT)
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=BLUE)
    _draw_header(draw)

    lx = WIDTH // 2
    draw.text((lx, HEIGHT // 2 - 90), "MOOVON FINANCE", fill=ACCENT, font=_font(52), anchor="mm")
    draw.text((lx, HEIGHT // 2 - 10), "SUBSCRIBE SEKARANG!", fill=WHITE, font=_font(78), anchor="mm")
    draw.rounded_rectangle([lx - 220, HEIGHT // 2 + 58, lx + 220, HEIGHT // 2 + 66], radius=4, fill=ACCENT)

    font_sub = _font(34, bold=False)
    clean = re.sub(r"[#*\[\]]", "", content).strip().replace("\n", " ")
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    display = ""
    for s in sentences:
        candidate = (display + " " + s).strip()
        if len(textwrap.wrap(candidate, width=58)) <= 3:
            display = candidate
        else:
            break
    if not display:
        display = textwrap.wrap(clean, width=58 * 3)[0] if clean else ""
    lines = textwrap.wrap(display, width=58)
    y_sub = HEIGHT // 2 + 100
    for wl in lines:
        draw.text((lx, y_sub), wl, fill=GRAY, font=font_sub, anchor="mm")
        y_sub += 48

    _draw_footer(draw)
    return img



# ─── Section parsing & keywords ───────────────────────────────────────────────

def parse_sections(script: str) -> list[dict]:
    pattern  = re.compile(r"\[([A-Za-z0-9\s\-]+?)\](.*?)(?=\[[A-Za-z0-9\s\-]+?\]|$)", re.DOTALL)
    sections = []
    for m in pattern.finditer(script):
        label   = m.group(1).strip().upper()
        content = re.sub(r"\[[A-Za-z0-9\s\-]+?\]", "", m.group(2)).strip()
        if content:
            sections.append({"label": label, "content": content})
    if not sections:
        chunks   = [script[i:i + 500] for i in range(0, len(script), 500)]
        sections = [{"label": f"BAGIAN {i + 1}", "content": c} for i, c in enumerate(chunks)]
    return sections


_SECTION_PHOTO_HINTS = {
    "HOOK":        "{topic} stock market crash breaking news",
    "INTRO":       "{topic} financial analysis Indonesia office",
    "KESIMPULAN":  "investor saham Indonesia sukses bursa efek analisis",
    "CTA":         "Indonesia stock market bull growth investment coins",
}
_SKIP_WORDS = {"detik", "menit", "utama", "bagian", "hook", "intro", "kesimpulan", "cta", "isi"}

_LABEL_DISPLAY = {
    "HOOK": "TERKINI",
    "INTRO": "PENDAHULUAN",
    "ISI UTAMA": "PEMBAHASAN",
    "KESIMPULAN": "KESIMPULAN",
}


def _clean_label(label: str) -> str:
    """Remove duration info; kalau formatnya 'KODE - Judul deskriptif'
    (mis. 'SECTION 1 - Fundamentalnya Masih Bagus'), pakai judul
    deskriptifnya di layar — jauh lebih informatif daripada kode section
    generik. Hyphen di dalam kata majemuk (mis. 'Baik-Baik') tidak ikut
    terpotong karena dipisah pada '-' yang diapit spasi saja."""
    clean = re.sub(r'\s*-\s*[\d][\d\-]*\s*(DETIK|MENIT)', '', label.upper()).strip()
    if clean in _LABEL_DISPLAY:
        return _LABEL_DISPLAY[clean]
    parts = re.split(r'\s+-\s+', clean, maxsplit=1)
    if len(parts) == 2 and parts[1].strip():
        return parts[1].strip()
    return clean


def _short_content(content: str, max_sentences: int = 3, max_chars: int = 320) -> str:
    """Ringkas narasi jadi beberapa kalimat pertama untuk ditampilkan di
    layar. Narasi lengkap tetap dibacakan lewat audio — layar cukup jadi
    highlight, bukan transkrip penuh (dulu seluruh paragraf ditulis apa
    adanya, jadi wall-of-text yang berat dibaca)."""
    clean = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", content)   # buang **bold**/*italic*
    clean = re.sub(r"\s+", " ", clean).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    picked, total = [], 0
    for s in sentences:
        # Kalimat pembuka basa-basi pendek ("Nah, ini bagian intinya.") tidak
        # boleh berhenti sendirian tanpa isi — paksa ambil kalimat berikutnya
        # walau sedikit lewat budget karakter, daripada caption kosong makna.
        is_short_opener = not picked and len(s) < 40
        if len(picked) >= max_sentences:
            break
        if picked and not is_short_opener and total + len(s) > max_chars:
            break
        picked.append(s)
        total += len(s)
    if not picked and sentences:
        picked = [sentences[0][:max_chars]]
    return " ".join(picked)


def _section_keywords(label: str, content: str, topic: str) -> str:
    label_upper = label.upper()
    for key, tmpl in _SECTION_PHOTO_HINTS.items():
        if key in label_upper:
            return tmpl.format(topic=topic[:40])
    label_words = [w for w in re.sub(r"[^\w\s]", " ", label.lower()).split()
                   if len(w) > 3 and w not in _SKIP_WORDS]
    # Sengaja TIDAK pakai potongan kalimat narasi mentah di sini: dulu itu
    # dipakai sebagai bagian query (mis. "harga saham turun...") dan ddgs
    # sering nyasar ke foto tak relevan/tak pantas (iklan pinjol, dst).
    # Query generik+aman (topic + label) jauh lebih dapat diprediksi.
    return f"{' '.join(label_words[:3])} {topic[:40]} professional finance business Indonesia".strip()


def _slide_type(label: str) -> str:
    u = label.upper()
    if "HOOK" in u:
        return "hook"
    if "CTA" in u:
        return "cta"
    return "content"


def _match_charts_to_sections(sections: list, charts: list) -> list:
    """Kelompokkan tiap chart ke section-nya. Return list paralel dengan
    `sections`: elemen ke-i berisi daftar spec chart untuk section itu.
    Chart tanpa 'section' cocok → dilekatkan ke ISI UTAMA (atau section terakhir).
    """
    per_section = [[] for _ in sections]
    if not sections:
        return per_section

    def _fallback_index() -> int:
        for i, s in enumerate(sections):
            if "ISI" in s["label"].upper():
                return i
        return len(sections) - 1

    for chart in charts or []:
        target = str(chart.get("section", "")).upper().strip()
        placed = False
        if target:
            for i, s in enumerate(sections):
                lbl = s["label"].upper()
                if target in lbl or lbl in target:
                    per_section[i].append(chart)
                    placed = True
                    break
        if not placed:
            per_section[_fallback_index()].append(chart)
    return per_section


def _resolve_keyword(label: str, content: str, topic: str, visual_keywords: dict) -> str:
    """Resolve image search keyword: keyword map first, rule-based fallback."""
    label_upper = label.upper()
    if label_upper in visual_keywords:
        return visual_keywords[label_upper]
    for key, kw in visual_keywords.items():
        if key in label_upper:
            return kw
    return _section_keywords(label, content, topic)


def _burn_subtitles(video_path: str, srt_path: str, output_path: str):
    """Burn SRT subtitles into video using bundled ffmpeg."""
    import subprocess
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # CATATAN SKALA: libass memakai PlayResY=288 untuk SRT, lalu menskalakan ke
    # resolusi video. Di 1080p semua angka di bawah dikali ~3,75:
    # FontSize=13 ≈ 49px, Outline=1 ≈ 4px, MarginV=12 ≈ 45px dari bawah.
    style = (
        "FontName=DejaVu Sans Bold,"
        "FontSize=13,"
        "PrimaryColour=&H00ffffff,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=1,"
        "Shadow=0.5,"
        "ShadowColour=&H80000000,"
        "MarginV=12,"
        "MarginL=30,"
        "MarginR=30,"
        "Alignment=2,"
        "Bold=1"
    )

    result = subprocess.run(
        [ffmpeg, "-y", "-i", video_path,
         "-vf", f"subtitles={srt_path}:force_style='{style}'",
         "-c:a", "copy", output_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg subtitle burn failed:\n{result.stderr[-500:]}")


_ID_MONTHS = ["JAN", "FEB", "MAR", "APR", "MEI", "JUN",
              "JUL", "AGU", "SEP", "OKT", "NOV", "DES"]


def _id_date(dt=None) -> str:
    dt = dt or datetime.now()
    return f"{dt.day:02d} {_ID_MONTHS[dt.month - 1]} {dt.year}"


def _guess_ticker(*texts: str) -> str:
    """Tebak kode emiten (4 huruf kapital) dari judul/topik; fallback 'IDX'."""
    for t in texts:
        for m in re.findall(r"\b[A-Z]{4}\b", t or ""):
            return m
    return "IDX"


def _first_sentence(text: str, max_chars: int = 120) -> str:
    clean = re.sub(r"[#*\[\]]", "", text or "").strip()
    clean = re.sub(r"\s+", " ", clean)
    parts = re.split(r"(?<=[.!?])\s+", clean)
    s = parts[0] if parts else clean
    return (s[:max_chars].rstrip(" ,.;:—–-") + "…") if len(s) > max_chars else s


def create_video(
    title: str,
    script: str,
    audio_path: str,
    output_path: str,
    topic_keywords: str = "",
    visual_keywords: dict | None = None,
    charts: list | None = None,
    valuation: dict | None = None,
    snapshot: dict | None = None,
    eyebrow: str | None = None,
    ticker_override: str | None = None,
) -> str:
    """Pipeline video FULL ON-BRAND v2.0 "SINYAL". Semua slide dirender dari
    render_slides.py (cover + section naratif + penutup) + chart tema gelap.
    TIDAK ada lagi foto/ddgs/Ken Burns — identitas visual 100% terkontrol.
    Pertahankan: TTS/audio, subtitle burn dari SRT, penyisipan chart, timing."""
    import sys
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "core"))
    import render_slides as RS
    import moovon_theme as MT
    from PIL import Image as _Img, ImageDraw as _Draw
    from subtitle import transcribe, to_srt
    from chart_templates import render_chart

    charts          = charts or []
    sections        = parse_sections(script)
    out_dir         = Path(output_path).parent
    audio           = AudioFileClip(audio_path)
    total_duration  = audio.duration
    topic           = topic_keywords or title
    # ticker_override: string kustom (mis. "EDUKASI") atau "" utk sembunyikan kapsul.
    ticker          = ticker_override if ticker_override is not None else _guess_ticker(title, topic)
    cover_eyebrow   = eyebrow or "Bedah Saham"
    n_sec           = len(sections)

    # ── COVER (intro statis 10 dtk) ──
    # Buang prefix "TICKER:" dari judul (ticker sudah tampil di kapsul).
    cover_title = title
    if ":" in title:
        head, rest = title.split(":", 1)
        if len(head.strip()) <= 6 and rest.strip():
            cover_title = rest.strip()
    subtitle = _first_sentence(sections[0]["content"], 96) if sections else ""
    cover_path = str(out_dir / "slide_cover.png")
    RS.render_cover(cover_eyebrow, cover_title, ticker, subtitle, _id_date()).save(cover_path)
    print(f"   🎨 Cover on-brand — {ticker or '(tanpa ticker)'}")
    clips = [ImageClip(cover_path).with_duration(10).with_fps(FPS).with_effects([vfx.FadeIn(FADE)])]

    # ── Posisi sisip slide tanda tangan (gauge valuasi & snapshot fundamental) ──
    # Dicocokkan ke section lewat kata kunci label (pola sama dgn chart matching).
    def _find_section(keys, default):
        for idx, s in enumerate(sections):
            u = s["label"].upper()
            if any(k in u for k in keys):
                return idx
        return default

    last_content = max(
        (i for i, s in enumerate(sections) if _slide_type(s["label"]) != "cta"),
        default=len(sections) - 1,
    )
    first_content = next(
        (i for i, s in enumerate(sections) if _slide_type(s["label"]) == "content"), 0
    )
    val_after = _find_section(
        ["VALUAS", "NILAI WAJAR", "MARGIN", "MURAH", "MAHAL", "HARGA WAJAR", "DISKON"],
        last_content,
    ) if valuation else None
    snap_after = _find_section(
        ["FUNDAMENTAL", "SNAPSHOT", "KINERJA", "KEUANGAN", "LABA"], first_content
    ) if snapshot else None

    # ── Tiap section = 1 slide on-brand; chart disisipkan setelah section ──
    per_section_charts = _match_charts_to_sections(sections, charts)
    items = []
    for i, section in enumerate(sections):
        items.append({"kind": "slide", "section": section, "index": i})
        for j, chart in enumerate(per_section_charts[i]):
            items.append({"kind": "chart", "spec": chart, "section": section, "index": i, "sub": j})
        if snapshot and i == snap_after:
            items.append({"kind": "snapshot", "data": snapshot, "index": i})
        if valuation and i == val_after:
            items.append({"kind": "valuation", "data": valuation, "index": i})

    n_charts = sum(len(c) for c in per_section_charts)
    if n_charts:
        print(f"   📊 {n_charts} chart data (tema gelap v2.0) disisipkan sebagai slide")

    remaining = total_duration - 10
    per_item  = max(4.0, remaining / max(len(items), 1))

    for item in items:
        if item["kind"] == "valuation":
            v = item["data"]
            slide_path = str(out_dir / f"slide_valuation_{item['index']:03d}.png")
            RS.render_valuation(ticker, v["harga"], v["nilai_wajar"],
                                v.get("catatan", "")).save(slide_path)
            label, _c, mos = MT.verdict(v["harga"], v["nilai_wajar"])
            print(f"   📐 Gauge Margin of Safety — {label} (MoS {mos*100:+.1f}%)")
            clips.append(
                ImageClip(slide_path).with_duration(per_item)
                .with_fps(FPS).with_effects([vfx.FadeIn(FADE)])
            )
            continue

        if item["kind"] == "snapshot":
            s = item["data"]
            slide_path = str(out_dir / f"slide_snapshot_{item['index']:03d}.png")
            RS.render_snapshot(ticker, s.get("judul", f"{ticker} — Snapshot"),
                               s["metrics"]).save(slide_path)
            print(f"   🧭 Snapshot fundamental — {len(s['metrics'])} metrik")
            clips.append(
                ImageClip(slide_path).with_duration(per_item)
                .with_fps(FPS).with_effects([vfx.FadeIn(FADE)])
            )
            continue

        if item["kind"] == "chart":
            spec = dict(item["spec"])
            spec.setdefault("sumber", "Moovon Finance")
            spec.setdefault("nama_file", f"chart_{item['index']:03d}_{item['sub']}")
            print(f"   📊 [{item['section']['label'][:20]}] chart {spec.get('type','?')}: {str(spec.get('judul',''))[:40]}")
            chart_path = render_chart(spec, out_dir=out_dir)
            if chart_path:
                clips.append(
                    ImageClip(chart_path).with_duration(per_item)
                    .with_fps(FPS).with_effects([vfx.FadeIn(FADE)])
                )
            else:
                print("   ⚠️  Chart gagal dirender, slide dilewati.")
            continue

        section = item["section"]
        i       = item["index"]
        stype   = _slide_type(section["label"])
        lead    = _short_content(section["content"], max_sentences=3, max_chars=300)
        slide_path = str(out_dir / f"slide_{i:03d}.png")

        if stype == "cta":
            slide_img = RS.render_closing(ticker, _first_sentence(section["content"], 88))
        elif stype == "hook":
            # mode statement: lead besar, tanpa judul (hindari duplikat)
            hook_lead = _short_content(section["content"], max_sentences=2, max_chars=210)
            slide_img = RS.render_section(i + 1, n_sec, "", hook_lead, ticker, eyebrow="Sorotan")
        else:
            slide_img = RS.render_section(i + 1, n_sec, _clean_label(section["label"]),
                                          lead, ticker, eyebrow="Analisis")
        slide_img.save(slide_path)
        print(f"   🎨 [{section['label'][:24]}] slide on-brand {i + 1}/{n_sec}")
        clips.append(
            ImageClip(slide_path).with_duration(per_item)
            .with_fps(FPS).with_effects([vfx.FadeIn(FADE)])
        )

    # ── Kompensasi kalau ada chart/slide gagal dirender di tengah loop ──
    # (durasi tiap item dihitung di muka dari jumlah item; item yang gagal
    # dilewati tanpa clip pengganti, jadi total durasi visual bisa lebih
    # pendek dari audio. Perpanjang slide terakhir menutup selisihnya
    # supaya subclip ke total_duration tidak error.)
    shortfall = total_duration - sum(c.duration for c in clips)
    if shortfall > 0.05:
        print(f"   ⏱️  Visual {shortfall:.1f} detik lebih pendek dari audio — slide terakhir diperpanjang")
        clips[-1] = clips[-1].with_duration(clips[-1].duration + shortfall)

    # ── Export background-only video ──
    bg_path = output_path.replace(".mp4", "_bg.mp4")
    video   = concatenate_videoclips(clips).with_audio(audio)
    video   = video.subclipped(0, total_duration)
    video.write_videofile(bg_path, fps=FPS, codec="libx264", audio_codec="aac", logger=None)

    # ── Subtitle: pakai SRT akurat dari TTS bila ada, fallback whisper ──
    import shutil
    srt_path = output_path.replace(".mp4", ".srt")
    tts_srt  = Path(audio_path).with_suffix(".srt")
    if tts_srt.exists() and tts_srt.stat().st_size > 0:
        print(f"   📝 Subtitle akurat dari TTS: {tts_srt.name}")
        shutil.copyfile(tts_srt, srt_path)
    else:
        print("   🎯 Transcribing audio for subtitles (fallback whisper)...")
        segments = transcribe(audio_path)
        to_srt(segments, srt_path)
        print(f"   📝 {len(segments)} subtitle segments")

    # ── Burn subtitles ──
    print("   🔤 Burning subtitles...")
    _burn_subtitles(bg_path, srt_path, output_path)
    Path(bg_path).unlink(missing_ok=True)

    print(f"Video saved: {output_path}")
    return output_path
