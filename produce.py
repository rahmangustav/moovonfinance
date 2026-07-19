#!/usr/bin/env python3
"""
Produksi video Moovon Finance — sistem generik (v2, dibangun 2026-07-04).

Beda dari sistem lama: TIDAK ADA lagi file produce_<topik>.py per video.
Semua topik dibaca langsung dari assets/draft_script_moovon.md + state.json.

Alur:
  1. Riset + tulis draft (dikerjakan Claude di sesi chat) -> assets/draft_script_moovon.md
  2. User approve ("Data aman, lanjut render")
  3. python produce.py render   -> TTS + visual (foto+PIL, auto) + chart + compile + thumbnail
  4. Review video di output/<run_dir>/video.mp4
  5. Tulis output/<run_dir>/metadata.json (title/description/tags) setelah user approve
  6. python produce.py upload <run_dir> [--privacy public|unlisted|private]

Format draft (assets/draft_script_moovon.md) yang dibaca parser:
  # DRAFT SCRIPT — <judul video>
  **Topic keywords:** <kata kunci pendek untuk fallback pencarian foto>
  ...
  ## SCRIPT
  ### <LABEL> (mm:ss–mm:ss)
  <narasi...>
  > [VISUAL/CHART: ...]   <- baris anotasi, diabaikan (bukan dibacakan)
  ...
  ## CHARTS: (...)
  ```json
  [ {...spec chart...}, ... ]
  ```

Blok OPSIONAL elemen tanda tangan v2.0 (kalau ada, otomatis jadi slide;
angka WAJIB dari riset, bukan karangan):
  ## VALUATION:                 <- gauge Margin of Safety, sisip setelah section valuasi
  ```json
  {"harga": 5800, "nilai_wajar": 9150, "catatan": "..."}
  ```
  ## SNAPSHOT:                  <- grid metrik, sisip setelah section fundamental
  ```json
  {"judul": "BBCA — Kuartal I 2026",
   "metrics": [["Laba bersih","14,7 T","up"], ["NPL","1,8%","up"], ...]}
  ```
  (metrics = [label, nilai, warna]; warna: "up"/"down"/"neutral"/null)
"""
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Zona waktu penonton (WIB / GMT+7). Slot upload default: 17:30 WIB pada
# Selasa/Rabu/Kamis — publish 1-2 jam sebelum puncak nonton malam 19:00-22:00.
WIB = timezone(timedelta(hours=7))
DEFAULT_SLOT_HOUR, DEFAULT_SLOT_MINUTE = 17, 30
DEFAULT_SLOT_DAYS = (1, 2, 3)  # Senin=0 ... Minggu=6 -> Selasa,Rabu,Kamis


def _next_upload_slot(hour=DEFAULT_SLOT_HOUR, minute=DEFAULT_SLOT_MINUTE,
                      days=DEFAULT_SLOT_DAYS) -> datetime:
    """Cari slot upload terdekat (WIB) di hari yang diizinkan, minimal ~15 menit
    dari sekarang biar YouTube sempat memproses sebelum publishAt."""
    now = datetime.now(WIB)
    for add in range(0, 9):
        cand = (now + timedelta(days=add)).replace(
            hour=hour, minute=minute, second=0, microsecond=0)
        if cand.weekday() in days and cand > now + timedelta(minutes=15):
            return cand
    return now + timedelta(hours=1)


def _parse_slot(value: str) -> datetime:
    """'next' -> slot terdekat; atau 'YYYY-MM-DD HH:MM' (dianggap WIB)."""
    v = value.strip()
    if v.lower() == "next":
        return _next_upload_slot()
    dt = datetime.strptime(v, "%Y-%m-%d %H:%M")
    return dt.replace(tzinfo=WIB)


def _to_publish_at(dt_wib: datetime) -> str:
    """datetime WIB -> string RFC3339 UTC (format publishAt YouTube)."""
    return dt_wib.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

ROOT       = Path(__file__).resolve().parent
DRAFT_PATH = ROOT / "assets" / "draft_script_moovon.md"
STATE_PATH = ROOT / "state.json"
OUT_ROOT   = ROOT / "output"

