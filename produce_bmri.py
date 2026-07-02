#!/usr/bin/env python3
"""
Produksi video: Bedah Saham BMRI (script approved user 2026-07-03, sumber:
assets/draft_script_moovon.md — angka dari riset web 3 Jul 2026).

  python produce_bmri.py step1   → voiceover + subtitle, simpan state
  python produce_bmri.py step2   → compile: slide Canva (canva_slides.json) +
                                   chart lokal + subtitle. TANPA upload.

Workflow visual baru: slide utama dari Canva (memory/sop_loop.md Fase 2).
step2 membaca <run_dir>/canva_slides.json = {"LABEL SECTION": ["path.png", ...]}.
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from modules.tts import generate_audio
from modules.video_maker import create_video
from modules.thumbnail import create_thumbnail

OUT_ROOT = Path("output")
STATE = OUT_ROOT / "bmri_state.json"

TITLE = "Bedah Saham BMRI: Laba Naik, Kok Harganya Turun?"

SCRIPT = """
[HOOK - 35 detik]
Ada yang aneh di saham Bank Mandiri. Kuartal pertama tahun ini, labanya naik 16,6 persen. Salah satu yang paling kencang di antara bank besar. Tapi harga sahamnya? Turun hampir 18 persen dalam setahun, dan minggu lalu ikut rontok bareng IHSG. Laba naik, harga turun. Buat sebagian orang, ini alarm. Buat sebagian lagi, ini diskon. Di video ini kita bedah datanya, bukan feeling-nya. Dan sebelum mulai, inget, konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan atau financial advice. Bukan ajakan beli atau jual. Keputusan tetap di tangan lo.

[PROFIL BANK MANDIRI - 90 detik]
Kenalan dulu. Bank Mandiri itu bank dengan aset terbesar di Indonesia. Akhir 2025, asetnya tembus 2.830 triliun rupiah, naik 16,6 persen dalam setahun. Kalau BRI yang pernah kita bedah itu rajanya kredit mikro dan UMKM, Mandiri main di lapangan yang beda. Kredit korporasi dan wholesale. Perusahaan-perusahaan gede, BUMN, pembiayaan proyek. Ditambah satu mesin yang lagi ngebut, aplikasi Livin' by Mandiri yang bikin pendapatan non-bunganya melonjak. Kenapa karakter ini penting? Karena kredit korporasi itu marginnya lebih tipis daripada kredit mikro, tapi risikonya jauh lebih terkendali. Dan itu kelihatan banget nanti di satu angka yang bakal kita bahas. Rasio kredit macet Mandiri termasuk yang paling rendah di industri perbankan Indonesia.

[KINERJA - 2 menit]
Sekarang kita lihat rapornya. Tahun 2025 penuh, laba bersih Mandiri 56,3 triliun rupiah. Naiknya memang tipis, cuma nol koma sembilan persen dari tahun sebelumnya. Tapi inget konteksnya, 2025 itu tahun yang berat buat perbankan. Suku bunga tinggi, ekonomi melambat. Yang menarik justru mesin di baliknya. Kredit tumbuh 13,4 persen jadi 1.895 triliun rupiah. Dana pihak ketiga naik 23,9 persen. Dan pendapatan non-bunga, fee dari Livin', transaksi, treasury, melonjak 14,5 persen jadi 48,5 triliun rupiah. Terus masuk 2026, kuartal pertama, laba 15,4 triliun rupiah, naik 16,6 persen dibanding periode yang sama tahun lalu. Return on equity 22 persen. Artinya, tiap 100 rupiah modal yang ditanam, setahun bisa menghasilkan laba 22 rupiah. Buat bank sebesar ini, itu angka yang sehat banget. Jadi kalau kita lihat dapurnya doang, gak ada tanda-tanda mesin rusak. Justru lagi kenceng-kencengnya.

