"""
Moovon Finance — Generator Shorts 9:16 (mesin penemuan, HOOK-FIRST).

Dua mode:

1) SKRIP MANDIRI (utama, hook-first by design) — Short 100% sendiri, bukan
   potongan video panjang. Narasi diawali kalimat HOOK biar payoff terdengar di
   DETIK 1 (kunci retensi Shorts). TTS + subtitle dibuat baru.
       python shorts.py script <file.txt>
   Format file skrip (lihat contoh assets/short_template.txt):
       TICKER: TLKM
       HOOK: Laba Telkom anjlok 21 persen. Tapi asing malah memborong.
       BODY: Pendapatannya justru naik. Yang bikin laba turun cuma beban sekali...
       CLOSE: Analisis lengkap di channel.   (opsional)

2) PAKAI-ULANG audio video panjang — ambil JENDELA mulai dari kalimat hook
   (BUKAN dari detik 0, biar tak keawali intro/disclaimer), audio & subtitle
   digeser. Cepat, tanpa TTS baru.
       python shorts.py <run_dir> [--hook "Baris 1|Baris 2"] [--start 9] [--cut 45]

Sumber kebenaran desain tetap moovon_theme.py (warna/font/brand).
"""
from __future__ import annotations
import re, sys, subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw

import moovon_theme as T

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "core"))
VW, VH = 1080, 1920          # kanvas Short (9:16)
S = 2                        # supersampling
FPS = 24
MAX_CUT = 56.0               # Shorts wajib < 60 dtk
DEFAULT_CLOSE = "Analisis lengkap di channel."

# Sumber kebenaran: moovon_theme.NON_TICKER_ACRONYMS (dipakai juga oleh
# core/visuals._guess_ticker) — biar tak salah nangkep istilah umum channel
# ini (BUMN, IHSG, dst) sebagai kode emiten sungguhan.
_NON_TICKER_ACRONYMS = T.NON_TICKER_ACRONYMS


# ─── util SRT ─────────────────────────────────────────────────────────────────
def _parse_srt(path: Path):
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = block.splitlines()
        if len(lines) >= 2 and "-->" in lines[1]:
            a, b = lines[1].split("-->")
            cues.append((_ts(a), _ts(b), " ".join(lines[2:]).strip()))
    return cues


