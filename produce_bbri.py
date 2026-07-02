#!/usr/bin/env python3
"""
Produksi video khusus: BBRI (Bank Rakyat Indonesia), target durasi >= 10 menit.
Data & chart dari riset nyata (bukan karangan AI). Dua fase:

  python produce_bbri.py step1   → riset→skrip→voiceover, simpan state, cek durasi
  python produce_bbri.py step2   → render video + thumbnail + upload PUBLIC

Dipisah agar render (mahal) hanya jalan bila audio sudah >= 10 menit.
"""
import os
import re
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(str(Path(__file__).resolve().parent / ".env"))

from groq import Groq
from modules.script_writer import parse_script
from modules.tts import generate_audio
from modules.video_maker import create_video
from modules.thumbnail import create_thumbnail
from modules.youtube_uploader import upload_video, get_youtube_client

OUT_ROOT = Path("output")
STATE = OUT_ROOT / "bbri_state.json"
MIN_DURATION = 600  # 10 menit

# ── Data riset nyata (per Jun 2026) ───────────────────────────────────────────
RISET = """
DATA RESMI BBRI (Bank Rakyat Indonesia) — gunakan HANYA angka ini, jangan mengarang angka lain:
- Laba bersih konsolidasi: 2021 Rp32,22 triliun; 2022 Rp51,17 triliun; 2023 Rp53,15 triliun; 2024 Rp60,30 triliun (rekor tertinggi); 2025 Rp57,13 triliun (turun 5,27% dari 2024).
- Penyebab laba 2025 turun: kenaikan beban pencadangan/provisi seiring kualitas aset. NPL gross naik dari 2,94% ke 3,29%; NPL net naik dari 0,75% ke 0,96% (sikap konservatif).
- Penyaluran kredit 2025: Rp1.521,49 triliun, tumbuh 12,3% YoY.
- Pendapatan bunga 2025: Rp207,8 triliun (+4,27% YoY). Pendapatan bersih Rp151,79 triliun (+5,54%).
- Dana murah (CASA): Giro tumbuh 19,7% YoY, Tabungan tumbuh 7,9% YoY.
- Model bisnis inti: pemberdayaan UMKM & ultra mikro (holding bersama Pegadaian dan PNM/Mekaar).
- Saham BBRI per Juni 2026: harga sekitar Rp2.840; kapitalisasi pasar Rp427,6 triliun; rentang 52 minggu Rp2.540–Rp4.270.
- Dividen: sekitar Rp346 per saham, dividend yield sekitar 12,6% (dibayar dua kali setahun).
- Konsensus 22 analis: rating rata-rata "Buy", target harga 12 bulan Rp3.905 (potensi kenaikan ~46% dari harga sekarang).
"""

# ── Chart dari data riil (disisipkan ke section terkait) ──────────────────────
CHARTS = [
    {"type": "line", "section": "KINERJA 2025",
     "judul": "Laba Bersih BRI 2021–2025 (Rp Triliun)", "sumber": "Laporan Keuangan BRI",
     "x": ["2021", "2022", "2023", "2024", "2025"],
     "y_dict": {"Laba Bersih": [32.22, 51.17, 53.15, 60.30, 57.13]}},
    {"type": "bar", "section": "KENAPA LABA TURUN", "horizontal": True,
     "judul": "Pertumbuhan Bisnis BRI 2025 (% YoY)", "sumber": "Laporan Keuangan BRI 2025",
     "kategori": ["Giro (CASA)", "Kredit", "Tabungan", "Pendapatan Bunga", "Laba Bersih"],
     "nilai": [19.7, 12.3, 7.9, 4.3, -5.3]},
    {"type": "table", "section": "VALUASI SAHAM",
     "judul": "Profil Saham BBRI", "sumber": "Bursa Efek Indonesia, per Jun 2026",
     "headers": ["Indikator", "Nilai"],
     "rows": [
         ["Harga Saham", "Rp2.840"],
         ["Kapitalisasi Pasar", "Rp427,6 T"],
         ["Dividen / Saham", "Rp346"],
         ["Dividend Yield", "12,6%"],
         ["Rentang 52 Minggu", "Rp2.540 - Rp4.270"],
         ["Target Analis", "Rp3.905"],
         ["Potensi Upside", "+46%"],
         ["Rating Konsensus", "Buy"],
     ]},
]