[KENAPA SAHAM TURUN - 2 menit]
Nah, ini bagian pentingnya. Harga saham BMRI sekarang di sekitar 3.900 rupiah. Setahun terakhir turun hampir 18 persen. Akhir Juni kemarin bahkan ikut kena panic selling, waktu IHSG anjlok tiga persen sehari dan saham bank besar rontok berjamaah. Penyebabnya bukan dari dalam dapur Mandiri, tapi dari luar. Setidaknya ada empat. Pertama, Bank Indonesia naikin suku bunga tiga kali dalam sebulan, sampai ke 5,75 persen. Dan saham bank memang paling sensitif sama ini, karena biaya dana ikut naik. Kedua, investor asing lagi keluar. Net sell terus-terusan, terutama di saham BUMN. Ketiga, sentimen politik. Isu reshuffle kabinet bikin pasar gugup sama saham pelat merah. Dan keempat, dari luar negeri. Tarif impor Amerika 32 persen untuk produk Indonesia yang mulai berlaku 1 Agustus, bikin pasar waswas soal arah ekonomi. Poinnya gini. Laba naik tapi harga turun, itu artinya pasar lagi menghukum sektornya dan negaranya, bukan perusahaannya. Tapi hati-hati. Ini bukan berarti besok langsung balik. Sentimen kayak gini bisa berlangsung lama, dan harga bisa turun lebih dalam dulu sebelum pulih.

[KUALITAS ASET DAN DIVIDEN - 2 menit]
Di tengah tekanan kayak gini, ada dua angka yang bikin BMRI beda. Yang pertama, kualitas aset. Rasio kredit macet alias NPL gross-nya cuma 0,96 persen di akhir 2025. Dan di kuartal satu 2026 masih terjaga di 0,98 persen. Bandingin sama BRI yang NPL-nya 3,29 persen, karena main di segmen mikro yang lebih rawan macet. Bukan berarti BRI jelek ya, beda medan aja. Tapi buat ukuran keamanan, angka Mandiri ini kelas satu. Apalagi mereka udah nyiapin dana jaga-jaga alias pencadangan, dua setengah kali lipat dari total kredit macetnya. Konservatif banget. Yang kedua, dividen. Untuk tahun buku 2025, Mandiri bagi 476,96 rupiah per saham. Di harga sekarang, itu setara imbal hasil sekitar 12 persen. Angka segede ini muncul justru karena harganya lagi turun. Dan catatan penting, yield segede ini gak otomatis keulang tiap tahun. Kalau harga naik atau laba berubah, yield-nya ikut bergeser. Proyeksi analis untuk tahun-tahun ke depan lebih konservatif, di kisaran 7 sampai 8 persen. Itu pun masih termasuk yang paling tinggi di bursa.

[KATA ANALIS - 60 detik]
Terus, pasar profesional lihatnya gimana? Konsensus 17 analis yang dirangkum TradingView kasih target harga rata-rata 5.300 rupiah. Sekitar 36 persen di atas harga sekarang. Yang paling pesimis di 3.600. Yang paling optimis, UBS, sampai 7.950. MNC, Danareksa, Macquarie, dan CGS semuanya di kisaran enam ribuan. Dan mayoritas rekomendasinya, beli. Tapi inget dua hal. Target harga itu opini, bukan janji. Analis juga sering salah. Dan sebagian besar konsensus ini dibuat sebelum dampak tarif Amerika beneran kerasa di lapangan. Jadi pakai angka ini sebagai salah satu bahan pertimbangan, bukan satu-satunya.

[KESIMPULAN - 45 detik]
Jadi, BMRI hari ini kayak gini. Bisnisnya lagi sehat. Laba kuartalan naik dua digit, kredit macet terendah di kelasnya, dividen jumbo. Sahamnya lagi murah bukan karena perusahaannya bermasalah, tapi karena pasarnya lagi takut. Suku bunga, asing keluar, politik, tarif. Buat trader jangka pendek, ini zona yang gak nyaman. Buat investor yang horizonnya panjang dan ngerti risikonya, sejarah bilang momen kayak gini justru yang sering dicari-cari. Lo yang mana? Itu keputusan lo, sesuaikan sama profil risiko lo. Dan sekali lagi, ini edukasi, bukan rekomendasi beli atau jual.

