import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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


def create_thumbnail(title: str, output_path: str) -> str:
    img = Image.new("RGB", (TW, TH), DARK_BG)
    draw = ImageDraw.Draw(img)

    # Background gradient
    for i in range(TH):
        r = int(BLUE[0] * (1 - i / TH) * 0.4)
        g = int(BLUE[1] * (1 - i / TH) * 0.4)
        b = int(30 + BLUE[2] * (1 - i / TH) * 0.3)
        draw.line([(0, i), (TW, i)], fill=(r, g, b))

    # Left accent bar
    draw.rectangle([(0, 0), (12, TH)], fill=BLUE)

    # Top label
    font_label = get_font(36)
    draw.rectangle([(50, 40), (320, 90)], fill=BLUE)
    draw.text((185, 65), "MOOVON FINANCE", fill=WHITE, font=font_label, anchor="mm")

    # Main title
    font_title = get_font(88)
    font_small = get_font(72)

    words = title.split()
    if len(title) > 35:
        font_use = font_small
        wrap_width = 22
    else:
        font_use = font_title
        wrap_width = 18

    lines = textwrap.wrap(title, width=wrap_width)
    total_h = len(lines) * 100
    y = (TH - total_h) // 2 - 20

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_use)
        w = bbox[2] - bbox[0]
        # Shadow
        draw.text((50 + 3, y + 3), line, fill=(0, 0, 0), font=font_use)
        draw.text((50, y), line, fill=WHITE, font=font_use)
        y += 100

    # Accent underline
    draw.rectangle([(50, y + 10), (min(50 + len(title) * 40, TW - 50), y + 18)], fill=ACCENT)

    # Bottom tag
    font_tag = get_font(32)
    draw.text((TW - 60, TH - 50), "#InvestasiSaham", fill=YELLOW, font=font_tag, anchor="rm")

    img.save(output_path, "JPEG", quality=95)
    print(f"Thumbnail saved: {output_path}")
    return output_path
