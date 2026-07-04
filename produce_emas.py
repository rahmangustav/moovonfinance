#!/usr/bin/env python3
"""
Produksi video: Investasi Emas 2026 (script SUDAH di-approve user 2026-07-04,
sumber: assets/draft_script_moovon.md — angka dari riset web, bukan karangan AI).

  python produce_emas.py step1   → voiceover + subtitle, simpan state, cek durasi
  python produce_emas.py step2   → render video + thumbnail (TANPA upload)

Sesuai SOP loop: TIDAK ada upload otomatis — output final di output/, metadata
berupa draft untuk direview user.
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
STATE = OUT_ROOT / "emas_state.json"
MIN_DURATION = 420  # 7 menit (soft target)

TITLE = "Investasi Emas 2026: Kenapa Harganya Terus Naik, dan Gimana Cara Ikutan?"

# ── Narasi FINAL (approved). Angka per riset 4 Juli 2026 — JANGAN diubah AI. ──
SCRIPT = """
[HOOK - 30 detik]
Emas baru aja bikin rekor lagi. Hari ini di Indonesia, harga emas Antam nembus dua koma enam tujuh juta rupiah per gram, naik empat hari berturut-turut. Di pasar dunia, harganya udah dua puluh empat persen lebih mahal dibanding setahun lalu. Banyak orang mulai panik, kelewatan gak sih kalau baru mau mulai sekarang? Video ini bakal jelasin kenapa emas naik terus, dan gimana cara ikutan investasi emas yang masuk akal, bukan ikut-ikutan panik. Seperti biasa, konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan atau financial advice.

[EMAS NAIK EMPAT HARI - 90 detik]
Mulai dari angka konkretnya dulu. Dari tanggal satu sampai empat Juli, harga emas Antam naik terus. Dari dua koma enam dua lima juta, ke dua koma enam empat juta, ke dua koma enam lima satu juta, sampai hari ini dua koma enam tujuh juta rupiah per gram. Empat hari, empat kali naik. Ini bukan cuma gejala lokal. Di pasar dunia, harga emas yang diukur dalam dolar per troy ons juga lagi rebound, sempat naik dua koma dua lima persen dalam sehari, menuju level empat ribu dua ratus dolar. Kalau kita lihat gambar lebih besar, dalam sebulan terakhir harga emas sebenarnya sempat turun tujuh persen, jadi bukan garis lurus naik terus. Tapi dalam setahun terakhir, emas tetap naik hampir dua puluh empat persen. Artinya, siapapun yang beli emas setahun lalu, sekarang untung cukup besar, walau di tengah jalan sempat ada koreksi.

[KENAPA EMAS NAIK - 90 detik]
Ada dua kekuatan utama di balik ini. Pertama, dolar Amerika lagi melemah. Awal Juli, data tenaga kerja Amerika keluar jauh lebih jelek dari perkiraan. Pasar langsung menduga The Fed, bank sentral Amerika, bakal lebih hati-hati naikin suku bunga. Kalau bunga dolar gak jadi naik setinggi perkiraan, dolar jadi kurang menarik, dan uang mengalir ke aset alternatif kayak emas. Kedua, bank-bank sentral dunia sendiri lagi rajin borong emas buat cadangan mereka. Bulan Mei aja, tercatat pembelian bersih empat puluh satu ton. Ini bukan investor ritel kayak kita, ini institusi negara yang mengumpulkan emas dalam skala besar, dan itu ikut mendorong permintaan. Kombinasi dolar lemah plus permintaan institusi ini yang bikin harga emas jadi punya angin di belakang, walau tetap ada naik turunnya harian.

