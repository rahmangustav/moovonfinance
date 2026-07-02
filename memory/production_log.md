# Production Log — Moovon Finance

> **Channel VERIFIED per 2026-07-03** — custom thumbnail via API sudah jalan (`thumbnails.set`, scope youtube.upload cukup). Thumbnail SBN & BMRI v2 terpasang retroaktif; upload berikutnya otomatis.

Format: tanggal | topik/judul | status | link/ID | catatan

## Video yang sudah dipublikasikan
- 2026-07-01 | Bedah Saham BBRI 2025: Laba Turun (analisis kinerja BBRI) | PUBLIC | `LLg7NYh0lXE` (versi subtitle fix, 11:57) | Versi lama `c8aZ9_VW9ps` subtitle salah, masih public — perlu di-unlist manual di YouTube Studio (scope OAuth kurang).
- 2026-07-02 | Cara Kerja Obligasi SBN: Dibayar Negara Tiap Bulan | PUBLIC | `VVn3WHReEP8` (10:03) | Edukasi obligasi/SBN: ORI-SR-SBR-ST, simulasi kupon ORI029, floating with floor, pajak 10% vs 20%, jadwal 2026. 5 chart data riil. Custom thumbnail ke-skip (channel belum verified). FOLLOW-UP 3 Jul: kupon ORI030 resmi diumumkan → tambah ke deskripsi (manual YouTube Studio) / pin comment. Thumbnail Canva FINAL: `output/sbn_20260702_201929/thumbnail_canva.png` (Canva design `DAHOQKIpIsw`) — pasang manual di YouTube Studio setelah channel verified.

- 2026-07-03 | Bedah Saham BMRI: Laba Naik, Kok Harganya Turun? | **PUBLIC (v2 subtitle-fix)** | `ymRoSeUyPO8` (8:28) | Menggantikan `FId3xkUS0CY` (unlisted manual oleh user; subtitle burned terlalu besar). Fix permanen di `_burn_subtitles`: skala libass PlayResY=288 — font 13 (≈49px @1080p), MarginV=12 (bawah). |
- 2026-07-03 | (versi lama) idem | UNLISTED | `FId3xkUS0CY` | Video PERTAMA workflow visual Canva (hybrid: 4 slide Canva + 5 slide PIL on-brand + 4 chart matplotlib, zero foto web). Thumbnail custom ke-skip lagi (channel belum verified) — file siap di `output/bmri_20260703_003419/thumbnail_canva.png`. Catatan workflow: Canva AI kacau di slide teks kompleks (1x fabrikasi angka!), quota AI generation habis di tengah proses → slide kompleks dibikin lokal.

- 2026-07-03 | Bedah Saham BBNI: Turun 20%, Kok Analis Kompak Bilang Beli? | PUBLIC | `WNrqGryFf9M` (7:39) | Penutup trilogi bank BUMN. Video pertama dengan THUMBNAIL OTOMATIS (channel verified) + subtitle ukuran baru sejak awal. Visual: 9 slide PIL on-brand (opsi A, quota Canva habis) + 4 chart. CTA menjanjikan: video perbandingan 3 bank / bedah BCA kalau diminta komentar.

## Topik yang sudah dibahas (hindari pengulangan persis)
- Analisis kinerja/laporan keuangan saham BBRI (Bank Rakyat Indonesia)
- Cara kerja obligasi SBN / SBN ritel dasar (ORI, SR, SBR, ST, kupon, tenor, jatuh tempo)
- Analisis saham BMRI (Bank Mandiri): kinerja 2025/Q1-2026, NPL, dividen, tekanan makro
- Analisis saham BBNI (BNI): FY2025 turun vs Q1-2026 bangkit, dividen payout 65%, konsensus analis

## Antrian / draft
- 2026-07-03 | Bedah saham BBNI | DRAFT — menunggu review user | `assets/draft_script_moovon.md` | Penutup trilogi bank BUMN. Angle: saham paling tertekan (-20% setahun) vs 19 analis kompak buy. Quota Canva habis hari ini → visual opsi PIL on-brand atau tunggu besok.
- 2026-07-03 | Bedah saham BMRI (Bank Mandiri) | DRAFT — menunggu review user | `assets/draft_script_moovon.md` | Video pertama workflow visual Canva. Angle: laba naik 16,6% vs saham -17,7% setahun (tekanan makro, bukan fundamental).
- 2026-07-03 | Kupon ORI030 | PENDING — angka resmi belum diumumkan saat dicek | - | Guardrail stop; lanjut begitu DJPPR rilis angka resmi.
- 2026-07-02 | Cara kerja obligasi SBN | **RENDER SELESAI — jadwal upload 6 Juli 2026** | `output/sbn_20260702_201929/video.mp4` (10,03 mnt, 1080p) | Keputusan user 2 Jul: upload tepat 6 Jul (hari pembukaan ORI030) — hook "Tanggal 6 Juli ini" tetap akurat hari itu, re-render tidak wajib. SEBELUM upload: (1) fact-check kupon ORI030 yang diumumkan ~3–5 Jul → sebut di pin comment, atau re-render hook kalau user mau; (2) user pilih judul dari 5 opsi di `metadata_draft.md`. Script approved user; 5 chart data riil.
