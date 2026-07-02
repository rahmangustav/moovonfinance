#!/usr/bin/env python3
"""
Produksi video: Cara Kerja Obligasi SBN (script SUDAH di-approve user 2026-07-02,
sumber: assets/draft_script_moovon.md — angka dari riset web, bukan karangan AI).

  python produce_sbn.py step1   → voiceover + subtitle, simpan state, cek durasi
  python produce_sbn.py step2   → render video + thumbnail (TANPA upload)

Sesuai SOP loop: TIDAK ada upload otomatis — output final di output/, metadata
berupa draft untuk direview user.
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from modules.script_writer import parse_script  # noqa: F401 (konsistensi import pipeline)
from modules.tts import generate_audio
from modules.video_maker import create_video
from modules.thumbnail import create_thumbnail

OUT_ROOT = Path("output")
STATE = OUT_ROOT / "sbn_state.json"
MIN_DURATION = 480  # 8 menit (soft target)

TITLE = "Cara Kerja Obligasi SBN: Dibayar Negara Tiap Bulan"

# ── Narasi FINAL (approved). Angka per riset 2 Juli 2026 — JANGAN diubah AI. ──
SCRIPT = """
[HOOK - 35 detik]
Tanggal 6 Juli ini, pemerintah buka lagi lapak utang buat kita semua. Namanya ORI030. Dan timing-nya menarik, karena Bank Indonesia baru aja naikin suku bunga tiga kali dalam sebulan, sekarang nangkring di 5,75 persen. Pertanyaannya, kalau lo minjemin duit ke negara, lo dapet apa? Amankah? Dan kenapa banyak orang bilang ini naik kelasnya orang yang biasa nabung di deposito? Di video ini kita bedah cara kerja obligasi negara alias SBN, dari nol, pakai angka asli tahun ini. Tapi satu hal dulu. Konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan atau financial advice. Semua keputusan investasi tetap di tangan lo.

[APA ITU OBLIGASI - 90 detik]
Gampangnya gini. Kalau saham itu lo beli kepemilikan perusahaan, obligasi itu lo minjemin duit. Lo jadi pihak yang punya piutang. Nah, SBN, Surat Berharga Negara, artinya yang ngutang ke lo itu negara. Republik Indonesia. Duit yang lo pinjemin dipakai pemerintah buat bangun jalan, sekolah, subsidi, dan ngisi APBN. Sebagai gantinya, negara bayar uang sewa ke lo secara rutin. Uang sewa ini namanya kupon. Analoginya kayak lo ngekosin kamar. Duit lo ngekos di negara, tiap bulan lo terima uang sewanya, dan pas kontraknya habis, istilahnya jatuh tempo, duit pokok lo balik utuh, seratus persen. Ada tiga kata kunci yang bakal sering muncul di video ini. Pertama, pokok, yaitu duit yang lo pinjemin. Kedua, kupon, yaitu bunga atau imbal hasil yang dibayar rutin ke rekening lo. Ketiga, tenor, yaitu lamanya kontrak, misalnya dua tahun, tiga tahun, atau enam tahun. Simpel kan? Lo minjemin duit, lo digaji tiap bulan sama negara, dan di akhir kontrak duit lo balik. Sekarang pertanyaannya, SBN yang bisa dibeli orang biasa kayak kita itu yang mana aja?

[JENIS SBN RITEL - 2 menit]
SBN ritel, yang bisa dibeli masyarakat umum mulai dari satu juta rupiah, itu ada empat keluarga. Bedanya cuma di dua hal. Konvensional atau syariah, dan bisa dijual lagi atau nggak. Keluarga pertama, ORI, Obligasi Negara Ritel. Ini konvensional, kuponnya tetap alias fixed, dan bisa diperjualbelikan lagi di pasar sekunder setelah periode tertentu. Keluarga kedua, SR, Sukuk Ritel. Ini kembarannya ORI tapi versi syariah. Imbal hasilnya tetap, dan bisa diperjualbelikan juga. Keluarga ketiga, SBR, Savings Bond Ritel. Ini konvensional, tapi kuponnya mengambang alias floating, dan gak bisa dijual lagi. Mirip deposito, dikunci sampai jatuh tempo. Dan keluarga keempat, ST, Sukuk Tabungan, kembarannya SBR versi syariah. Tahun 2026 ini semua keluarga kebagian jatah terbit. Yang udah lewat, ORI029, kuponnya 5,45 persen untuk tenor tiga tahun, dan 5,8 persen untuk tenor enam tahun. Terus SR024, imbal hasilnya 5,55 persen dan 5,9 persen. Dan ST016, imbalannya mulai dari 6,05 persen. Angka-angka ini penting, karena jadi patokan kasar buat nebak kupon seri berikutnya, termasuk ORI030 yang sebentar lagi buka.