[FISIK VS DIGITAL - 105 detik]
Sekarang bagian praktisnya. Kalau mau ikutan, ada dua jalan, emas fisik dan emas digital. Emas fisik itu ya batangan beneran, kayak Antam, yang lo pegang sendiri atau simpan di brankas. Kelebihannya, itu aset riil, gak ada risiko platform tutup. Tapi ya itu, lo yang tanggung jawab nyimpennya, dan kalau mau jual harus ke toko emas atau tempat buyback. Emas digital, misalnya lewat Tokopedia Emas atau Pegadaian, itu emas yang secara hukum ada wujud fisiknya, disimpan di kustodian resmi, tapi lo cuma pegang catatan digitalnya di aplikasi. Enaknya, modalnya kecil banget, bisa mulai dari lima ribu rupiah, dan jual belinya bisa kapan aja lewat HP, dana cair dalam hitungan menit. Bedanya di biaya, Pegadaian narik biaya admin tiga puluh ribu setahun, Tokopedia Emas nggak. Tapi kalau tujuan lo nyimpen dalam jumlah besar buat jangka sangat panjang dan pengen bentuk fisik, opsi cetak ke emas batangan tetap ada di Pegadaian. Jadi bukan soal mana yang lebih bagus, tapi mana yang cocok sama tujuan lo, modal kecil dan fleksibel, atau pegang fisik jangka panjang.

[ONGKOS TERSEMBUNYI - 75 detik]
Ini bagian yang sering dilewatin pemula. Emas itu punya dua harga, harga jual waktu lo beli dari toko, dan harga buyback waktu lo jual balik. Tanggal tiga Juli kemarin misalnya, harga jual Antam dua koma enam lima satu juta per gram, tapi harga buyback-nya cuma dua koma empat juta. Selisihnya dua ratus lima puluh satu ribu rupiah, atau sekitar sembilan setengah persen. Artinya apa? Begitu lo beli emas, nilai lo otomatis nyangkut sekitar sembilan persen di bawah harga beli, sampai harga emas naik cukup tinggi buat nutup selisih itu. Ini bukan berarti emas jelek, tapi ini alasan kenapa emas fisik lebih cocok buat simpanan jangka panjang, bukan buat trading harian kayak saham.

[PORSI IDEAL PORTOFOLIO - 60 detik]
Terus, kalau mau punya emas, berapa banyak idealnya? Ini bukan aturan pasti, tapi rule of thumb yang sering dipakai perencana keuangan, sekitar lima sampai sepuluh persen dari total portofolio lo. Investor yang lebih konservatif kadang naikin sampai delapan sampai dua belas persen, yang lebih agresif dan fokus pertumbuhan biasanya cukup tiga sampai lima persen aja. Logikanya, emas itu perannya sebagai peredam guncangan, bukan mesin pertumbuhan utama. Kalau seluruh portofolio lo isinya emas semua, lo justru kehilangan potensi pertumbuhan dari aset lain. Sekali lagi, angka ini rule of thumb umum, bukan resep buat semua orang, porsi yang pas tetap tergantung tujuan keuangan dan profil risiko lo masing-masing.

[KESIMPULAN - 45 detik]
Jadi, emas lagi naik karena dolar melemah dan bank sentral dunia lagi borong cadangan, bukan tanpa alasan, tapi juga bukan garis lurus, tetap ada koreksi di tengah jalan. Kalau mau ikutan, emas digital cocok buat modal kecil dan fleksibel, emas fisik cocok buat simpanan jangka panjang, dan jangan lupa, ada selisih jual beli sekitar sembilan persen yang bikin emas ini permainan jangka panjang, bukan jangka pendek. Porsi lima sampai sepuluh persen dari portofolio adalah titik awal yang wajar buat dipertimbangkan, sesuaikan sama kondisi lo sendiri.