# (label, target_kata, brief) — digenerate per section agar durasi andal >= 10 menit
SECTION_BRIEFS = [
    ("HOOK - 30 detik", 85,
     "Pembuka menohok: BBRI 'saham sejuta umat', bank paling untung di Indonesia, "
     "tapi 2025 labanya JUSTRU turun setelah bertahun-tahun naik terus. Bikin penonton "
     "penasaran: alarm bahaya atau malah peluang emas? Jangan sebut angka detail dulu."),
    ("INTRO - 1 menit", 155,
     "Sapa penonton Moovon Finance & kenalkan topik. Jelaskan singkat siapa BRI: bank BUMN "
     "fokus UMKM & ultra mikro, salah satu bank terbesar dan emiten paling likuid di BEI. "
     "Preview isi: bedah kinerja 2025, alasan laba turun, model bisnis, valuasi & dividen, prospek."),
    ("KINERJA 2025 - 2 menit", 245,
     "Bedah kinerja 2025 dengan angka: laba bersih Rp57,13 triliun, turun 5,27% dari rekor "
     "Rp60,30 triliun (2024). Ceritakan tren laba 2021-2025: Rp32,22T, Rp51,17T, Rp53,15T, "
     "Rp60,30T, lalu Rp57,13T. Tegaskan bisnis inti TETAP tumbuh: pendapatan bunga Rp207,8 "
     "triliun (+4,3%), pendapatan bersih Rp151,79 triliun (+5,5%). Jadi bukan bisnis menyusut."),
    ("KENAPA LABA TURUN - 2 menit", 235,
     "Jelaskan kenapa laba turun padahal bisnis tumbuh: kenaikan beban pencadangan/provisi karena "
     "kualitas kredit memburuk. NPL gross naik 2,94% ke 3,29%, NPL net 0,75% ke 0,96%. Jelaskan "
     "NPL & provisi pakai analogi awam ('dana jaga-jaga kalau kredit macet'). Framing: langkah "
     "konservatif/prudent, bukan tanda kolaps. Sebut kredit tetap tumbuh 12,3% jadi Rp1.521 triliun "
     "dan dana murah CASA (Giro +19,7%, Tabungan +7,9%)."),
    ("BISNIS INTI - 2 menit", 225,
     "Jelaskan mesin uang BRI: pemberdayaan UMKM & ultra mikro lewat holding bersama Pegadaian dan "
     "PNM/Mekaar. Kenapa segmen mikro menguntungkan (margin bunga tebal) tapi juga berisiko (rawan "
     "saat ekonomi lesu, inilah yang menaikkan NPL). Jaringan jutaan nasabah kecil sebagai keunggulan "
     "kompetitif/moat yang sulit ditiru pesaing."),
    ("VALUASI SAHAM - 2 menit", 225,
     "Bahas sisi saham & valuasi: harga sekitar Rp2.840, kapitalisasi pasar Rp427,6 triliun, rentang "
     "52 minggu Rp2.540-Rp4.270 (sekarang dekat batas bawah). Sorot dividen: sekitar Rp346 per saham, "
     "dividend yield sekitar 12,6% (sangat tinggi), dibayar dua kali setahun. Jelaskan arti dividend "
     "yield dengan bahasa awam. Tekankan yield tinggi ini daya tarik utama, tapi ingatkan yield bisa "
     "berubah kalau laba atau harga bergerak."),
    ("PROSPEK - 1 menit", 165,
     "Prospek: konsensus 22 analis rating rata-rata 'Buy', target harga 12 bulan Rp3.905 (potensi naik "
     "sekitar 46% dari harga sekarang). Seimbangkan peluang (harga terdiskon, dividen jumbo, target "
     "analis tinggi) dan risiko (NPL & provisi, ketergantungan segmen mikro, kondisi makro). Jangan "
     "menjanjikan keuntungan pasti."),
    ("KESIMPULAN - 1 menit", 135,
     "Rangkum: BBRI 2025 = laba turun tipis karena provisi naik, TAPI bisnis inti tumbuh, dividen sangat "
     "tinggi, analis masih optimis. Menarik bagi investor pencari dividen yang sabar. Tegaskan lagi ini "
     "edukasi, bukan ajakan beli/jual — lakukan riset sendiri sesuai profil risiko."),
    ("CTA - 30 detik", 75,
     "Ajak like, subscribe Moovon Finance, nyalakan lonceng notifikasi, komentar saham apa yang mau "
     "dibedah berikutnya, dan tonton video lainnya. Energik dan ramah."),
]