[CARA KERJA KUPON - 2 menit 30 detik]
Oke, sekarang bagian yang paling sering ditanya. Duitnya gimana? Kita pakai angka beneran. Misal lo beli ORI029 tenor tiga tahun senilai sepuluh juta rupiah, dengan kupon 5,45 persen per tahun. Setahun, lo dapet sepuluh juta dikali 5,45 persen, sama dengan lima ratus empat puluh lima ribu rupiah. Dibagi dua belas bulan, jadi sekitar empat puluh lima ribu empat ratus rupiah per bulan. Nah, kupon ini kena pajak final sepuluh persen, jadi bersihnya sekitar empat puluh ribu sembilan ratus rupiah, masuk rekening lo tiap tanggal lima belas. Kecil? Inget, ini per sepuluh juta. Dan poin pentingnya, angka ini pasti. Gak peduli pasar lagi drama apa, kupon fixed gak berubah. Tiga tahun kemudian, pokok sepuluh juta lo balik utuh. Nah, yang tipe floating with floor, kayak ST016, beda cara mainnya. Kuponnya ngikutin BI Rate, disesuaikan tiap tiga bulan, tapi ada lantainya, batas bawah yang gak bisa ditembus. ST016 tenor dua tahun, floor-nya 6,05 persen. Itu asalnya dari BI Rate waktu itu, ditambah spread 1,3 persen. Sekarang BI Rate udah naik ke 5,75 persen. Artinya apa? Kalau BI Rate bertahan di level ini sampai penyesuaian berikutnya di sebelas Agustus, imbalan ST016 bisa ikut naik jadi sekitar 7,05 persen. Tapi inget, ini ilustrasi mekanisme ya, bukan janji. Angka resminya tetap nunggu penetapan pemerintah. Jadi logikanya gini. Suku bunga lagi tren naik, tipe floating yang diuntungin. Suku bunga tren turun, tipe fixed yang menang, dan yang floating tetep dilindungi sama floor-nya.

[RISIKO DAN KEAMANAN - 2 menit]
Kenapa SBN sering disebut instrumen paling aman di Indonesia? Karena pembayaran pokok dan kuponnya dijamin undang-undang, dibayar dari APBN. Negara gagal bayar utang ke warganya sendiri itu skenario yang jauh lebih ekstrem daripada satu bank kesulitan. Deposito aja penjaminannya lewat LPS, dan ada batasnya. Tapi, aman bukan berarti tanpa risiko. Ada dua yang wajib lo tau. Pertama, risiko likuiditas. SBR dan ST gak bisa dijual sebelum jatuh tempo. Ada sih fasilitas early redemption buat nyairin sebagian dana di jendela waktu tertentu, tapi terbatas dan ada syaratnya. Jadi, jangan taruh dana darurat lo di sini. Kedua, risiko harga pasar. ORI dan SR memang bisa dijual sebelum jatuh tempo, tapi harganya ngikutin pasar. Kalau suku bunga naik, harga obligasi lama cenderung turun. Lo bisa rugi kalau maksa jual di saat yang salah. Tapi kalau dipegang sampai jatuh tempo, pokok lo balik seratus persen. Dan satu lagi yang sering kelewat. Pajak. Kupon SBN kena pajak final cuma sepuluh persen. Bandingin sama bunga deposito yang kena dua puluh persen. Selisih sepuluh persen itu, buat dana ratusan juta, bukan angka kecil.

[CARA BELI DAN JADWAL - 90 detik]
Terus belinya gimana? Gampang, dan full online. Lewat mitra distribusi resmi, bisa bank, sekuritas, atau aplikasi fintech yang terdaftar. Lo tinggal daftar SID, Single Investor Identification, pesan pas masa penawaran buka, bayar, selesai. Minimal pembeliannya satu juta rupiah, dan kelipatannya juga satu juta. Sekarang catat kalender sisa tahun 2026. Jadwal ini tentatif dari Kementerian Keuangan ya, bisa berubah. Yang paling dekat, ORI030, dibuka enam sampai tiga puluh Juli. Kuponnya diumumkan menjelang pembukaan, jadi cek langsung di situs resmi DJPPR Kemenkeu atau di mitra distribusi. Setelah itu ada SR025 di dua puluh satu Agustus sampai sebelas September, SBR015 di dua puluh delapan September sampai dua puluh dua Oktober, dan penutup tahun, ST017, di enam November sampai dua Desember. Jadi kalau lo kelewatan satu seri, tenang, masih ada kesempatan berikutnya.

[KESIMPULAN - 60 detik]
Jadi, obligasi SBN itu intinya gini. Lo minjemin duit ke negara, dibayar kupon rutin tiap bulan, pokok balik utuh pas jatuh tempo, dijamin undang-undang, dan pajaknya lebih ringan daripada deposito. Ini bukan instrumen buat kaya cepat. Ini instrumen buat duit lo kerja pelan, tapi pasti. Cocok buat yang mau naik kelas dari sekadar nabung, tanpa harus begadang mantengin chart. Dan sekali lagi, ini konten edukasi, bukan ajakan beli produk tertentu. Selalu riset sendiri sebelum investasi, sesuaikan sama profil risiko lo.