sys.path.insert(0, str(ROOT / "core"))


# ─── Parser draft markdown -> title/topic/script/charts ──────────────────────

_HEADING_RE = re.compile(
    r"^###\s+(.+?)\s*\(\d{1,2}:\d{2}[–\-]\d{1,2}:\d{2}\)\s*$", re.MULTILINE
)


def _fenced_json_after(text: str, heading_kw: str):
    """Ambil blok ```json ...``` PERTAMA setelah heading '## <heading_kw>'.
    Return objek/list Python, atau None kalau heading/blok tak ada atau JSON rusak.
    Dipakai untuk blok opsional CHARTS / VALUATION / SNAPSHOT — anchored ke heading
    biar tidak saling rebutan (mis. array metrics snapshot dikira charts)."""
    m = re.search(
        rf"^##\s*{heading_kw}\b.*?```json\s*(.+?)\s*```",
        text, re.MULTILINE | re.DOTALL,
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def parse_draft(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    title_m = re.search(r"^#\s*DRAFT SCRIPT\s*[—-]\s*(.+)$", text, re.MULTILINE)
    if not title_m:
        raise ValueError("Draft tidak punya heading '# DRAFT SCRIPT — <judul>'")
    title = title_m.group(1).strip()

    topic_m = re.search(r"^\*\*Topic keywords:\*\*\s*(.+)$", text, re.MULTILINE)
    topic = topic_m.group(1).strip() if topic_m else title

    thumb_m = re.search(r"^\*\*Thumbnail text:\*\*\s*(.+)$", text, re.MULTILINE)
    thumbnail_text = thumb_m.group(1).strip() if thumb_m else None

    # Override opsional utk video non-bedah-emiten (mis. evergreen/edukasi konsep):
    #   **Eyebrow:** PANDUAN PEMULA   → ganti label kecil di cover (default "Bedah Saham")
    #   **Ticker:** EDUKASI           → ganti isi kapsul kanan-atas (kosongkan = sembunyikan)
    eyebrow_m = re.search(r"^\*\*Eyebrow:\*\*\s*(.+)$", text, re.MULTILINE)
    eyebrow = eyebrow_m.group(1).strip() if eyebrow_m else None
    ticker_m = re.search(r"^\*\*Ticker:\*\*\s*(.+)$", text, re.MULTILINE)
    ticker_override = ticker_m.group(1).strip() if ticker_m else None
    if ticker_override and ticker_override.lower() in {"none", "-", "kosong", "tanpa"}:
        ticker_override = ""   # sembunyikan kapsul ticker (video non-emiten)

    script_m = re.search(r"^## SCRIPT\s*$(.*?)^---\s*$", text, re.MULTILINE | re.DOTALL)
    if not script_m:
        raise ValueError("Draft tidak punya section '## SCRIPT' yang diakhiri '---'")
    script_block = script_m.group(1)

    headings = list(_HEADING_RE.finditer(script_block))
    if not headings:
        raise ValueError("Tidak ada heading '### LABEL (mm:ss–mm:ss)' di dalam ## SCRIPT")

    sections = []
    for i, m in enumerate(headings):
        # Simpan heading APA ADANYA (termasuk bagian deskriptif setelah " — ")
        # supaya slide bisa tampilkan judul yang informatif, bukan cuma
        # "SECTION 1" generik. Chart-matching tetap jalan karena cocokin
        # substring ("SECTION 1" tetap ada di dalam label penuh).
        label = m.group(1).strip()
        start = m.end()
        end   = headings[i + 1].start() if i + 1 < len(headings) else len(script_block)
        body  = script_block[start:end]
        # buang baris anotasi "> [...]" dan baris kosong berlebih
        lines = [ln for ln in body.split("\n") if not ln.strip().startswith(">")]
        narration = "\n".join(lines).strip()
        sections.append((label, narration))

    # visuals.parse_sections cuma terima [A-Za-z0-9\s\-] di dalam tanda kurung
    # siku, jadi bersihkan em-dash/tanda baca lain dari label sebelum ditulis
    # (tetap dipertahankan sebagai teks biasa, cuma karakternya disederhanakan).
    def _sanitize_label(label: str) -> str:
        label = label.replace("—", "-").replace("–", "-")
        return re.sub(r"[^A-Za-z0-9\s\-]", "", label).strip()

    script_plain = "\n\n".join(
        f"[{_sanitize_label(label)}]\n{narration}" for label, narration in sections
    )

    charts = _fenced_json_after(text, "CHARTS")
    if charts is None:
        # fallback lama: array json pertama di mana pun (draft tanpa heading CHARTS)
        charts_m = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
        charts = json.loads(charts_m.group(1)) if charts_m else []

    # Blok opsional elemen tanda tangan v2.0 (boleh tidak ada):
    #   ## VALUATION:  ```json {"harga":.., "nilai_wajar":.., "catatan":".."} ```
    #   ## SNAPSHOT:   ```json {"judul":"..", "metrics":[["Laba","14,7 T","up"],..]} ```
    valuation = _fenced_json_after(text, "VALUATION")
    snapshot  = _fenced_json_after(text, "SNAPSHOT")

    return {
        "title": title, "topic": topic, "script": script_plain,
        "charts": charts, "thumbnail_text": thumbnail_text,
        "valuation": valuation, "snapshot": snapshot,
        "eyebrow": eyebrow, "ticker_override": ticker_override,
    }


# ─── State helpers ────────────────────────────────────────────────────────────

def _load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(st: dict) -> None:
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def _audio_with_retry(script: str, audio_path: str, tries: int = 60, wait: int = 15):
    from tts import generate_audio
    for i in range(1, tries + 1):
        try:
            segs = generate_audio(script, audio_path)
            if segs:
                return segs
            print(f"   (percobaan {i}/{tries}: 0 segmen, ulangi)", flush=True)
        except Exception as e:
            print(f"   (percobaan {i}/{tries} gagal: {type(e).__name__})", flush=True)
        time.sleep(wait)
    raise RuntimeError("TTS gagal setelah banyak percobaan (jaringan mati terus)")


# ─── Commands ─────────────────────────────────────────────────────────────────

def render():
    from visuals import create_video

    draft = parse_draft(DRAFT_PATH)
    print(f"✍️  Judul: {draft['title']}")
    print(f"   Topic keywords: {draft['topic']}")
    extras = []
    if draft.get("valuation"): extras.append("gauge valuasi")
    if draft.get("snapshot"):  extras.append("snapshot fundamental")
    print(f"   {len(draft['charts'])} chart, script {len(draft['script'])} karakter"
          + (f" (+{', '.join(extras)})" if extras else ""))

    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "script.txt").write_text(draft["script"], encoding="utf-8")

    print("🎙️  Membuat voiceover (edge-tts, word-boundary subtitle)...")
    audio_path = str(run_dir / "audio.mp3")
    _audio_with_retry(draft["script"], audio_path)

    from moviepy import AudioFileClip
    with AudioFileClip(audio_path) as a:
        dur = a.duration
    print(f"   Durasi audio: {dur:.1f} detik ({dur/60:.2f} menit)")

    print(f"🎬 Render video ({dur/60:.2f} menit)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        draft["title"], draft["script"], audio_path, video_path,
        topic_keywords=draft["topic"], charts=draft["charts"],
        valuation=draft.get("valuation"), snapshot=draft.get("snapshot"),
        eyebrow=draft.get("eyebrow"), ticker_override=draft.get("ticker_override"),
    )

    # Thumbnail on-brand: pakai slide cover v2.0 yang sudah dirender create_video
    # (1920x1080 -> 1280x720 JPG). Konsisten dengan identitas video, tanpa foto.
    print("🖼️  Membuat thumbnail on-brand (dari slide cover v2.0)...")
    thumb_path  = str(run_dir / "thumbnail.jpg")
    cover_slide = run_dir / "slide_cover.png"
    if cover_slide.exists():
        from PIL import Image as _Img
        (_Img.open(cover_slide).convert("RGB")
             .resize((1280, 720), _Img.LANCZOS)
             .save(thumb_path, quality=90))
        print(f"   ✅ Thumbnail: {thumb_path}")
    else:
        print("   ⚠️  slide_cover.png tak ada — thumbnail dilewati (YouTube pilih frame otomatis).")

    (run_dir / "run_state.json").write_text(json.dumps({
        "title": draft["title"], "topic": draft["topic"],
        "duration": dur, "rendered_at": datetime.now().isoformat(timespec="minutes"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    st = _load_state()
    st["phase"] = "selesai_render_menunggu_review"
    st["last_run_dir"] = str(run_dir.relative_to(ROOT))
    _save_state(st)

    print(f"\n✅ SELESAI RENDER (tanpa upload). Video: {video_path}")
    print("   Review dulu videonya. Setelah oke, siapkan metadata.json di folder run lalu:")
    print(f"   python produce.py upload {run_dir.relative_to(ROOT)}")


def upload(run_dir_arg: str, privacy: str = "public", at: str | None = None):
    """Upload video. Kalau `at` diisi ('next' atau 'YYYY-MM-DD HH:MM' WIB),
    video di-upload sebagai TERJADWAL: privasi 'private' + publishAt, lalu
    YouTube otomatis publish (jadi public) pas waktu itu."""
    from youtube_uploader import get_youtube_client
    from googleapiclient.http import MediaFileUpload

    run_dir = ROOT / run_dir_arg
    meta_path = run_dir / "metadata.json"
    if not meta_path.exists():
        print(f"❌ {meta_path} belum ada. Buat dulu file metadata.json berisi "
              '{"title": "...", "description": "...", "tags": ["...", "..."]}')
        return

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    video_path = run_dir / "video.mp4"
    thumb_path = run_dir / "thumbnail.jpg"

    # Guard: YouTube menolak judul kosong atau > 100 karakter (error invalidTitle).
    # Gagal cepat sebelum mengunggah 16 MB, biar jelas apa yang harus diperbaiki.
    title = (meta.get("title") or "").strip()
    if not title:
        print("❌ metadata.json: field 'title' kosong. Isi judul dulu.")
        return
    if len(title) > 100:
        print(f"❌ Judul {len(title)} karakter — batas YouTube 100. Perpendek 'title' di "
              f"{meta_path} (title_options berisi alternatif yang lebih pendek).")
        return

    # Penjadwalan: video harus di-upload 'private' + publishAt (UTC RFC3339).
    # 'now' = escape-hatch untuk publish seketika (jarang dipakai).
    slot_wib = publish_at = None
    if at and at.strip().lower() != "now":
        slot_wib = _parse_slot(at)
        publish_at = _to_publish_at(slot_wib)

    status = {"privacyStatus": "private" if publish_at else privacy}
    if publish_at:
        status["publishAt"] = publish_at

    if publish_at:
        print(f"🚀 Upload TERJADWAL {video_path} ({video_path.stat().st_size / 1e6:.1f} MB)")
        print(f"   ⏰ Publish otomatis: {slot_wib:%A %d %b %Y, %H:%M} WIB  (publishAt {publish_at})")
    else:
        print(f"🚀 Upload {video_path} ({video_path.stat().st_size / 1e6:.1f} MB) — {privacy}...")

    youtube = get_youtube_client()
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "categoryId": "27",  # Education — kanal edukasi analisis saham, bukan berita/politik
            "defaultLanguage": "id",       # bahasa judul/deskripsi
            "defaultAudioLanguage": "id",  # bahasa AUDIO — wajib 'id' biar YouTube tak salah kira Inggris
        },
        "status": status,
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    video_id = response["id"]
    print(f"Video uploaded: https://youtube.com/watch?v={video_id}")

    if thumb_path.exists():
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()
            print("Thumbnail uploaded.")
        except Exception as e:
            print(f"⚠️  Thumbnail dilewati: {e}")

    if publish_at:
        print(f"\n✅ TERJADWAL: https://youtube.com/watch?v={video_id}")
        print(f"   Akan publik otomatis {slot_wib:%a %d %b %H:%M} WIB. Ubah/awal-kan lewat YouTube Studio kalau perlu.")
    else:
        print(f"\n✅ LIVE: https://youtube.com/watch?v={video_id}")

    st = _load_state()
    st.setdefault("history", []).append({
        "topic": meta["title"], "youtube_id": video_id,
        "uploaded": datetime.now().strftime("%Y-%m-%d"), "run_dir": None,
        "scheduled_for": (slot_wib.isoformat() if slot_wib else None),
    })
    st["phase"] = "idle"
    _save_state(st)


if __name__ == "__main__":
    USAGE = ("Pakai:\n"
             "  python produce.py render\n"
             "  python produce.py upload <run_dir>                      # PUBLIK: otomatis dijadwalkan ke slot prime berikutnya (17:30 WIB Sel/Rab/Kam)\n"
             "  python produce.py upload <run_dir> --at now             # publish SEKETIKA (lewati pengaman jam)\n"
             "  python produce.py upload <run_dir> --at next            # jadwal ke slot berikutnya (17:30 WIB Sel/Rab/Kam)\n"
             '  python produce.py upload <run_dir> --at "2026-07-07 17:30"  # jadwal ke waktu spesifik (WIB)\n'
             "  python produce.py upload <run_dir> --privacy unlisted   # unlisted/private: publish langsung, tanpa jadwal\n"
             "  python produce.py short <run_dir> [--hook \"a|b\"] [--start N] [--cut N] [--ticker XXXX] [--eyebrow \"TEKS\"]  # Short 9:16 dari HOOK video panjang (pakai-ulang audio)\n"
             "  python produce.py short script <file.txt>               # Short mandiri (TTS+subtitle baru, hook-first)")
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "render":
        render()
    elif cmd == "upload":
        if len(sys.argv) < 3:
            print(USAGE)
            sys.exit(1)
        priv = "public"
        if "--privacy" in sys.argv:
            priv = sys.argv[sys.argv.index("--privacy") + 1]
        at = None
        if "--at" in sys.argv:
            at = sys.argv[sys.argv.index("--at") + 1]
        # PENGAMAN JAM: upload PUBLIK tanpa --at gampang keceplosan publish jam
        # jelek (mis. tengah malam -> 0 views). Default-kan ke slot prime
        # berikutnya (17:30 WIB Sel/Rab/Kam). Pakai `--at now` kalau memang
        # sengaja mau publish seketika. unlisted/private tak terpengaruh.
        if at is None and priv == "public":
            at = "next"
            slot = _next_upload_slot()
            print(f"ℹ️  Upload publik tanpa --at → otomatis dijadwalkan ke slot prime "
                  f"{slot:%A %d %b, %H:%M} WIB.\n    (pakai `--at now` untuk publish seketika, "
                  f"atau `--at \"YYYY-MM-DD HH:MM\"` untuk waktu lain)")
        upload(sys.argv[2], priv, at)
    elif cmd == "short":
        # Delegasi ke shorts.py (mesin penemuan 9:16). Dua mode sama persis dgn
        # CLI shorts.py: 'short script <file>' = Short mandiri (TTS baru),
        # 'short <run_dir> [flags]' = pakai-ulang audio video panjang.
        import shorts
        sargs = sys.argv[2:]
        if not sargs:
            print(USAGE)
            sys.exit(1)
        if sargs[0] == "script":
            if len(sargs) < 2:
                print(USAGE)
                sys.exit(1)
            shorts.make_short_from_script(sargs[1])
        else:
            run = sargs[0]
            hook = cut = start = tick = eyeb = None
            if "--hook" in sargs:   hook  = sargs[sargs.index("--hook") + 1]
            if "--cut" in sargs:    cut   = float(sargs[sargs.index("--cut") + 1])
            if "--start" in sargs:  start = float(sargs[sargs.index("--start") + 1])
            if "--ticker" in sargs: tick  = sargs[sargs.index("--ticker") + 1]
            if "--eyebrow" in sargs: eyeb = sargs[sargs.index("--eyebrow") + 1]
            shorts.make_short(run, hook=hook, cut=cut, start=start, ticker=tick,
                              eyebrow=eyeb)
    else:
        print(f"Command tidak dikenal: {cmd}")
        print(USAGE)
        sys.exit(1)