TITLE = "Bedah Saham BBRI 2025: Laba Turun, Dividen Jumbo?"

DESCRIPTION = (
    "Bedah lengkap saham BBRI (Bank Rakyat Indonesia) 2025. Untuk pertama kalinya dalam "
    "beberapa tahun, laba bersih BRI turun menjadi Rp57,13 triliun (−5,27%) — tapi apakah ini "
    "alarm bahaya atau justru peluang? Di video ini kita kupas kinerja keuangan 2025, alasan di "
    "balik penurunan laba (kenaikan provisi & NPL), mesin bisnis ultra mikro BRI bersama Pegadaian "
    "dan PNM, valuasi saham, dividend yield yang mencapai ~12,6%, hingga target harga konsensus "
    "analis di Rp3.905. Cocok untuk investor pemula yang ingin memahami saham perbankan dan strategi "
    "dividen di pasar saham Indonesia. Tonton sampai habis biar dapat gambaran utuh risiko dan "
    "peluangnya. Jangan lupa subscribe Moovon Finance untuk analisis saham & keuangan Indonesia lainnya."
)

TAGS = [
    "BBRI", "saham BBRI", "Bank BRI", "Bank Rakyat Indonesia", "analisis saham BBRI",
    "saham dividen", "dividen BBRI", "saham perbankan", "investasi saham", "saham blue chip",
    "IHSG", "bursa efek indonesia", "Moovon Finance", "belajar saham", "analisis fundamental",
]

VISUAL_KEYWORDS = {
    "TITLE": "Bank BRI building logo Indonesia finance",
    "HOOK": "Bank BRI headquarters building Jakarta Indonesia",
    "INTRO": "BRI bank branch Indonesia customers service",
    "KINERJA 2025": "financial growth profit chart Indonesia rupiah money",
    "KENAPA LABA TURUN": "banking risk management analysis meeting Indonesia",
    "BISNIS INTI": "Indonesian small business market vendor UMKM microfinance",
    "VALUASI SAHAM": "stock market trading screen Indonesia stock exchange",
    "PROSPEK": "Indonesia city skyline economy growth investment future",
    "KESIMPULAN": "investor analyzing finance decision Indonesia office",
    "CTA": "subscribe youtube finance channel notification",
}


def _gen_section(client, label, n_words, brief) -> str:
    prompt = (
        "Kamu penulis skrip VOICEOVER channel YouTube finance 'Moovon Finance'. "
        f"Tulis SATU bagian narasi berbahasa Indonesia yang mengalir, santai tapi berbobot, "
        f"sekitar {n_words} kata. HANYA paragraf narasi siap dibaca — TANPA judul, label, poin "
        "bullet, tanda bintang, emoji, atau markdown. Gunakan angka pada DATA apa adanya, jangan "
        "mengarang angka lain.\n\n"
        f"DATA:\n{RISET}\n\nBAGIAN YANG DITULIS ({label}):\n{brief}"
    )
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200, temperature=0.7,
    )
    text = r.choices[0].message.content.strip()
    # Bersihkan sisa markdown/label jika ada
    text = re.sub(r"^\s*\[.*?\]\s*", "", text)
    text = re.sub(r"[#*]+", "", text).strip()
    return text


