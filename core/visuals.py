import re
from datetime import datetime
from pathlib import Path
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips, vfx

# Video FULL ON-BRAND v2.0 "SINYAL": semua slide dirender oleh render_slides.py
# (cover + section + valuasi/gauge + snapshot + penutup) + chart tema gelap.
# TIDAK ADA lagi foto/ddgs/Ken Burns — jalur lama (draw_*_slide, image_fetcher,
# keyword pencarian foto) sudah dihapus. Sumber kebenaran desain: moovon_theme.py.

WIDTH, HEIGHT = 1920, 1080
FPS  = 24
FADE = 0.6


# ─── Section parsing & label ──────────────────────────────────────────────────

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
    Pertahankan: TTS/audio, subtitle burn dari SRT, penyisipan chart, timing.

    (visual_keywords dipertahankan di signature demi kompatibilitas pemanggil
    lama; sudah tak dipakai sejak video tanpa foto.)"""
    import sys
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "core"))
    import render_slides as RS
    import moovon_theme as MT
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