def _ts(s: str) -> float:
    s = s.strip().replace(",", ".")
    h, m, rest = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def _fmt(sec: float) -> str:
    h = int(sec // 3600); m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def _pick_window(cues, start_override=None, cut_override=None):
    """Jendela HOOK-FIRST [start, end] dari audio panjang.

    start = awal kalimat hook (pertanyaan pertama) MINUS lead-in kecil, biar
    Short langsung masuk ke inti — BUKAN dari detik 0 yang isinya intro/disclaimer.
    end   = start + hingga ~44 dtk, dipatok ke batas kalimat & MAX_CUT.
    """
    # tentukan start
    if start_override is not None:
        start = max(0.0, float(start_override))
    else:
        start = 0.0
        for a, b, txt in cues:
            if a >= 6 and txt.rstrip().endswith("?"):
                start = max(0.0, a - 0.35)          # lead-in tipis sebelum hook
                break
    # tentukan end
    if cut_override is not None:
        end = start + min(float(cut_override), MAX_CUT)
    else:
        matched_end = None
        for a, b, _ in cues:
            if a >= start and b <= start + 44:
                matched_end = b
        end = min(matched_end if matched_end is not None else (start + 38.0), start + MAX_CUT)
    return start, end


def _write_sub_srt(cues, start: float, end: float, out: Path):
    """Tulis SRT subset [start, end], waktunya DIGESER agar mulai dari 0."""
    lines, n = [], 0
    for a, b, txt in cues:
        if b <= start or a >= end:
            continue
        n += 1
        a2 = max(0.0, a - start)
        b2 = min(b, end) - start
        lines.append(str(n))
        lines.append(f"{_fmt(a2)} --> {_fmt(b2)}")
        lines.append(txt)
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


# ─── util teks/gambar ─────────────────────────────────────────────────────────
def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _rounded(draw, box, r, **kw):
    draw.rounded_rectangle(box, radius=r, **kw)


# ─── render latar Short ───────────────────────────────────────────────────────
def _render_bg(ticker: str, hook_lines: list[str], out: Path, eyebrow: str = "BEDAH SAHAM"):
    W, H = VW * S, VH * S
    img = Image.new("RGB", (W, H), T.RGB["bg"])
    d = ImageDraw.Draw(img)
    mx = 84 * S
    brand = T.RGB["brand"]

    def F(role, size):
        return T.font(role, size * S)

    # ── chrome atas: logo mark + wordmark ──
    top = 96 * S
    ms = 40 * S
    _rounded(d, [mx, top, mx + ms, top + ms], 11 * S, fill=brand)
    bx = mx + ms * 0.28
    for i, h in enumerate((11, 20, 8)):
        bh = h * S
        d.rectangle([bx + i * 7 * S, top + ms - 9 * S - bh,
                     bx + i * 7 * S + 4 * S, top + ms - 9 * S], fill=T.RGB["black"])
    wm_f = F("title", 27)
    d.text((mx + ms + 16 * S, top + ms / 2), "MOOVON", font=wm_f, fill=T.RGB["text"], anchor="lm")
    wlen = d.textlength("MOOVON ", font=wm_f)
    d.text((mx + ms + 16 * S + wlen, top + ms / 2), "FINANCE", font=wm_f, fill=brand, anchor="lm")

    # ── kapsul ticker (kanan atas) — dilewati kalau ticker kosong/"-" ──
    if ticker and ticker not in ("-", "IDX"):
        tf = F("mono_reg", 26)
        tick = f"IDX : {ticker}"
        tw = d.textlength(tick, font=tf)
        pad = 18 * S
        cap_w = tw + pad * 2
        cap_h = 46 * S
        cx1 = W - mx - cap_w
        _rounded(d, [cx1, top - 3 * S, cx1 + cap_w, top - 3 * S + cap_h], cap_h / 2,
                 outline=brand, width=2 * S)
        d.text((cx1 + cap_w / 2, top - 3 * S + cap_h / 2), tick, font=tf, fill=brand, anchor="mm")

    # ── eyebrow ──
    ey = top + ms + 150 * S
    d.line([mx, ey, mx + 40 * S, ey], fill=brand, width=3 * S)
    d.text((mx + 54 * S, ey), eyebrow.upper(), font=F("mono_reg", 27),
           fill=brand, anchor="lm")

    # ── HOOK besar (auto-fit) ──
    y = ey + 60 * S
    max_w = W - mx * 2
    size = 96
    while size > 52:
        hf = T.font("display", size * S)
        wrapped = []
        for ln in hook_lines:
            wrapped += _wrap(d, ln, hf, max_w)
        lh = size * 1.14 * S
        if len(wrapped) * lh <= 760 * S and all(d.textlength(w, font=hf) <= max_w for w in wrapped):
            break
        size -= 4
    hf = T.font("display", size * S)
    lh = size * 1.14 * S
    for ln in hook_lines:
        for w in _wrap(d, ln, hf, max_w):
            d.text((mx, y), w, font=hf, fill=T.RGB["text"], anchor="lm")
            y += lh
        y += 8 * S  # jeda antar-kalimat hook

    # garis citron di bawah hook
    d.line([mx, y + 6 * S, mx + 120 * S, y + 6 * S], fill=brand, width=5 * S)

    # ── CTA bawah + disclaimer (di atas zona subtitle) ──
    # Hierarki: pil SUBSCRIBE = aksi utama (Shorts nyaris tak mengonversi sub
    # tanpa ajakan eksplisit), baru link ke video panjang, lalu disclaimer.
    # Zona subtitle mulai ~320px dari bawah (MarginV=48) → pil aman di 235px.
    pill_f = F("mono_semi", 28)
    pill_t = "SUBSCRIBE"
    pw = d.textlength(pill_t, font=pill_f)
    pad_x, pill_h = 26 * S, 52 * S
    pill_w = pw + pad_x * 2
    pill_y = H - 235 * S
    _rounded(d, [W / 2 - pill_w / 2, pill_y, W / 2 + pill_w / 2, pill_y + pill_h],
             pill_h / 2, fill=brand)
    d.text((W / 2, pill_y + pill_h / 2), pill_t, font=pill_f,
           fill=T.RGB["black"], anchor="mm")

    cta_y = H - 150 * S
    cta_f = F("mono_semi", 30)
    label = "▶  ANALISIS LENGKAP DI CHANNEL"
    lw = d.textlength(label, font=cta_f)
    d.text((W / 2 - lw / 2, cta_y), label, font=cta_f, fill=brand, anchor="lm")
    disc_f = F("mono_reg", 21)
    disc = "Konten edukasi — bukan saran jual atau beli"
    dw = d.textlength(disc, font=disc_f)
    d.text((W / 2 - dw / 2, cta_y + 46 * S), disc, font=disc_f, fill=T.RGB["text_dim"], anchor="lm")

    img = img.resize((VW, VH), Image.LANCZOS)
    img.save(out)
    return out


def _burn(video: Path, srt: Path, out: Path, duration: float | None = None):
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # Portrait: libass men-skala font dari PlayResY=288 → faktor 1920/288 ≈ 6,67.
    # FontSize di sini KECIL karena kanvas 9:16 tinggi. FontSize=8 ≈ 53px (mirip
    # ukuran absolut subtitle video lanskap, pas untuk lebar 1080). MarginV=48
    # ≈ 320px dari bawah → di atas zona CTA. Outline tipis biar tak "gemuk".
    style = (
        "FontName=DejaVu Sans Bold,FontSize=8,"
        "PrimaryColour=&H00ffffff,OutlineColour=&H00000000,"
        "BorderStyle=1,Outline=0.7,Shadow=0.4,ShadowColour=&H80000000,"
        "MarginV=48,MarginL=70,MarginR=70,Alignment=2,Bold=1"
    )
    subs = f"subtitles={srt}:force_style='{style}'"
    if duration and duration > 0:
        # Progress bar citron di TEPI ATAS (bukan bawah seperti video lanskap —
        # tepi bawah Shorts tertutup UI YouTube: scrubber, judul, tombol).
        # Teknik sama dgn core/visuals: overlay dengan x per-frame (t = waktu).
        filter_complex = (
            f"[0:v]{subs}[v];"
            f"color=c=0xC6F24E:s={VW}x8:d={duration:.3f}[bar];"
            f"[v][bar]overlay=x='-w+w*min(t/{duration:.3f}\\,1)':y=0:shortest=1[outv]"
        )
        cmd = [ffmpeg, "-y", "-i", str(video),
               "-filter_complex", filter_complex,
               "-map", "[outv]", "-map", "0:a?",
               "-c:a", "copy", str(out)]
    else:
        cmd = [ffmpeg, "-y", "-i", str(video),
               "-vf", subs, "-c:a", "copy", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"burn gagal:\n{r.stderr[-500:]}")


def _default_hook(title: str) -> list[str]:
    """Fallback hook 3 baris dari judul (pisah di ':' lalu ',')."""
    core = title.split(":", 1)[-1].split("—")[0].strip()
    parts = [p.strip() for p in core.split(",") if p.strip()]
    return parts[:3] or [core]


def _hook_to_lines(hook: str) -> list[str]:
    """Pecah teks HOOK jadi ≤3 baris besar untuk layar (pisah di '|', '—', '.')."""
    if "|" in hook:
        parts = hook.split("|")
    else:
        parts = re.split(r"\s*[—.]\s+", hook)
    parts = [p.strip(" .—") for p in parts if p.strip(" .—")]
    return parts[:3] or [hook.strip()]


def parse_short_script(text: str) -> dict:
    """Parse skrip Short mandiri. Field: TICKER, HOOK, BODY, CLOSE (opsional).

    Narasi = HOOK + BODY + CLOSE (hook di DEPAN → payoff terdengar detik 1).
    """
    fields = {}
    key = None
    for raw in text.splitlines():
        m = re.match(r"^(TICKER|HOOK|BODY|CLOSE|EYEBROW)\s*:\s*(.*)$", raw.strip(), re.IGNORECASE)
        if m:
            key = m.group(1).upper()
            fields[key] = m.group(2).strip()
        elif key and raw.strip():                    # lanjutan baris multi-line
            fields[key] = (fields[key] + " " + raw.strip()).strip()
    hook = fields.get("HOOK", "").strip()
    body = fields.get("BODY", "").strip()
    if not hook or not body:
        raise ValueError("Skrip wajib punya field HOOK dan BODY.")
    close = fields.get("CLOSE", "").strip() or DEFAULT_CLOSE
    eyebrow = fields.get("EYEBROW", "").strip() or "BEDAH SAHAM"
    ticker = fields.get("TICKER", "").strip().upper()
    if "TICKER" not in fields:                        # auto-ekstrak hanya bila tak diisi
        candidates = re.findall(r"\b([A-Z]{4})\b", hook + " " + body)
        ticker = next((c for c in candidates if c not in _NON_TICKER_ACRONYMS), "-")

    def _end(s):                                      # pastikan diakhiri titik
        return s if s.rstrip().endswith((".", "?", "!")) else s.rstrip() + "."
    narration = " ".join(_end(x) for x in (hook, body, close))
    return {"ticker": ticker, "eyebrow": eyebrow, "hook": hook,
            "narration": narration, "hook_lines": _hook_to_lines(hook)}


def make_short_from_script(script_path: str):
    """MODE UTAMA: Short mandiri hook-first dari file skrip pendek."""
    from tts import generate_audio
    from moviepy import AudioFileClip
    from visuals import _kinetic_clip

    sp = Path(script_path)
    if not sp.exists():
        print(f"❌ Skrip tak ada: {sp}"); return None
    info = parse_short_script(sp.read_text(encoding="utf-8"))
    ticker = info["ticker"]

    rd = ROOT / "output" / f"short_{ticker}_{datetime.now():%Y%m%d_%H%M%S}"
    rd.mkdir(parents=True, exist_ok=True)
    print(f"\U0001F3AC Short MANDIRI {ticker}  |  hook: {' / '.join(info['hook_lines'])}")

    audio_p = rd / "audio.mp3"
    generate_audio(info["narration"], str(audio_p))   # tulis audio + audio.srt
    srt_p = audio_p.with_suffix(".srt")
    cues = _parse_srt(srt_p)
    dur = max((b for _, b, _ in cues), default=0.0)
    if dur > 58:
        print(f"   ⚠️  Durasi {dur:.0f}s > 58s — persingkat BODY (Shorts wajib <60s).")

    bg = _render_bg(ticker, info["hook_lines"], rd / "short_bg.png", eyebrow=info["eyebrow"])
    sub_srt = rd / "short.srt"
    _write_sub_srt(cues, 0.0, dur + 1, sub_srt)

    audio = AudioFileClip(str(audio_p))
    # push-in pelan sepanjang durasi — Short hidup tanpa mengganggu hook besar
    clip = _kinetic_clip(str(bg), audio.duration, "in", size=(VW, VH)).with_audio(audio)
    bg_mp4 = rd / "short_bg.mp4"
    clip.write_videofile(str(bg_mp4), fps=FPS, codec="libx264", audio_codec="aac", logger=None)
    audio.close(); clip.close()

    out = rd / "short.mp4"
    print("   \U0001F524 burning subtitle + progress bar...")
    _burn(bg_mp4, sub_srt, out, duration=dur)
    Path(bg_mp4).unlink(missing_ok=True)   # duplikat mentah, sudah menyatu ke `out`
    print(f"✅ Short: {out}  ({dur:.1f}s, {VW}x{VH})")
    return out


def make_short(run_dir: str, hook: str | None = None, cut: float | None = None,
               start: float | None = None, ticker: str | None = None,
               eyebrow: str | None = None):
    """MODE PAKAI-ULANG: Short dari jendela HOOK audio video panjang (hook-first)."""
    from moviepy import AudioFileClip
    from visuals import _kinetic_clip, _guess_ticker

    rd = Path(run_dir)
    audio_p = rd / "audio.mp3"
    srt_p = rd / "audio.srt"
    if not audio_p.exists() or not srt_p.exists():
        print(f"❌ {rd}: butuh audio.mp3 + audio.srt (video panjang v2.0).")
        return None

    # ticker & hook dari metadata bila ada
    title = ""
    meta = rd / "metadata.json"
    if meta.exists():
        import json
        title = json.loads(meta.read_text(encoding="utf-8")).get("title", "")
    if not ticker:
        ticker = _guess_ticker(title, rd.name.upper())

    hook_lines = [h.strip() for h in hook.split("|")] if hook else _default_hook(title)

    cues = _parse_srt(srt_p)
    a0, a1 = _pick_window(cues, start_override=start, cut_override=cut)
    print(f"\U0001F3AC Short {ticker}: jendela {a0:.1f}→{a1:.1f}s ({a1-a0:.1f}s) | "
          f"hook: {' / '.join(hook_lines)}")

    bg = _render_bg(ticker, hook_lines, rd / "short_bg.png",
                    eyebrow=eyebrow or "BEDAH SAHAM")
    sub_srt = rd / "short.srt"
    _write_sub_srt(cues, a0, a1, sub_srt)

    audio = AudioFileClip(str(audio_p)).subclipped(a0, a1)
    clip = _kinetic_clip(str(bg), a1 - a0, "in", size=(VW, VH)).with_audio(audio)
    bg_mp4 = rd / "short_bg.mp4"
    clip.write_videofile(str(bg_mp4), fps=FPS, codec="libx264", audio_codec="aac", logger=None)
    audio.close(); clip.close()

    out = rd / "short.mp4"
    print("   \U0001F524 burning subtitle + progress bar...")
    _burn(bg_mp4, sub_srt, out, duration=a1 - a0)
    Path(bg_mp4).unlink(missing_ok=True)   # duplikat mentah, sudah menyatu ke `out`
    print(f"✅ Short: {out}  ({a1-a0:.1f}s, {VW}x{VH})")
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)

    # Mode SKRIP MANDIRI (utama)
    if args[0] == "script":
        if len(args) < 2:
            print("Pakai: python shorts.py script <file.txt>"); sys.exit(1)
        make_short_from_script(args[1])
        sys.exit(0)

    # Mode PAKAI-ULANG
    run = args[0]
    hook = cut = start = tick = eyeb = None
    if "--hook" in args:
        hook = args[args.index("--hook") + 1]
    if "--cut" in args:
        cut = float(args[args.index("--cut") + 1])
    if "--start" in args:
        start = float(args[args.index("--start") + 1])
    if "--ticker" in args:
        tick = args[args.index("--ticker") + 1]
    if "--eyebrow" in args:
        eyeb = args[args.index("--eyebrow") + 1]
    make_short(run, hook=hook, cut=cut, start=start, ticker=tick, eyebrow=eyeb)