[CTA - 20 detik]
Kalau video kayak gini ngebantu, share ke temen yang lagi mikir mulai investasi emas. Like, subscribe, nyalain lonceng notifikasi, biar makin banyak orang Indonesia melek finansial. Sampai ketemu di video berikutnya.
"""

# ── Chart dari data riset (fact sheet approved) ───────────────────────────────
CHARTS = [
    {"type": "line", "section": "EMAS NAIK EMPAT HARI",
     "judul": "Harga Emas Antam: Naik 4 Hari Berturut-turut (1-4 Juli 2026)", "sumber": "Kompas, Fortune Indonesia, 1-4 Jul 2026",
     "x": ["1 Jul", "2 Jul", "3 Jul", "4 Jul"],
     "y_dict": {"Harga Antam (Rp/gram)": [2625000, 2640000, 2651000, 2670000]}},
    {"type": "table", "section": "FISIK VS DIGITAL",
     "judul": "Emas Fisik vs Emas Digital", "sumber": "Tokopedia, Pegadaian, pluang.com, 2026",
     "headers": ["Aspek", "Emas Fisik (Antam)", "Emas Digital"],
     "rows": [["Minimum beli", "0,01-1 gram", "Rp5.000"], ["Biaya admin/tahun", "Tidak ada (fisik)", "Rp0-30.000 (tergantung platform)"], ["Kecepatan cair", "Kunjungan fisik", "Menit, via app"]]},
    {"type": "bar", "section": "ONGKOS TERSEMBUNYI",
     "judul": "Selisih Harga Jual vs Buyback Antam (3 Juli 2026)", "sumber": "Kompas, JPNN, 3 Jul 2026",
     "kategori": ["Harga Jual", "Harga Buyback"], "nilai": [2651000, 2400000]},
    {"type": "donut", "section": "PORSI IDEAL PORTOFOLIO",
     "judul": "Contoh Alokasi Portofolio dengan Emas 10%", "sumber": "Rule of thumb perencana keuangan (heygotrade.com, bareksa.com)",
     "labels": ["Emas", "Aset Lain"], "persentase": [10, 90]},
]

VISUAL_KEYWORDS = {
    "TITLE": "gold bars investment finance Indonesia",
    "HOOK": "gold bullion bars stack rupiah",
    "EMAS NAIK EMPAT HARI": "gold price rising chart bullion",
    "KENAPA EMAS NAIK": "US dollar weak central bank reserve gold",
    "FISIK VS DIGITAL": "smartphone digital gold investment app",
    "ONGKOS TERSEMBUNYI": "gold shop buyback jewelry store Indonesia",
    "PORSI IDEAL PORTOFOLIO": "financial planning portfolio diversification laptop",
    "KESIMPULAN": "young Indonesian professional investing finance laptop",
    "CTA": "subscribe youtube finance channel notification",
}

TOPIC = "investasi emas Antam digital Indonesia"

# ── Fallback visual: Canva kena limit kuota (sama seperti kasus BMRI/BBNI).
#    Pakai slide on-brand PIL (draw_content_slide dkk, tanpa foto/Canva) —
#    konten bullet di bawah SEMUA angka dari fact sheet approved, tidak ada
#    yang baru/dikarang. ──
HOOK_TEXT = "Harga emas Antam pecah rekor, naik empat hari berturut-turut. Kelewatan gak sih kalau baru mau mulai sekarang? Konten ini untuk tujuan edukasi, bukan nasihat keuangan."

CTA_TEXT = "Kalau video ini ngebantu, share ke temen yang lagi mikir mulai investasi emas. Like, subscribe, nyalain lonceng notifikasi, biar makin banyak orang Indonesia melek finansial."

SLIDE_CONTENT = {
    "EMAS NAIK EMPAT HARI": ("Emas Naik 4 Hari Berturut-turut", """
- Harga emas Antam naik terus 1-4 Juli 2026
- Harga dunia (XAU/USD) ikut rebound
- Setahun terakhir: harga emas +23,9%
- Sebulan terakhir sempat -7% (bukan garis lurus)
"""),
    "KENAPA EMAS NAIK": ("Kenapa Harga Emas Naik?", """
- Data tenaga kerja AS lebih lemah dari perkiraan
- Ekspektasi kenaikan suku bunga The Fed turun
- Dolar AS melemah, emas jadi alternatif menarik
- Bank sentral dunia borong 41 ton emas (Mei 2026)
"""),
    "FISIK VS DIGITAL": ("Emas Fisik vs Emas Digital", """