[CTA - 30 detik]
Kalau video ini bikin lo lebih ngerti soal SBN, bantu channel ini dengan like dan subscribe, biar makin banyak orang Indonesia yang melek finansial. Tulis juga di komentar, lo tim kupon fixed atau tim floating? Sampai ketemu di video Moovon Finance berikutnya.
"""

# ── Chart dari data riset (fact sheet approved) ───────────────────────────────
CHARTS = [
    {"type": "line", "section": "HOOK",
     "judul": "BI-Rate 2026: Naik 3 Kali dalam Sebulan (%)", "sumber": "Bank Indonesia, per 18 Jun 2026",
     "x": ["Jan-Apr", "20 Mei", "9 Jun", "18 Jun"],
     "y_dict": {"BI-Rate": [4.75, 5.25, 5.50, 5.75]}},
    {"type": "table", "section": "JENIS SBN RITEL",
     "judul": "4 Keluarga SBN Ritel", "sumber": "DJPPR Kemenkeu",
     "headers": ["Seri", "Prinsip", "Kupon", "Bisa Dijual Lagi?"],
     "rows": [
         ["ORI", "Konvensional", "Tetap", "Ya"],
         ["SR", "Syariah", "Tetap", "Ya"],
         ["SBR", "Konvensional", "Floating + floor", "Tidak"],
         ["ST", "Syariah", "Floating + floor", "Tidak"],
     ]},
    {"type": "bar", "section": "JENIS SBN RITEL",
     "judul": "Kupon SBN Ritel 2026 (% per tahun)", "sumber": "DJPPR Kemenkeu, per Jul 2026",
     "kategori": ["ORI029\n3 th", "ORI029\n6 th", "SR024\n3 th", "SR024\n5 th", "ST016\n2 th*", "ST016\n4 th*"],
     "nilai": [5.45, 5.80, 5.55, 5.90, 6.05, 6.25]},
    {"type": "bar", "section": "RISIKO DAN KEAMANAN",
     "judul": "Pajak Final Imbal Hasil: SBN vs Deposito (%)", "sumber": "PP 91/2021",
     "kategori": ["Kupon SBN", "Bunga Deposito"], "nilai": [10, 20], "horizontal": True},
    {"type": "timeline", "section": "CARA BELI DAN JADWAL",
     "judul": "Jadwal SBN Ritel Sisa 2026 (tentatif)", "sumber": "DJPPR Kemenkeu",
     "events": ["ORI030", "SR025", "SBR015", "ST017"],
     "dates": ["6-30 Jul", "21 Agu-11 Sep", "28 Sep-22 Okt", "6 Nov-2 Des"]},
]

VISUAL_KEYWORDS = {
    "TITLE": "Indonesia government bonds rupiah investment finance",
    "HOOK": "Indonesia ministry of finance building Jakarta",
    "APA ITU OBLIGASI": "government bond certificate document handshake agreement",
    "JENIS SBN RITEL": "Indonesian rupiah money savings investment choice",
    "CARA KERJA KUPON": "calculator financial planning money coins Indonesia",
    "RISIKO DAN KEAMANAN": "financial security shield protection umbrella savings",
    "CARA BELI DAN JADWAL": "mobile banking app smartphone investment Indonesia",
    "KESIMPULAN": "young Indonesian professional planning finance laptop",
    "CTA": "subscribe youtube finance channel notification",
}

TOPIC = "obligasi SBN Surat Berharga Negara Indonesia"


def _audio_with_retry(script, audio_path, tries=60, wait=15):
    """edge-tts sering timeout/DNS gagal (jaringan intermiten). Retry panjang."""
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
    run_dir = OUT_ROOT / f"sbn_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "script.txt").write_text(SCRIPT.strip(), encoding="utf-8")

    word_count = len(SCRIPT.split())
    print(f"✍️  Skrip approved: {word_count} kata")

    print("🎙️  Membuat voiceover (edge-tts, word-boundary subtitle)...")
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
        "topic": TOPIC, "duration": dur, "words": word_count,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    if dur < MIN_DURATION:
        print(f"⚠️  Durasi {dur/60:.2f} mnt di bawah target 8 menit (lanjut boleh, tapi dicatat).")
    print(f"\n✅ STEP1 OK — audio {dur/60:.2f} menit. Lanjut: python produce_sbn.py step2")


def step2():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    run_dir = Path(st["run_dir"])
    print(f"🎬 Render video dari {run_dir} (audio {st['duration']/60:.2f} mnt)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        st["title"], st["script"], st["audio_path"], video_path,
        topic_keywords=st["topic"], visual_keywords=st["visual_keywords"],
        charts=st["charts"],
    )
    print("🖼️  Membuat thumbnail...")
    thumb = str(run_dir / "thumbnail.jpg")
    create_thumbnail(st["title"], thumb)
    print(f"\n✅ SELESAI RENDER (tanpa upload). Video: {video_path}")
    print("   Review dulu, upload terpisah setelah metadata disetujui.")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "step1"
    {"step1": step1, "step2": step2}[phase]()
