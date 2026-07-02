#!/usr/bin/env python3
"""Upload video BMRI (approved) ke YouTube — PUBLIC. Metadata per
output/bmri_20260703_003419/metadata_draft.md, judul opsi 1."""
import time
from pathlib import Path

from modules.youtube_uploader import upload_video

RUN_DIR = Path("output/bmri_20260703_003419")

TITLE = "Bedah Saham BMRI: Laba Naik, Kok Harganya Turun?"

DESCRIPTION = """Ada anomali di saham Bank Mandiri (BMRI): laba kuartal I 2026 naik 16,6% jadi Rp15,4 triliun — tapi harga sahamnya turun hampir 18% dalam setahun dan ikut rontok saat IHSG anjlok 3% akhir Juni. Di video ini kita bedah pakai data: kinerja FY2025 & Q1 2026, empat faktor eksternal yang menekan harga (BI-Rate 5,75%, net sell asing, sentimen politik, tarif impor AS 32%), kualitas aset dengan NPL 0,96% (dibandingkan BBRI 3,29%), dividen Rp476,96/saham, sampai target harga konsensus 17 analis di Rp5.301. Data dulu, baru opini.

⏱️ Timestamp:
00:00 Laba naik 16,6%, saham turun 18% — anomali BMRI
00:48 Kenalan: bank aset terbesar di Indonesia (Rp2.830 T)
01:51 Rapor FY2025 & kuartal I 2026
03:13 Empat faktor kenapa sahamnya turun
04:47 Dua jangkar: NPL 0,96% & dividen Rp476,96/saham
06:18 Kata 17 analis: target harga Rp5.301
07:17 Kesimpulan: fundamental vs sentimen
08:12 Penutup

⚠️ Disclaimer: Konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan (financial advice). Bukan rekomendasi membeli atau menjual saham tertentu. Selalu lakukan riset mandiri dan sesuaikan dengan profil risiko Anda. Data per awal Juli 2026 dari laporan keuangan BMRI, BEI, TradingView, dan pemberitaan media keuangan.

Sumber data: Laporan Keuangan Bank Mandiri, IDN Financials, Bisnis Indonesia, Databoks Katadata, TradingView, Bareksa, Investortrust.

#BMRI #BankMandiri #SahamBMRI #AnalisisSaham #MoovonFinance"""

TAGS = [
    "BMRI", "saham BMRI", "Bank Mandiri", "analisis saham BMRI", "bedah saham",
    "saham perbankan", "saham dividen", "dividen BMRI", "NPL bank", "saham turun",
    "IHSG", "BI rate", "net sell asing", "saham BUMN", "investasi saham",
    "saham blue chip", "Moovon Finance", "belajar saham", "analisis fundamental",
    "target harga BMRI",
]


def _retry(fn, tries=50, wait=15):
    for i in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            print(f"   (upload percobaan {i}/{tries} gagal: {type(e).__name__}: {str(e)[:120]})", flush=True)
            time.sleep(wait)
    raise RuntimeError("upload gagal setelah banyak percobaan (jaringan?)")


def main():
    video = RUN_DIR / "video.mp4"
    thumb = RUN_DIR / "thumbnail_canva.png"
    assert video.exists(), f"video tidak ada: {video}"
    print(f"🚀 Upload {video} ({video.stat().st_size // 1048576} MB) — PUBLIC...")
    vid = _retry(lambda: upload_video(
        video_path=str(video), title=TITLE,
        description=DESCRIPTION, tags=TAGS, thumbnail_path=str(thumb),
    ))
    (RUN_DIR / "youtube_id.txt").write_text(vid, encoding="utf-8")
    print(f"\n✅ LIVE: https://youtube.com/watch?v={vid}")


if __name__ == "__main__":
    main()
