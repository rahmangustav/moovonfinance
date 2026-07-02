#!/usr/bin/env python3
"""Upload video BBNI (approved, compile+upload sekali jalan) ke YouTube — PUBLIC."""
import time
from pathlib import Path

from modules.youtube_uploader import upload_video

RUN_DIR = Path("output/bbni_20260703_030329")

TITLE = "Bedah Saham BBNI: Turun 20%, Kok Analis Kompak Bilang Beli?"

DESCRIPTION = """Penutup trilogi bank BUMN: BBNI (Bank Negara Indonesia) — saham yang paling tertekan di antara bank besar (-20% setahun) tapi direkomendasikan beli oleh 19 dari 19 analis, nol yang bilang jual. Kita bedah pakai data: laba FY2025 yang sempat turun 7,15%, pemulihan kuartal I 2026 (laba Rp5,66 T, kredit +20,1%, CASA +26,6%), NPL 1,9% dibanding BMRI dan BBRI, dividen Rp349,41/saham dengan payout 65%, sampai target harga konsensus Rp4.788. Data dulu, baru opini.

⏱️ Timestamp:
00:00 Saham -20%, tapi 19 analis bilang beli — teka-teki BBNI
00:47 Kenalan: si anak tengah, 80 tahun, jaringan internasional
01:42 Rapor: FY2025 jeblok, Q1 2026 bangkit
03:06 Kenapa sahamnya paling tertekan?
04:13 Dividen Rp349,41 (payout 65%) & kualitas aset
05:22 Kata 19 analis: target rata-rata Rp4.788
06:19 Kesimpulan: mesin nyala vs tekanan belum reda
07:07 Penutup trilogi bank BUMN

⚠️ Disclaimer: Konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan (financial advice). Bukan rekomendasi membeli atau menjual saham tertentu. Selalu lakukan riset mandiri dan sesuaikan dengan profil risiko Anda. Data per awal Juli 2026 dari laporan keuangan BNI, BEI, TradingView, dan pemberitaan media keuangan.

Sumber data: Laporan Keuangan BNI, CNBC Indonesia, Bisnis Indonesia, Bareksa, TradingView, Kontan, TradingEconomics.

Tonton juga trilogi bank BUMN lainnya: Bedah Saham BBRI dan Bedah Saham BMRI di channel ini.

#BBNI #BankBNI #SahamBBNI #AnalisisSaham #MoovonFinance"""

TAGS = [
    "BBNI", "saham BBNI", "Bank BNI", "Bank Negara Indonesia", "analisis saham BBNI",
    "bedah saham", "saham perbankan", "saham dividen", "dividen BBNI", "saham turun",
    "IHSG", "BI rate", "saham BUMN", "investasi saham", "saham blue chip",
    "wondr BNI", "Moovon Finance", "belajar saham", "analisis fundamental", "target harga BBNI",
]


def _retry(fn, tries=50, wait=15):
    for i in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            print(f"   (upload percobaan {i}/{tries} gagal: {type(e).__name__}: {str(e)[:120]})", flush=True)
            time.sleep(wait)
    raise RuntimeError("upload gagal setelah banyak percobaan")


def main():
    video = RUN_DIR / "video.mp4"
    thumb = "output/bbni_slides/01_title.png"
    assert video.exists(), f"video tidak ada: {video}"
    print(f"🚀 Upload {video} ({video.stat().st_size // 1048576} MB) — PUBLIC...")
    vid = _retry(lambda: upload_video(
        video_path=str(video), title=TITLE,
        description=DESCRIPTION, tags=TAGS, thumbnail_path=thumb,
    ))
    (RUN_DIR / "youtube_id.txt").write_text(vid, encoding="utf-8")
    print(f"\n✅ LIVE: https://youtube.com/watch?v={vid}")


if __name__ == "__main__":
    main()
