import re
import textwrap
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from moviepy import AudioFileClip, VideoClip, ImageClip, concatenate_videoclips, vfx

# Brand palette
DARK_BG    = (8, 12, 28)
PANEL_BG   = (14, 22, 52)
BLUE       = (40, 110, 230)
BLUE_DIM   = (22, 55, 130)
ACCENT     = (0, 210, 160)
ACCENT_DIM = (0, 80, 62)
WHITE      = (255, 255, 255)
GRAY       = (128, 148, 180)

WIDTH, HEIGHT = 1920, 1080
FPS    = 24
FADE   = 0.6
ZOOM   = 0.07        # Ken Burns zoom headroom (7%)
SPLIT_X = 1100       # x where photo panel starts


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


def _draw_bg(draw: ImageDraw.ImageDraw, x_limit: int = WIDTH):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(DARK_BG[0] + 6 * (1 - t))
        g = int(DARK_BG[1] + 8 * (1 - t))
        b = int(DARK_BG[2] + 20 * (1 - t))
        draw.line([(0, y), (x_limit, y)], fill=(r, g, b))
    grid = (16, 22, 46)
    for x in range(0, x_limit + 1, 120):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid)
    for y in range(0, HEIGHT + 1, 120):
        draw.line([(0, y), (x_limit, y)], fill=grid)


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


def _paste_rounded(base: Image.Image, overlay: Image.Image, xy: tuple, r: int = 16):
    mask = Image.new("L", overlay.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, overlay.width - 1, overlay.height - 1], radius=r, fill=255)
    base.paste(overlay, xy, mask)


# ─── Ken Burns ────────────────────────────────────────────────────────────────

_KB_CYCLE = ["zoom_in", "pan_right", "zoom_out", "pan_left"]


