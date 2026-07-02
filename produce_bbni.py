#!/usr/bin/env python3
"""
Produksi video: Bedah Saham BBNI (script approved user 2026-07-03, opsi visual A:
slide pack PIL on-brand penuh — quota Canva habis hari itu).

  python produce_bbni.py step1   → voiceover + subtitle
  python produce_bbni.py step2   → compile: slide pack + chart + subtitle (TANPA upload)
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from modules.tts import generate_audio
from modules.video_maker import create_video

OUT_ROOT = Path("output")
STATE = OUT_ROOT / "bbni_state.json"

TITLE = "Bedah Saham BBNI: Turun 20%, Kok Analis Kompak Bilang Beli?"

SCRIPT = """
[HOOK - 35 detik]
Dari tiga bank BUMN raksasa, dua udah kita bedah. Nah, yang ketiga ini, sahamnya paling babak belur. Minus 20 persen dalam setahun. Lebih dalam dari BRI, lebih dalam dari Mandiri. Tapi anehnya, dari 19 analis yang ngeliatin saham ini, sembilan belas-sembilan belasnya bilang beli. Nol yang bilang jual. Saham yang paling dibuang pasar, tapi paling kompak direkomendasiin analis. Ada yang gak nyambung, dan hari ini kita cari tau kenapa. Seperti biasa, konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan atau financial advice. Keputusan tetap di tangan lo.

[PROFIL BNI - 75 detik]
Kenalan dulu. BNI itu bank BUMN paling senior. Berdiri 5 Juli 1946, bulan ini genap 80 tahun. Posisinya unik. Kalau BRI rajanya kredit mikro, dan Mandiri rajanya korporasi domestik, BNI main di tengah. Kredit korporasi, plus satu keunggulan yang jarang dibahas, bisnis internasional. BNI itu satu-satunya bank Indonesia dengan jaringan kantor luar negeri yang signifikan. Dari Singapura, Tokyo, sampai New York. Ditambah mesin digital barunya, aplikasi wondr, yang lagi digenjot buat ngejar dana murah. Ukurannya memang paling kecil di antara bertiga. Tapi justru itu yang bikin ceritanya menarik. Pasar menghargai saham ini paling murah, dan sekarang kita cek, apakah itu adil.

[KINERJA - 2 menit]
Kita jujur dulu. 2025 bukan tahun yang bagus buat BNI. Laba bersihnya 20,04 triliun rupiah, turun 7,15 persen dari tahun sebelumnya. Satu-satunya dari tiga bank besar yang labanya turun sedalam itu. Likuiditas ketat, biaya dana mahal, margin kejepit. Dan ini alasan pertama kenapa sahamnya dihukum pasar. Tapi masuk 2026, arahnya berbalik. Kuartal pertama, laba 5,66 triliun rupiah, naik 5 persen dibanding tahun lalu. Dan yang lebih penting dari angka labanya, adalah mesin di baliknya. Kredit tumbuh 20,1 persen. Paling kencang di antara bank besar. Dana murah alias CASA melonjak 26,6 persen, sebagian besar berkat aplikasi wondr tadi. Dan rasio kredit macet justru membaik ke 1,9 persen. Jadi polanya kebaca. 2025 kena pukul. 2026 mulai bangkit. Tapi harga sahamnya, masih diparkir di posisi kena pukul.

[KENAPA PALING TERTEKAN - 100 detik]
Empat tekanan makro yang kita bahas di video Mandiri masih berlaku semua. BI Rate 5,75 persen, asing keluar, sentimen politik, dan tarif Amerika. Tapi BBNI dapet bonus tekanan yang spesifik buat dia. Pertama, laba 2025-nya beneran turun. Jadi pasar punya alasan fundamental, bukan cuma sentimen. Kedua, margin bunganya paling tertekan, karena perebutan dana yang bikin biaya mahal. Ketiga, ada kenaikan tipis kredit bermasalah di segmen kecil dan konsumer. Dan keempat, ini menarik, manajemennya sendiri terbuka bilang, dalam skenario terburuk, minyak dunia 150 dolar dan rupiah tembus 20 ribu, NPL bisa naik 1,6 poin. Transparansi kayak gini sebenarnya sehat. Tapi buat investor yang penakut, malah bikin makin mundur. Hasilnya ya itu tadi. Minus 20 persen setahun. Terdalam di kelasnya.

[DIVIDEN DAN VALUASI - 90 detik]
Sekarang sisi lain timbangannya. Untuk tahun buku 2025, BNI bagi dividen 13,02 triliun rupiah. Atau 349,41 rupiah per saham. Dan itu 65 persen dari seluruh labanya. Payout ratio segede itu artinya manajemen pede sama kekuatan modalnya. Di harga sekarang, yield-nya sekitar 11 persen. Buat konteks, itu di atas kupon SBN mana pun yang pernah kita bahas. Walau tentu, risikonya beda kelas. Kualitas asetnya gimana? NPL 1,9 persen. Bukan sekelas Mandiri yang 0,96. Tapi jauh lebih aman dari BRI yang 3,29. Inget, beda medan main. Jadi sekarang kita punya bank yang dividennya jumbo, NPL-nya menengah tapi sehat, kreditnya tumbuh paling kencang. Di harga yang paling didiskon pasar.

[KATA ANALIS - 60 detik]
Balik ke teka-teki pembuka. 19 analis, 19 bilang beli, nol jual. Target harga rata-ratanya 4.788 rupiah. Sekitar 51 persen di atas harga sekarang. Yang paling konservatif di 3.800. Yang paling optimis 5.500. Tapi dua catatan wajib. Satu, sebagian target itu dibuat sebelum koreksi terakhir. Buktinya, RHB Sekuritas baru aja mangkas targetnya dari 5.250 ke 4.560. Walau rekomendasinya tetap beli. Dua, kompak bukan berarti benar. Analis menilai fundamental. Sedangkan yang nekan saham ini sekarang, sebagian besar faktor makro yang gak bisa dikontrol siapa pun.

