# DRAFT — Short GGRM: Dividen Jumbo

**Status:** DRAFT — MENUNGGU APPROVAL ("Data aman, lanjut render")
**Tanggal riset:** 18 Juli 2026
**Format:** Short mandiri (`shorts.py script`), TTS+subtitle baru, 9:16.
**Topik:** Dividen tunai Gudang Garam (GGRM) 2026 — belum pernah dibahas channel (cek `memory/production_log.md`, tidak ada match "GGRM"/"Gudang Garam").
**Catatan:** draft LONG sebelumnya (ICBP "Cara Baca Laporan Keuangan dari Nol") diarsipkan ke `assets/draft_script_ICBP_20260715_PENDING.md` — belum diselesaikan, tapi dilepas dulu sesuai arahan user, prioritas sekarang format Short (LONG terbukti nyaris nol penonton).

## Riset & Sumber (diambil 18 Jul 2026)
- Dividen tunai **Rp800/saham**, naik **60%** dari tahun buku sebelumnya (Rp500/saham). Total **Rp1,54 triliun**, setara **98,9%** dari laba bersih tahun buku 2025 (Rp1,556 triliun). — [Bareksa](https://www.bareksa.com/berita/saham/2026-06-25/gudang-garam-ggrm-bagi-dividen-rp800-per-saham-cek-jadwal-cum-dividen-hingga-pembayarannya), [Bisnis.com](https://market.bisnis.com/read/20260625/192/1983266/gudang-garam-ggrm-bagikan-dividen-rp153-triliun-dari-laba-bersih-2025)
- Jadwal: cum dividen pasar reguler **1 Juli 2026**, recording date **3 Juli 2026**, **dibayar 23 Juli 2026**. — [Bareksa](https://www.bareksa.com/berita/saham/2026-06-25/gudang-garam-ggrm-bagi-dividen-rp800-per-saham-cek-jadwal-cum-dividen-hingga-pembayarannya), [IDX Channel](https://www.idxchannel.com/market-news/catat-jadwal-dividen-gudang-garam-ggrm-rp800-per-saham)
- Laba bersih kuartal I-2026: **Rp1,5 triliun** — disebut setara ±50% dari estimasi konsensus laba setahun (hasil pencarian web 18 Jul 2026, konsisten di beberapa outlet).
- Harga saham GGRM per 10 Jul 2026: **±Rp16.400** (range 52 minggu Rp8.300–Rp17.975; naik ±87% dalam setahun, ±13% dalam sebulan) — sumber agregat tradingeconomics/investing.com, hasil pencarian web 18 Jul 2026.
- **CATATAN PENTING:** cum dividen sudah LEWAT (1 Jul 2026) — pembeli saham SEKARANG (18 Jul) TIDAK dapat dividen ini. Script sengaja menegaskan ini di CLOSE supaya tidak menyesatkan (bukan ajakan "buru-buru beli").

## Angka yang SENGAJA TIDAK dipakai
- Yield dividen (800/16.400 ≈ 4,9%) — tidak disebut eksplisit karena bisa membingungkan mengingat cum date sudah lewat; payout ratio (98,9%) lebih jujur mewakili "cerita"-nya dan tidak butuh konteks tambahan.

## Script (`shorts.py script` format)

```
TICKER: GGRM
HOOK: Gudang Garam bagi dividen Rp800 per saham, naik 60 persen dari tahun lalu.
BODY: Totalnya Rp1,54 triliun, itu hampir seluruh laba bersih tahun 2025, sampai 98,9 persen dibagi ke pemegang saham. Dividen ini dibayar 23 Juli. Uniknya, kuartal pertama tahun ini labanya sudah Rp1,5 triliun sendiri, setara separuh dari perkiraan laba setahun, jadi dividen jumbo ini didukung kinerja yang lagi kencang.
CLOSE: Catatan, periode beli buat dapat dividen ini sudah lewat awal Juli, jadi ini bukan ajakan buru-buru beli sekarang.
```

Estimasi kata: HOOK 13 + BODY 45 + CLOSE 18 = **76 kata** → est. ±48 detik pada 1,6 kata/detik (di bawah batas 60 detik, aman dari anggaran 85 kata).

## Cek pantangan
- Tidak ada rekomendasi beli/jual spesifik (bahkan eksplisit "bukan ajakan buru-buru beli").
- Tidak ada kata Inggris/tanda kurung penjelas di narasi.
- Tidak clickbait menakutkan — hook faktual, bukan sensasi.
- Semua angka bersumber & bertanggal (lihat Riset & Sumber di atas).

## Metadata usulan (draft, boleh direvisi saat finishing)
- **Judul (5 opsi):**
  1. Gudang Garam Bagi Dividen Rp800 per Saham, Naik 60 Persen
  2. Dividen GGRM Rp1,54 Triliun — 98,9 Persen dari Labanya Dibagi
  3. Kenapa Gudang Garam Bagi Hampir Semua Labanya Sebagai Dividen?
  4. GGRM: Dividen Jumbo Rp800, Dibayar 23 Juli
  5. Rahasia Dividen Jumbo Gudang Garam 2026
- **Tags:** GGRM, Gudang Garam, dividen saham, dividen jumbo, saham dividen Indonesia, IHSG, investasi saham pemula

## STATUS: MENUNGGU APPROVAL
Belum di-render. Tunggu konfirmasi persis **"Data aman, lanjut render"** sebelum lanjut ke Fase 2 (TTS + render Short + review visual — upload tetap butuh approval terpisah).

---

## VERIFIKASI ULANG INDEPENDEN — 19 Juli 2026

Seluruh angka dicek ulang lewat pencarian web baru, bukan mengandalkan catatan
riset 18 Juli. **Hasil: 6 dari 6 klaim COCOK, tidak ada koreksi angka.**

| Klaim di draft | Hasil verifikasi |
|---|---|
| Dividen Rp800 per saham | cocok |
| Naik 60% dari Rp500 (tahun buku 2024) | cocok — TB2024 memang Rp500/saham, total Rp962 M, 98% dari laba Rp981 M |
| Total Rp1,54 triliun | cocok — angka resmi Rp1,539 T |
| Payout 98,9% dari laba bersih 2025 (Rp1,556 T) | cocok |
| Cum 1 Juli · recording 3 Juli · bayar 23 Juli 2026 | cocok — RUPST 23 Juni 2026, Kediri |
| Laba Q1-2026 Rp1,5 T ≈ 50% konsensus setahun | cocok — laba kuartalan tertinggi sejak awal 2023 |

### ⏳ TENGGAT: draft ini basi setelah 23 Juli 2026
Dividennya **dibayar 23 Juli**. Setelah tanggal itu, hook "dibayar 23 Juli"
berubah dari berita jadi arsip. Kalau mau tayang, idealnya sebelum 23 Juli —
sisa **4 hari** dari 19 Juli.

### ⚠️ RISIKO PEMBINGKAIAN (bukan salah angka, tapi perlu diputuskan)
Kalimat BODY *"dividen jumbo ini didukung kinerja yang lagi kencang"* berdiri
sendiri terlalu cerah, dan berbenturan dengan pantangan kanal "no pom-pom
saham". Konteks yang tidak disebut draft, semuanya terverifikasi:

- Lonjakan laba Q1-2026 datang dari **basis yang ambruk**: Q1-2025 hanya
  Rp104,43 miliar, jadi kenaikannya +1.372% justru karena tahun lalu nyaris nol.
- **Pendapatan masih TURUN** — pendapatan semester I-2025 Rp44,36 T, −11,3%
  tahun ke tahun. Labanya naik lewat efisiensi & margin kotor, bukan penjualan.
- Laba 2024 sendiri sudah anjlok **−81,6%** (Rp980,8 M dari Rp5,32 T di 2023).
- Ada program efisiensi tenaga kerja: **308–309 karyawan** dilepas lewat pensiun
  reguler, pensiun dini, dan kontrak habis. Manajemen membantah PHK massal lewat
  surat resmi ke BEI; serikat menyebut penyebabnya produksi SKM menurun.
  *(Angka "23,5% tenaga kerja" sempat muncul di satu judul media tapi TIDAK
  berhasil dikonfirmasi — jangan dipakai.)*

**Usulan koreksi satu kalimat di BODY** — ganti
*"jadi dividen jumbo ini didukung kinerja yang lagi kencang"* menjadi:

> *"Tapi perlu dicatat, lonjakan labanya datang dari efisiensi, bukan dari
> penjualan yang naik — pendapatannya sendiri masih turun."*

Lebih jujur, tetap ringkas, dan justru lebih menarik karena memberi penonton
sesuatu yang tidak mereka dapat dari judul berita biasa. Keputusan tetap di
tangan pemilik.

**Status data: bersih, siap dirender.** Tinggal putuskan soal pembingkaian di
atas, lalu kalimat persis: "Data aman, lanjut render".