def _ken_burns_clip(slide_path: str, duration: float, style: str = "zoom_in") -> VideoClip:
    """VideoClip with subtle Ken Burns motion. Pan styles use pre-rendered large
    array (fast); zoom styles do per-frame crop+resize (slower but true zoom)."""
    orig_pil = Image.open(slide_path).convert("RGB")
    W, H = orig_pil.size

    if "pan" in style:
        big_w = int(W * (1 + ZOOM))
        big_h = int(H * (1 + ZOOM))
        big   = np.array(orig_pil.resize((big_w, big_h), Image.LANCZOS))
        max_x = big_w - W
        max_y = big_h - H

        def pan_frame(t):
            p = min(t / duration, 1.0)
            x = int(max_x * p) if style == "pan_right" else int(max_x * (1 - p))
            return big[max_y // 2: max_y // 2 + H, x: x + W]

        return VideoClip(pan_frame, duration=duration).with_fps(FPS)

    else:
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

    # Solid dark left panel so text is readable
    for x in range(WIDTH // 2 + 40):
        t = max(0.0, 1 - x / (WIDTH // 2 + 40))
        draw.line([(x, 0), (x, HEIGHT)], fill=(int(DARK_BG[0] + 4 * t),
                                                int(DARK_BG[1] + 5 * t),
                                                int(DARK_BG[2] + 18 * t)))

    # Decorative glow top-right
    for r in range(400, 0, -20):
        t = r / 400
        c = (int(BLUE[0] * t * 0.3), int(BLUE[1] * t * 0.3), int(BLUE[2] * t * 0.3))
        draw.ellipse([WIDTH - 80 - r, -80 - r, WIDTH - 80 + r, -80 + r], fill=c)

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


def draw_hook_slide(content: str, bg_image_path: str | None = None) -> Image.Image:
    """Breaking-news style: full background photo, text overlay at bottom."""
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    if bg_image_path:
        try:
            bg = _fill_crop(Image.open(bg_image_path).convert("RGB"), WIDTH, HEIGHT)
            bg = bg.filter(ImageFilter.GaussianBlur(4))
            bg = ImageEnhance.Brightness(bg).enhance(0.55)
            img.paste(bg, (0, 0))
        except Exception:
            pass

    draw = ImageDraw.Draw(img)

    # Gradient darkening from midpoint down
    mid = HEIGHT // 2
    for y in range(mid, HEIGHT):
        t = (y - mid) / (HEIGHT - mid)
        v = int(200 * (t ** 1.5))
        r_, g_, b_ = DARK_BG
        draw.line([(0, y), (WIDTH, y)], fill=(r_, g_, b_))

    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT)
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=BLUE)
    _draw_header(draw)

    # "TERKINI" badge
    draw.rounded_rectangle([38, HEIGHT - 288, 196, HEIGHT - 250], radius=5, fill=ACCENT)
    draw.text((117, HEIGHT - 269), "⚡ TERKINI", fill=DARK_BG, font=_font(28), anchor="mm")

    # Hook text — first 2 paragraphs, large
    font_t = _font(46, bold=False)
    y = HEIGHT - 240
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"[#*\[\]]", "", stripped)
        for wl in textwrap.wrap(stripped, width=60):
            if y > HEIGHT - 72:
                break
            draw.text((42, y), wl, fill=WHITE, font=font_t)
            y += 54

    draw.rectangle([(0, HEIGHT - 64), (WIDTH, HEIGHT - 58)], fill=ACCENT)
    _draw_footer(draw)
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

    draw = ImageDraw.Draw(img)

    # Radial dark vignette
    cx, cy = WIDTH // 2, HEIGHT // 2
    for r in range(max(WIDTH, HEIGHT), 0, -30):
        t = r / max(WIDTH, HEIGHT)
        v = int(180 * (t ** 2))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(v // 10, v // 8, v // 4))

    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT)
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=BLUE)
    _draw_header(draw)

    # Centered CTA
    lx = WIDTH // 2
    draw.text((lx, HEIGHT // 2 - 90), "MOOVON FINANCE", fill=ACCENT, font=_font(52), anchor="mm")
    draw.text((lx, HEIGHT // 2 - 10), "SUBSCRIBE SEKARANG!", fill=WHITE, font=_font(78), anchor="mm")
    draw.rounded_rectangle([lx - 220, HEIGHT // 2 + 58, lx + 220, HEIGHT // 2 + 66], radius=4, fill=ACCENT)

    # Sub-text — hanya kalimat lengkap, max 3 baris
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


def draw_content_slide(
    title: str,
    content: str,
    slide_num: int,
    total: int,
    side_image_path: str | None = None,
) -> Image.Image:
    """Standard split-layout slide: text left, photo right."""
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)
    draw = ImageDraw.Draw(img)

    has_img    = bool(side_image_path)
    text_right = SPLIT_X - 18 if has_img else WIDTH - 22

    _draw_bg(draw, x_limit=text_right + 10)
    _draw_header(draw, slide_num, total)
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=ACCENT)

    # Section badge
    bx1, by1, bx2, by2 = 22, 82, 108, 150
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=10, fill=BLUE_DIM)
    draw.text(((bx1 + bx2) // 2, (by1 + by2) // 2), f"{slide_num:02d}", fill=ACCENT, font=_font(40), anchor="mm")

    tx, ty = 126, 86
    for line in textwrap.wrap(title, width=46 if has_img else 60):
        if ty > 168:
            break
        draw.text((tx, ty), line, fill=WHITE, font=_font(56))
        ty += 66

    draw.rounded_rectangle([tx, ty + 6, min(tx + len(title) * 28, text_right - 20), ty + 11], radius=3, fill=ACCENT)

    card_top = max(ty + 26, 244)
    card_bot = HEIGHT - 66
    draw.rounded_rectangle([22, card_top, text_right, card_bot], radius=14, fill=PANEL_BG)
    draw.rounded_rectangle([22, card_top, text_right, card_bot], radius=14, outline=BLUE_DIM, width=1)

    font_body = _font(33, bold=False)
    font_head = _font(34, bold=True)
    cx, cy    = 54, card_top + 26
    max_cy    = card_bot - 18
    wrap_w    = 52 if has_img else 80

    for raw_line in content.split("\n"):
        if cy >= max_cy:
            break
        stripped = raw_line.strip()
        if not stripped:
            cy += 12
            continue

        is_heading = stripped.startswith("###") or (stripped.startswith("**") and stripped.endswith("**"))
        is_bullet  = stripped[:1] in ("•", "-", "*", "●")

        if is_heading:
            text = re.sub(r"[#*]", "", stripped).strip()
            bbox = draw.textbbox((0, 0), text, font=font_head)
            tw   = bbox[2] - bbox[0]
            draw.rounded_rectangle([cx - 8, cy - 4, cx + min(tw + 16, text_right - cx - 10), cy + 38],
                                    radius=6, fill=ACCENT_DIM)
            for wl in textwrap.wrap(text, width=wrap_w):
                if cy >= max_cy: break
                draw.text((cx, cy), wl, fill=ACCENT, font=font_head)
                cy += 46
            cy += 4
        elif is_bullet:
            text  = re.sub(r"^[•\-\*●]\s*", "", stripped)
            first = True
            for wl in textwrap.wrap(text, width=wrap_w - 2):
                if cy >= max_cy: break
                if first:
                    draw.text((cx, cy), "●", fill=ACCENT, font=font_body)
                    draw.text((cx + 28, cy), wl, fill=WHITE, font=font_body)
                    first = False
                else:
                    draw.text((cx + 28, cy), wl, fill=GRAY, font=font_body)
                cy += 42
        else:
            for wl in textwrap.wrap(stripped, width=wrap_w + 4):
                if cy >= max_cy: break
                draw.text((cx, cy), wl, fill=WHITE, font=font_body)
                cy += 42

    # Right photo panel
    if has_img:
        img_x = SPLIT_X
        img_w = WIDTH - SPLIT_X - 22
        img_h = card_bot - card_top
        try:
            side = _fill_crop(Image.open(side_image_path).convert("RGB"), img_w, img_h)
            _paste_rounded(img, side, (img_x, card_top), r=14)
            # Soft blend edge
            for dx in range(36):
                t = 1 - dx / 36
                r_, g_, b_ = PANEL_BG
                draw.line([(img_x + dx, card_top), (img_x + dx, card_bot)], fill=(r_, g_, b_))
        except Exception as e:
            print(f"   ⚠️  Foto gagal: {e}")

    _draw_footer(draw, slide_num, total)
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
    """Remove duration info and map to clean display name."""
    clean = re.sub(r'\s*-\s*[\d][\d\-]*\s*(DETIK|MENIT)', '', label.upper()).strip()
    return _LABEL_DISPLAY.get(clean, clean)


def _section_keywords(label: str, content: str, topic: str) -> str:
    label_upper = label.upper()
    for key, tmpl in _SECTION_PHOTO_HINTS.items():
        if key in label_upper:
            return tmpl.format(topic=topic[:40])
    # For ISI UTAMA / custom sections: use label words + first content line
    label_words = [w for w in re.sub(r"[^\w\s]", " ", label.lower()).split()
                   if len(w) > 3 and w not in _SKIP_WORDS]
    first_line  = re.sub(r"[#*\[\]]", "", content.split("\n")[0]).strip()[:55]
    return f"{' '.join(label_words[:2])} {first_line} Indonesia".strip() or f"{topic} finance"


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


# ─── Main pipeline ────────────────────────────────────────────────────────────

def _resolve_keyword(
    label: str,
    content: str,
    topic: str,
    visual_keywords: dict,
) -> str:
    """Resolve image search keyword: AI-generated first, rule-based fallback."""
    label_upper = label.upper()

    # 1. Exact match from AI keywords
    if label_upper in visual_keywords:
        return visual_keywords[label_upper]

    # 2. Partial match (e.g. "HOOK - 30 DETIK" matches key "HOOK")
    for key, kw in visual_keywords.items():
        if key in label_upper:
            return kw

    # 3. Rule-based fallback
    return _section_keywords(label, content, topic)


def draw_fullimage_slide(bg_image_path: str | None) -> Image.Image:
    """Full-screen image slide with header + bottom gradient (no text content)."""
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    if bg_image_path:
        try:
            bg = _fill_crop(Image.open(bg_image_path).convert("RGB"), WIDTH, HEIGHT)
            img.paste(bg, (0, 0))
        except Exception:
            pass

    draw = ImageDraw.Draw(img)

    # Dark gradient at top so header is readable
    for y in range(90):
        t = 1 - (y / 90) ** 0.5
        r, g, b = int(10 * t), int(15 * t), int(35 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(8 + r, 12 + g, 28 + b))

    # Dark gradient at bottom so subtitles are readable
    for y in range(HEIGHT - 220, HEIGHT):
        t = ((y - (HEIGHT - 220)) / 220) ** 0.6
        v = int(t * 220)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, v - 8), max(0, v - 10), max(0, v - 5)))

    # Header
    draw.rectangle([(0, 0), (WIDTH, 4)], fill=ACCENT)
    draw.text((38, 36), "MOOVON FINANCE", fill=ACCENT, font=_font(30), anchor="lm")

    # Footer
    draw.rectangle([(0, HEIGHT - 52), (WIDTH, HEIGHT)], fill=(8, 12, 28))
    draw.text((38, HEIGHT - 26),
              "Subscribe untuk update analisis saham terbaru  |  @MoovonFinance",
              fill=GRAY, font=_font(22, False), anchor="lm")

    return img


def _burn_subtitles(video_path: str, srt_path: str, output_path: str):
    """Burn SRT subtitles into video using bundled ffmpeg."""
    import subprocess
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    style = (
        "FontName=DejaVu Sans Bold,"
        "FontSize=26,"
        "PrimaryColour=&H00ffffff,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "ShadowColour=&H80000000,"
        "MarginV=90,"
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


def create_video(
    title: str,
    script: str,
    audio_path: str,
    output_path: str,
    topic_keywords: str = "",
    visual_keywords: dict | None = None,
    charts: list | None = None,
) -> str:
    import sys
    from modules.image_fetcher import fetch_image
    from modules.subtitle import transcribe, to_srt

    # Mesin grafik ada di scripts/ — pastikan bisa diimpor dari pipeline.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    from chart_templates import render_chart

    visual_keywords = visual_keywords or {}
    charts          = charts or []
    sections        = parse_sections(script)
    out_dir         = Path(output_path).parent
    audio           = AudioFileClip(audio_path)
    total_duration  = audio.duration
    topic           = topic_keywords or title

    # ── Title slide ──
    title_query = visual_keywords.get("TITLE") or f"{topic} finance Indonesia"
    print(f"   📸 Foto title: {title_query[:65]}")
    title_img  = draw_title_slide(title, bg_image_path=fetch_image(title_query))
    title_path = str(out_dir / "slide_title.png")
    title_img.save(title_path)
    clips = [_ken_burns_clip(title_path, 10, "zoom_in").with_effects([vfx.FadeIn(FADE)])]

    # ── Rencana visual: tiap section = 1 slide foto; chart (bila ada) disisipkan
    #    sebagai slide sendiri tepat setelah section terkait. ──
    per_section_charts = _match_charts_to_sections(sections, charts)
    items = []
    for i, section in enumerate(sections):
        items.append({"kind": "photo", "section": section, "index": i})
        for j, chart in enumerate(per_section_charts[i]):
            items.append({"kind": "chart", "spec": chart, "section": section, "index": i, "sub": j})

    n_charts = sum(len(c) for c in per_section_charts)
    if n_charts:
        print(f"   📊 {n_charts} chart data akan disisipkan sebagai slide")

    remaining = total_duration - 10
    per_item  = max(4.0, remaining / max(len(items), 1))

    photo_i = 0
    for item in items:
        if item["kind"] == "chart":
            spec = dict(item["spec"])
            spec.setdefault("sumber", "Moovon Finance")
            spec.setdefault("nama_file", f"chart_{item['index']:03d}_{item['sub']}")
            print(f"   📊 [{item['section']['label'][:20]}] chart {spec.get('type','?')}: {str(spec.get('judul',''))[:40]}")
            chart_path = render_chart(spec, out_dir=out_dir)
            if chart_path:
                # Chart sudah full-frame 1920x1080 dengan branding sendiri →
                # tampilkan statis (tanpa Ken Burns) agar teks/angka tetap tajam.
                clips.append(
                    ImageClip(chart_path).with_duration(per_item)
                    .with_fps(FPS).with_effects([vfx.FadeIn(FADE)])
                )
            else:
                print("   ⚠️  Chart gagal dirender, slide dilewati.")
            continue

        section  = item["section"]
        kw       = _resolve_keyword(section["label"], section["content"], topic, visual_keywords)
        print(f"   📸 [{section['label'][:20]}] → {kw[:55]}")
        img_path = fetch_image(kw)
        if not img_path:
            img_path = fetch_image(" ".join(kw.split()[:3]))
        if not img_path:
            fallback = _section_keywords(section["label"], section["content"], topic)
            if fallback != kw:
                img_path = fetch_image(fallback)
        if not img_path:
            img_path = fetch_image("Indonesia economy business finance")

        stype    = _slide_type(section["label"])
        kb_style = _KB_CYCLE[photo_i % len(_KB_CYCLE)]

        if stype == "cta":
            slide_img = draw_cta_slide(section["content"][:200], img_path)
        else:
            slide_img = draw_fullimage_slide(img_path)

        slide_path = str(out_dir / f"slide_{item['index']:03d}.png")
        slide_img.save(slide_path)
        clips.append(
            _ken_burns_clip(slide_path, per_item, kb_style).with_effects([vfx.FadeIn(FADE)])
        )
        photo_i += 1

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