def step1():
    if not os.getenv("GROQ_API_KEY"):
        sys.exit("GROQ_API_KEY kosong")
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    print("✍️  Menulis skrip BBRI per-section...")
    parts = []
    for label, n_words, brief in SECTION_BRIEFS:
        text = _gen_section(client, label, n_words, brief)
        wc = len(text.split())
        print(f"   [{label:24s}] {wc:4d} kata")
        parts.append(f"[{label}]\n{text}\n")
    script = "\n".join(parts)
    word_count = len(re.sub(r"\[.*?\]", "", script).split())
    print(f"   Total narasi: {word_count} kata")

    description = (DESCRIPTION +
        "\n\n⚠️ Video ini edukasi & analisis, BUKAN ajakan membeli/menjual. "
        "Selalu lakukan riset mandiri sesuai profil risiko. Data per Juni 2026."
        "\n#BBRI #BankBRI #SahamDividen #MoovonFinance")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"bbri_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "script.txt").write_text(script, encoding="utf-8")

    print("🎙️  Membuat voiceover (edge-tts)...")
    audio_path = str(run_dir / "audio.mp3")
    generate_audio(script, audio_path)

    from moviepy import AudioFileClip
    with AudioFileClip(audio_path) as a:
        dur = a.duration
    print(f"   Durasi audio: {dur:.1f} detik ({dur/60:.2f} menit)")

    STATE.write_text(json.dumps({
        "run_dir": str(run_dir), "audio_path": audio_path,
        "title": TITLE, "description": description, "tags": TAGS,
        "script": script, "visual_keywords": VISUAL_KEYWORDS, "charts": CHARTS,
        "topic": "saham BBRI Bank Rakyat Indonesia", "duration": dur, "words": word_count,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    if dur < MIN_DURATION:
        print(f"\n❌ DURASI KURANG dari 10 menit ({dur/60:.2f} mnt). Perpanjang target kata.")
        sys.exit(2)
    print(f"\n✅ STEP1 OK — audio {dur/60:.2f} menit (>= 10 menit). Judul: {TITLE}")
    print("   Lanjut: python produce_bbri.py step2")


def step2():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    run_dir = Path(st["run_dir"])
    print(f"🎬 Render video dari {run_dir} (durasi audio {st['duration']/60:.2f} mnt)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        st["title"], st["script"], st["audio_path"], video_path,
        topic_keywords=st["topic"], visual_keywords=st["visual_keywords"],
        charts=st["charts"],
    )
    print("🖼️  Membuat thumbnail...")
    thumb = str(run_dir / "thumbnail.jpg")
    create_thumbnail(st["title"], thumb)

    print("🚀 Upload ke YouTube (PUBLIC)...")
    vid = upload_video(
        video_path=video_path, title=st["title"],
        description=st["description"], tags=st["tags"], thumbnail_path=thumb,
    )
    print(f"\n✅ LIVE: https://youtube.com/watch?v={vid}")
    (run_dir / "youtube_id.txt").write_text(vid, encoding="utf-8")


def _regen_audio_with_retry(script, audio_path, tries=60, wait=15):
    """edge-tts sering timeout/DNS gagal (jaringan intermiten). Coba banyak kali
    dengan jeda panjang (~default 15 menit total) agar menangkap saat jaringan hidup."""
    import time
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


def redo():
    """Render ulang dengan skrip & chart SAMA, subtitle akurat, upload video baru
    PUBLIC, lalu set video lama → Unlisted."""
    st = json.loads(STATE.read_text(encoding="utf-8"))
    old_run = Path(st["run_dir"])
    old_id = ""
    if (old_run / "youtube_id.txt").exists():
        old_id = (old_run / "youtube_id.txt").read_text(encoding="utf-8").strip()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"bbri_{ts}_fix"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "script.txt").write_text(st["script"], encoding="utf-8")

    print("🎙️  Regenerasi voiceover + subtitle akurat (word-boundary TTS)...")
    audio_path = str(run_dir / "audio.mp3")
    _regen_audio_with_retry(st["script"], audio_path)

    from moviepy import AudioFileClip
    with AudioFileClip(audio_path) as a:
        dur = a.duration
    print(f"   Durasi audio: {dur/60:.2f} menit")
    if dur < MIN_DURATION:
        sys.exit(f"❌ Durasi {dur/60:.2f} mnt < 10 menit")

    print("🎬 Render video (subtitle diperbaiki)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        st["title"], st["script"], audio_path, video_path,
        topic_keywords=st["topic"], visual_keywords=st["visual_keywords"],
        charts=st["charts"],
    )
    print("🖼️  Membuat thumbnail...")
    thumb = str(run_dir / "thumbnail.jpg")
    create_thumbnail(st["title"], thumb)

    print("🚀 Upload video BARU (PUBLIC)...")
    new_id = upload_video(
        video_path=video_path, title=st["title"],
        description=st["description"], tags=st["tags"], thumbnail_path=thumb,
    )
    (run_dir / "youtube_id.txt").write_text(new_id, encoding="utf-8")
    print(f"✅ Video baru LIVE: https://youtube.com/watch?v={new_id}")

    if old_id:
        print(f"🔒 Set video lama {old_id} → Unlisted...")
        try:
            yt = get_youtube_client()
            yt.videos().update(part="status", body={
                "id": old_id,
                "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
            }).execute()
            print("   ✅ Video lama sekarang Unlisted")
        except Exception as e:
            print(f"   ⚠️  Gagal unlist video lama: {str(e)[:200]}")

    st.update({"run_dir": str(run_dir), "audio_path": audio_path, "duration": dur,
               "youtube_id": new_id, "old_youtube_id": old_id})
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ SELESAI. Baru: {new_id} (public) | Lama: {old_id} (unlisted)")


def _retry(fn, tries=50, wait=15, what="operasi"):
    """Ulang fn sampai sukses (jaringan intermiten)."""
    import time
    for i in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            print(f"   ({what} percobaan {i}/{tries} gagal: {type(e).__name__})", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"{what} gagal setelah {tries} percobaan (jaringan?)")


def upload_only():
    """Upload video hasil render yang SUDAH jadi (tanpa render ulang) + set video
    lama Unlisted. Dipakai kalau render sukses tapi upload gagal karena jaringan."""
    st = json.loads(STATE.read_text(encoding="utf-8"))

    # run_dir _fix terbaru yang punya video.mp4
    run_dir = next((f for f in sorted(OUT_ROOT.glob("bbri_*_fix"), reverse=True)
                    if (f / "video.mp4").exists()), None)
    if run_dir is None:
        sys.exit("❌ Tidak ada video.mp4 hasil render di folder *_fix")
    video_path = str(run_dir / "video.mp4")
    thumb = str(run_dir / "thumbnail.jpg")
    print(f"📦 Video jadi: {video_path} ({Path(video_path).stat().st_size//1048576} MB)")

    # id video lama (yang public salah subtitle)
    old_id = ""
    old_idfile = Path(st["run_dir"]) / "youtube_id.txt"
    if old_idfile.exists():
        old_id = old_idfile.read_text(encoding="utf-8").strip()

    print("🚀 Upload video BARU (PUBLIC) — dengan retry jaringan...")
    new_id = _retry(lambda: upload_video(
        video_path=video_path, title=st["title"],
        description=st["description"], tags=st["tags"], thumbnail_path=thumb,
    ), what="upload")
    (run_dir / "youtube_id.txt").write_text(new_id, encoding="utf-8")
    print(f"✅ Video baru LIVE: https://youtube.com/watch?v={new_id}")

    if old_id and old_id != new_id:
        print(f"🔒 Set video lama {old_id} → Unlisted...")
        def _unlist():
            yt = get_youtube_client()
            yt.videos().update(part="status", body={
                "id": old_id,
                "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
            }).execute()
        try:
            _retry(_unlist, tries=20, what="unlist")
            print("   ✅ Video lama sekarang Unlisted")
        except Exception as e:
            print(f"   ⚠️  Gagal unlist video lama: {str(e)[:150]}")

    st.update({"run_dir": str(run_dir), "youtube_id": new_id, "old_youtube_id": old_id})
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ SELESAI. Baru: {new_id} (public) | Lama: {old_id} (unlisted)")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "step1"
    {"step1": step1, "step2": step2, "redo": redo, "upload_only": upload_only}[phase]()