[KESIMPULAN - 45 detik]
Jadi, BBNI hari ini. Bank 80 tahun yang lagi transisi. Laba sempat jeblok di 2025, tapi kuartal pertama 2026, semua mesinnya nyala lagi. Kredit, dana murah, kualitas aset. Sahamnya paling murah di antara bank besar, karena pasar masih ngeliat kaca spion, bukan kaca depan. Buat yang percaya pemulihannya berlanjut dan tahan gejolak, ini tipe saham yang biasa disebut turnaround story dengan dividen gede. Buat yang gak tahan liat portofolio merah berbulan-bulan, mungkin bukan tempat yang nyaman. Sekali lagi, ini edukasi, bukan rekomendasi. Riset sendiri, sesuaikan profil risiko lo.

[CTA - 30 detik]
Trilogi bank BUMN resmi selesai. BRI, Mandiri, BNI. Kalau lo mau gw bikinin video perbandingan langsung ketiganya, atau bedah bank swasta kayak BCA, tulis di komentar. Like, subscribe, nyalain lonceng, biar makin banyak orang Indonesia yang melek finansial. Sampai ketemu di video Moovon Finance berikutnya.
"""

CHARTS = [
    {"type": "bar", "section": "KINERJA", "horizontal": True,
     "judul": "BBNI: 2025 Tertekan, Q1 2026 Bangkit (% yoy)", "sumber": "Laporan Keuangan BNI",
     "kategori": ["CASA Q1 2026", "Kredit Q1 2026", "Laba Q1 2026", "Laba FY 2025"],
     "nilai": [26.6, 20.1, 5.04, -7.15]},
    {"type": "table", "section": "KENAPA PALING TERTEKAN",
     "judul": "Profil Saham BBNI", "sumber": "BEI & TradingView, per 3 Jul 2026",
     "headers": ["Indikator", "Nilai"],
     "rows": [
         ["Harga Saham", "Rp3.170"],
         ["Kinerja 1 Tahun", "-20,15%"],
         ["Dividen / Saham (2025)", "Rp349,41"],
         ["Payout Ratio", "65%"],
         ["Yield (di harga sekarang)", "11%"],
         ["Target Konsensus (19 analis)", "Rp4.788"],
         ["Rekomendasi", "19 Buy - 0 Sell"],
     ]},
    {"type": "bar", "section": "DIVIDEN DAN VALUASI",
     "judul": "NPL Gross Tiga Bank BUMN (%)", "sumber": "Laporan Keuangan 2025 & Q1 2026",
     "kategori": ["BMRI", "BBNI", "BBRI"], "nilai": [0.96, 1.9, 3.29]},
    {"type": "bar", "section": "KATA ANALIS", "horizontal": True,
     "judul": "Target Harga Analis vs Harga Sekarang (Rp)", "sumber": "TradingView & Kontan, Jul 2026",
     "kategori": ["Harga sekarang", "Terendah", "RHB (baru)", "Rata-rata konsensus", "Tertinggi"],
     "nilai": [3170, 3800, 4560, 4788, 5500]},
]

VISUAL_KEYWORDS = {"TITLE": "Bank BNI building Indonesia finance"}  # fallback saja
TOPIC = "saham BBNI Bank Negara Indonesia"


def _audio_with_retry(script, audio_path, tries=60, wait=15):
    for i in range(1, tries + 1):
        try:
            segs = generate_audio(script, audio_path)
            if segs:
                return segs
            print(f"   (percobaan {i}/{tries}: 0 segmen, ulangi)", flush=True)
        except Exception as e:
            print(f"   (percobaan {i}/{tries} gagal: {type(e).__name__})", flush=True)
        time.sleep(wait)
    raise RuntimeError("TTS gagal setelah banyak percobaan")


def step1():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"bbni_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "script.txt").write_text(SCRIPT.strip(), encoding="utf-8")
    print(f"✍️  Skrip approved: {len(SCRIPT.split())} kata")

    print("🎙️  Membuat voiceover (edge-tts)...")
    audio_path = str(run_dir / "audio.mp3")
    _audio_with_retry(SCRIPT, audio_path)

    from moviepy import AudioFileClip
    with AudioFileClip(audio_path) as a:
        dur = a.duration
    print(f"   Durasi audio: {dur:.1f} detik ({dur/60:.2f} menit)")

    STATE.write_text(json.dumps({
        "run_dir": str(run_dir), "audio_path": audio_path,
        "title": TITLE, "script": SCRIPT,
        "visual_keywords": VISUAL_KEYWORDS, "charts": CHARTS,
        "topic": TOPIC, "duration": dur,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n✅ STEP1 OK — bangun slide pack, lalu: python produce_bbni.py step2")


def step2():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    run_dir = Path(st["run_dir"])
    packs_file = run_dir / "slides.json"
    slide_packs = json.loads(packs_file.read_text(encoding="utf-8")) if packs_file.exists() else {}
    n = sum(len(v) for v in slide_packs.values())
    print(f"🎨 Slide pack: {n} slide untuk {len(slide_packs)} section")

    print(f"🎬 Compile video dari {run_dir} (audio {st['duration']/60:.2f} mnt)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        st["title"], st["script"], st["audio_path"], video_path,
        topic_keywords=st["topic"], visual_keywords=st["visual_keywords"],
        charts=st["charts"], slide_packs=slide_packs,
    )
    print(f"\n✅ SELESAI COMPILE (tanpa upload). Video: {video_path}")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "step1"
    {"step1": step1, "step2": step2}[phase]()