[CTA - 30 detik]
Kalau lo mau saham lain dibedah kayak gini, data dulu baru opini, tulis di komentar. Jangan lupa like, subscribe, dan nyalain lonceng notifikasi, biar makin banyak orang Indonesia yang melek finansial. Sampai ketemu di video Moovon Finance berikutnya.
"""

CHARTS = [
    {"type": "bar", "section": "KINERJA", "horizontal": True,
     "judul": "Mesin BMRI Tetap Tumbuh (% yoy)", "sumber": "Laporan Keuangan BMRI",
     "kategori": ["DPK 2025", "Laba Q1 2026", "Non-bunga 2025", "Kredit 2025", "Laba FY 2025"],
     "nilai": [23.9, 16.6, 14.5, 13.4, 0.9]},
    {"type": "table", "section": "KENAPA SAHAM TURUN",
     "judul": "Profil Saham BMRI", "sumber": "BEI & TradingView, per 2 Jul 2026",
     "headers": ["Indikator", "Nilai"],
     "rows": [
         ["Harga Saham", "Rp3.900"],
         ["Kapitalisasi Pasar", "Rp367,4 T"],
         ["Kinerja 1 Tahun", "-17,7%"],
         ["Dividen / Saham (2025)", "Rp476,96"],
         ["Yield (TTM)", "12%"],
         ["Target Konsensus (17 analis)", "Rp5.301"],
         ["Potensi Upside", "+36%"],
     ]},
    {"type": "bar", "section": "KUALITAS ASET DAN DIVIDEN",
     "judul": "NPL Gross 2025: Mandiri vs BRI (%)", "sumber": "Laporan Keuangan BMRI & BBRI 2025",
     "kategori": ["BMRI", "BBRI"], "nilai": [0.96, 3.29]},
    {"type": "bar", "section": "KATA ANALIS", "horizontal": True,
     "judul": "Target Harga Analis vs Harga Sekarang (Rp)", "sumber": "Investortrust & TradingView, Jul 2026",
     "kategori": ["Harga sekarang", "Samuel", "MNC", "BRI Danareksa", "Macquarie", "CGS", "UBS"],
     "nilai": [3900, 5700, 6050, 6200, 6240, 6700, 7950]},
]

# Fallback foto web hanya kalau slide Canva tak tersedia untuk suatu section
VISUAL_KEYWORDS = {
    "TITLE": "Bank Mandiri building logo Indonesia finance",
    "HOOK": "stock market chart down red Indonesia trading screen",
    "PROFIL BANK MANDIRI": "Bank Mandiri headquarters tower Jakarta",
    "KINERJA": "financial report growth chart Indonesia banking",
    "KENAPA SAHAM TURUN": "stock exchange Indonesia market pressure trading",
    "KUALITAS ASET DAN DIVIDEN": "safe vault bank security money Indonesia",
    "KATA ANALIS": "financial analyst research office charts",
    "KESIMPULAN": "investor thinking decision finance Indonesia",
    "CTA": "subscribe youtube finance channel notification",
}

TOPIC = "saham BMRI Bank Mandiri"


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
    raise RuntimeError("TTS gagal setelah banyak percobaan (jaringan mati terus)")


def step1():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"bmri_{ts}"
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
    print(f"\n✅ STEP1 OK — lanjut desain slide Canva, lalu: python produce_bmri.py step2")


def step2():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    run_dir = Path(st["run_dir"])

    packs_file = run_dir / "canva_slides.json"
    slide_packs = {}
    if packs_file.exists():
        slide_packs = json.loads(packs_file.read_text(encoding="utf-8"))
        n = sum(len(v) for v in slide_packs.values())
        print(f"🎨 Slide pack Canva: {n} slide untuk {len(slide_packs)} section")
    else:
        print("⚠️  canva_slides.json tidak ada — fallback penuh ke foto web")

    print(f"🎬 Compile video dari {run_dir} (audio {st['duration']/60:.2f} mnt)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        st["title"], st["script"], st["audio_path"], video_path,
        topic_keywords=st["topic"], visual_keywords=st["visual_keywords"],
        charts=st["charts"], slide_packs=slide_packs,
    )
    print(f"\n✅ SELESAI COMPILE (tanpa upload). Video: {video_path}")
    print("   Review dulu; thumbnail via Canva; upload setelah approval.")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "step1"
    {"step1": step1, "step2": step2}[phase]()