- Emas fisik: aset riil, disimpan sendiri
- Emas digital: modal kecil, cair dalam hitungan menit
- Bukan soal mana yang "terbaik", tapi mana yang cocok tujuan lo
- Detail biaya & minimum beli: lihat tabel berikutnya
"""),
    "ONGKOS TERSEMBUNYI": ("Selisih Harga Jual vs Buyback", """
- Emas punya 2 harga: harga jual & harga buyback
- Selisihnya sekitar 9,5% dari harga jual
- Bukan berarti emas jelek, ini alasan emas cocok jangka panjang
- Detail angka: lihat chart berikutnya
"""),
    "PORSI IDEAL PORTOFOLIO": ("Berapa Porsi Emas yang Wajar?", """
- Rule of thumb umum: 5-10% dari total portofolio
- Konservatif: 8-12%, Agresif: 3-5%
- Emas peredam guncangan, bukan mesin pertumbuhan utama
- Sesuaikan dengan tujuan & profil risiko masing-masing
"""),
    "KESIMPULAN": ("Rangkuman", """
- Emas naik karena dolar melemah + bank sentral borong cadangan
- Emas digital: modal kecil & fleksibel
- Emas fisik: cocok simpanan jangka panjang
- Porsi 5-10% portofolio adalah titik awal yang wajar
"""),
}


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
    run_dir = OUT_ROOT / f"emas_{ts}"
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
        print(f"⚠️  Durasi {dur/60:.2f} mnt di bawah target 7 menit (lanjut boleh, tapi dicatat).")
    print(f"\n✅ STEP1 OK — audio {dur/60:.2f} menit. Lanjut: python produce_emas.py step2")


def slides():
    """Bangun slide on-brand PIL (fallback: Canva kena limit kuota)."""
    st = json.loads(STATE.read_text(encoding="utf-8"))
    run_dir = Path(st["run_dir"])

    from modules.video_maker import (
        draw_title_slide, draw_hook_slide, draw_cta_slide, draw_content_slide,
    )

    slide_packs = {}

    p = run_dir / "slide_pack_title.png"
    draw_title_slide(st["title"], bg_image_path=None).save(p)
    slide_packs["TITLE"] = [str(p)]

    p = run_dir / "slide_pack_hook.png"
    draw_hook_slide(HOOK_TEXT, bg_image_path=None).save(p)
    slide_packs["HOOK"] = [str(p)]

    total = len(SLIDE_CONTENT)
    for i, (label, (heading, body)) in enumerate(SLIDE_CONTENT.items(), start=1):
        p = run_dir / f"slide_pack_{i:02d}.png"
        draw_content_slide(heading, body.strip(), i, total, side_image_path=None).save(p)
        slide_packs[label] = [str(p)]

    p = run_dir / "slide_pack_cta.png"
    draw_cta_slide(CTA_TEXT, bg_image_path=None).save(p)
    slide_packs["CTA"] = [str(p)]

    st["slide_packs"] = slide_packs
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"🎨 {len(slide_packs)} slide on-brand PIL dibuat (tanpa foto/Canva).")
    print("   Lanjut: python produce_emas.py step2")


def step2():
    st = json.loads(STATE.read_text(encoding="utf-8"))
    run_dir = Path(st["run_dir"])
    print(f"🎬 Render video dari {run_dir} (audio {st['duration']/60:.2f} mnt)...")
    video_path = str(run_dir / "video.mp4")
    create_video(
        st["title"], st["script"], st["audio_path"], video_path,
        topic_keywords=st["topic"], visual_keywords=st["visual_keywords"],
        charts=st["charts"], slide_packs=st.get("slide_packs"),
    )
    print("🖼️  Membuat thumbnail...")
    thumb = str(run_dir / "thumbnail.jpg")
    create_thumbnail(st["title"], thumb)
    print(f"\n✅ SELESAI RENDER (tanpa upload). Video: {video_path}")
    print("   Review dulu, upload terpisah setelah metadata disetujui.")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "step1"
    {"step1": step1, "slides": slides, "step2": step2}[phase]()
