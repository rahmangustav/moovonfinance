#!/usr/bin/env python3
"""Upload video SBN (final, approved) ke YouTube — PUBLIC. Metadata final per
output/sbn_20260702_201929/metadata_draft.md, judul dipilih user 2026-07-02."""
import json
import time
from pathlib import Path

from modules.youtube_uploader import upload_video

RUN_DIR = Path("output/sbn_20260702_201929")

TITLE = "Cara Kerja Obligasi SBN: Dibayar Negara Tiap Bulan"

DESCRIPTION = """Pemerintah kembali membuka penawaran SBN ritel — ORI030 dijadwalkan 6–30 Juli 2026, tepat setelah BI-Rate naik ke 5,75%. Di video ini kita bedah cara kerja obligasi negara (SBN) dari nol: apa artinya "minjemin duit ke negara", bagaimana kupon dibayar tiap bulan, beda ORI, SR, SBR, dan ST, simulasi kupon dengan angka riil (ORI029 5,45%), mekanisme floating with floor ala ST016, risiko yang perlu dipahami, pajak kupon 10% vs deposito 20%, sampai jadwal SBN ritel sisa 2026. Cocok untuk investor pemula yang mau naik kelas dari sekadar nabung.

⏱️ Timestamp:
00:00 Lapak utang negara buka lagi (ORI030 & BI-Rate 5,75%)
00:46 Apa itu obligasi & SBN — analogi ngekos
02:17 4 keluarga SBN ritel: ORI, SR, SBR, ST
04:04 Cara kerja kupon: simulasi Rp10 juta + floating with floor
06:12 Amannya di mana, risikonya di mana (+ pajak 10% vs 20%)
07:41 Cara beli & jadwal SBN ritel sisa 2026
09:00 Kesimpulan
09:42 Penutup

⚠️ Disclaimer: Konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan (financial advice). Bukan ajakan membeli/menjual produk investasi tertentu. Selalu lakukan riset mandiri dan sesuaikan dengan profil risiko Anda. Data per awal Juli 2026 — kupon ORI030 diumumkan resmi oleh DJPPR Kemenkeu menjelang masa penawaran; cek djppr.kemenkeu.go.id.

Sumber data: Bank Indonesia, DJPPR Kementerian Keuangan, Bareksa, Kompas.

#SBN #ObligasiNegara #ORI030 #SukukRitel #MoovonFinance"""

TAGS = [
    "SBN", "obligasi negara", "ORI030", "ORI", "sukuk ritel", "sukuk tabungan",
    "savings bond ritel", "SBR", "cara kerja obligasi", "investasi pemula",
    "investasi aman", "surat berharga negara", "kupon obligasi", "BI rate",
    "investasi 1 juta", "Moovon Finance", "belajar investasi", "keuangan pribadi",
    "deposito vs SBN", "pajak obligasi",
]


def _retry(fn, tries=50, wait=15, what="upload"):
    for i in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            print(f"   ({what} percobaan {i}/{tries} gagal: {type(e).__name__}: {str(e)[:120]})", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"{what} gagal setelah {tries} percobaan (jaringan?)")


def main():
    video = RUN_DIR / "video.mp4"
    thumb = RUN_DIR / "thumbnail.jpg"
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
