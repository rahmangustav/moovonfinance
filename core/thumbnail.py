import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BLUE = (30, 100, 200)
DARK_BG = (10, 15, 30)
WHITE = (255, 255, 255)
ACCENT = (0, 200, 150)
YELLOW = (255, 210, 0)

TW, TH = 1280, 720


def get_font(size: int):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _fill_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    r = img.width / img.height
    if r > w / h:
        nw, nh = int(h * r), h
    else:
        nw, nh = w, int(w / r)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def create_thumbnail(
    title: str,
    output_path: str,
    hook_text: str | None = None,
    bg_image_path: str | None = None,
    tag: str = "#InvestasiSaham",
) -> str:
    """hook_text: teks pendek & punchy khusus thumbnail (3-6 kata / satu klausa
    singkat) — BUKAN judul video lengkap, karena thumbnail dibaca kecil dan
    cepat. Kalau tidak diisi, diambil otomatis dari klausa pertama judul."""
    img = Image.new("RGB", (TW, TH), DARK_BG)

    if bg_image_path:
        try:
            bg = _fill_crop(Image.open(bg_image_path).convert("RGB"), TW, TH)
            bg = bg.filter(ImageFilter.GaussianBlur(3))
            bg = ImageEnhance.Brightness(bg).enhance(0.45)
            img.paste(bg, (0, 0))
        except Exception:
            pass

    draw = ImageDraw.Draw(img)

    if not bg_image_path:
        for i in range(TH):
            r = int(BLUE[0] * (1 - i / TH) * 0.4)
            g = int(BLUE[1] * (1 - i / TH) * 0.4)
            b = int(30 + BLUE[2] * (1 - i / TH) * 0.3)
            draw.line([(0, i), (TW, i)], fill=(r, g, b))

    # Dark gradient overlay bottom, so text stays readable over any photo
    for i in range(TH // 2, TH):
        t = (i - TH // 2) / (TH // 2)
        v = int(150 * (t ** 1.4))
        draw.line([(0, i), (TW, i)], fill=(max(0, 10 - v // 20), max(0, 15 - v // 20), max(0, 30 - v // 10)))

    draw.rectangle([(0, 0), (12, TH)], fill=BLUE)

    # Top label — box sized to the actual text (previous fixed-size box clipped
    # the text at wider font metrics)
    font_label = get_font(34)
    label_text = "MOOVON FINANCE"
    bbox = draw.textbbox((0, 0), label_text, font=font_label)
    label_w, label_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 22, 14
    box = (40, 36, 40 + label_w + pad_x * 2, 36 + label_h + pad_y * 2)
    draw.rectangle(box, fill=BLUE)
    draw.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), label_text,
               fill=WHITE, font=font_label, anchor="mm")

    # Hook text pendek — kalau tidak dikasih, ambil klausa pertama judul saja
    if not hook_text:
        hook_text = re_first_clause(title)

    font_title = get_font(104)
    font_small = get_font(84)
    use_f = font_title if len(hook_text) <= 26 else font_small
    wrap_w = 13 if use_f is font_title else 16

    lines = textwrap.wrap(hook_text.upper(), width=wrap_w)[:3]
    line_h = 118 if use_f is font_title else 96
    total_h = len(lines) * line_h
    y = (TH - total_h) // 2 + 30

    for line in lines:
        draw.text((53, y + 4), line, fill=(0, 0, 0), font=use_f)
        draw.text((50, y), line, fill=WHITE, font=use_f)
        y += line_h

    max_line_w = max((draw.textbbox((0, 0), ln, font=use_f)[2] for ln in lines), default=200)
    draw.rectangle([(50, y + 6), (min(50 + max_line_w, TW - 50), y + 14)], fill=ACCENT)

    font_tag = get_font(30)
    draw.text((TW - 50, TH - 44), tag, fill=YELLOW, font=font_tag, anchor="rm")

    img.save(output_path, "JPEG", quality=95)
    print(f"Thumbnail saved: {output_path}")
    return output_path


def re_first_clause(title: str) -> str:
    """Ambil klausa pertama judul (sebelum ':' / ',' / '?') sebagai fallback
    hook text kalau tidak ada hook_text eksplisit."""
    import re
    m = re.split(r"[:,]", title, maxsplit=1)
    clause = m[0].strip()
    return clause if len(clause) <= 40 else clause[:40].rsplit(" ", 1)[0]
