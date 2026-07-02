# DRAFT SCRIPT — Cara Kerja Obligasi SBN
**Status:** DRAFT — MENUNGGU REVIEW (jangan render sebelum approval)
**Tanggal riset:** 2 Juli 2026
**Estimasi durasi:** ± 9–10 menit (~1.300 kata)

---

## FACT SHEET (semua angka dari web, diakses 2 Juli 2026)

| Data | Angka | Sumber |
|---|---|---|
| BI-Rate terkini | **5,75%** (RDG 17–18 Juni 2026, naik 25 bps) | bi.go.id, CNN Indonesia |
| Riwayat kenaikan BI-Rate 2026 | 4,75% → 5,25% (20 Mei) → 5,50% (9 Juni) → 5,75% (18 Juni) | CNN Indonesia |
| Kupon ORI029 (Jan 2026) | 5,45% (tenor 3 th) / 5,80% (tenor 6 th), fixed | Bareksa |
| Imbal hasil SR024 (Mar 2026) | 5,55% (3 th) / 5,90% (5 th), fixed | Infonasional |
| Imbalan ST016 (Mei 2026) | Floor 6,05% (T2) / 6,25% (T4); spread 130/150 bps di atas BI-Rate; penyesuaian tiap 11 Feb/Mei/Agu/Nov | Bareksa, Kemenkeu |
| Masa penawaran ORI030 | **6–30 Juli 2026** (kupon fixed, angka BELUM diumumkan per 2 Juli) | Bibit, OCBC, Kompas |
| Sisa jadwal SBN ritel 2026 | SR025 (21 Agu–11 Sep), SBR015 (28 Sep–22 Okt), ST017 (6 Nov–2 Des) — tentatif | OCBC, Kompas, BCA |
| Pajak kupon SBN | **10% final** (deposito: 20%) | Klikpajak, Bareksa |
| Minimal pembelian | Rp1 juta, kelipatan Rp1 juta | Kompas, DJPPR |
| Pembayaran kupon | ORI tiap tanggal 15/bulan; SR/ST/SBR tiap tanggal 10/bulan | Bareksa |

**⚠️ ITEM YANG PERLU DICEK ULANG SEBELUM RENDER:**
1. **Kupon ORI030** — belum diumumkan saat riset. Biasanya rilis 1–3 hari sebelum masa penawaran (≈3–5 Juli). Kalau render setelah 6 Juli, WAJIB masukin angka resminya.
2. Simulasi "kupon ST016 bisa naik ke ±7,05%" adalah ILUSTRASI mekanisme (BI-Rate 5,75% + spread 130 bps), bukan angka resmi — di script sudah diberi kalimat pengaman.
3. Jadwal SBN sisa 2026 bersifat tentatif (disebut di script).

---

## SCRIPT

### HOOK (0:00–0:35)
Tanggal 6 Juli ini, pemerintah buka lagi "lapak utang" buat kita semua — namanya ORI030. Dan timing-nya menarik: Bank Indonesia baru aja naikin suku bunga tiga kali dalam sebulan, sekarang nangkring di 5,75%. Pertanyaannya — kalau lo minjemin duit ke negara, lo dapet apa? Amankah? Dan kenapa banyak orang bilang ini "naik kelas"-nya orang yang biasa nabung deposito?

Di video ini kita bedah cara kerja obligasi negara alias SBN, dari nol, pakai angka asli tahun ini.

Oh iya, satu hal dulu: **konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan (financial advice).** Semua keputusan investasi tetap di tangan lo.

> [VISUAL: Animasi grafik — line chart BI-Rate 2026: 4,75% → 5,25% → 5,50% → 5,75%, highlight tiga kenaikan Mei–Juni]

### SECTION 1 — Obligasi Itu Apa Sih? (0:35–2:00)
Gampangnya gini. Kalau saham itu lo *beli kepemilikan* perusahaan, obligasi itu lo *minjemin duit*. Lo jadi yang punya piutang.

Nah, SBN — Surat Berharga Negara — artinya yang ngutang ke lo itu... negara. Republik Indonesia. Lo minjemin duit ke pemerintah, dipakai buat bangun jalan, sekolah, subsidi, dan isi APBN. Sebagai gantinya, negara bayar "uang sewa" ke lo secara rutin. Uang sewa ini namanya **kupon**.

Analoginya kayak lo ngekosin kamar: duit lo "ngekos" di negara, tiap bulan lo terima uang sewanya, dan pas kontrak habis — istilahnya **jatuh tempo** — duit pokok lo balik utuh.

Tiga kata kunci yang bakal sering muncul:
- **Pokok**: duit yang lo pinjemin.
- **Kupon**: bunga/imbal hasil yang dibayar rutin.
- **Tenor**: lamanya kontrak, misal 2, 3, atau 6 tahun.

> [VISUAL: Infografis alur — "Duit lo → Negara (APBN) → Kupon tiap bulan → Pokok balik saat jatuh tempo"]

### SECTION 2 — Empat Keluarga SBN Ritel (2:00–4:00)
SBN ritel — yang bisa dibeli orang biasa mulai **Rp1 juta** — ada 4 keluarga. Bedanya cuma di dua hal: konvensional atau syariah, dan bisa dijual lagi atau nggak.

1. **ORI** (Obligasi Negara Ritel) — konvensional, kupon **tetap**, dan **bisa diperjualbelikan** di pasar sekunder setelah periode tertentu.
2. **SR** (Sukuk Ritel) — kembarannya ORI versi **syariah**, imbal hasil tetap, bisa diperjualbelikan.
3. **SBR** (Savings Bond Ritel) — konvensional, kupon **mengambang** alias floating, dan **gak bisa dijual** — kayak deposito, dikunci sampai jatuh tempo.
4. **ST** (Sukuk Tabungan) — kembarannya SBR versi syariah.

Tahun 2026 ini semuanya kebagian jatah terbit. Yang udah lewat: ORI029 kuponnya 5,45% untuk 3 tahun dan 5,80% untuk 6 tahun. SR024: 5,55% dan 5,90%. ST016: mulai dari 6,05%.

> [VISUAL: Comparison table 4 keluarga SBN — kolom: Konvensional/Syariah, Kupon Fixed/Floating, Tradable/Non-tradable, Tenor]
> [VISUAL: Bar chart perbandingan kupon seri 2026 — ORI029 (5,45 / 5,80), SR024 (5,55 / 5,90), ST016 floor (6,05 / 6,25)]

### SECTION 3 — Cara Kerja Kuponnya, Pakai Angka Beneran (4:00–6:00)
Oke, sekarang bagian yang paling sering ditanya: *duitnya gimana?*

Misal lo beli ORI029 tenor 3 tahun senilai **Rp10 juta**, kupon 5,45% per tahun.
- Setahun: Rp10 juta × 5,45% = **Rp545.000**.
- Dibagi 12 bulan: sekitar **Rp45.400** per bulan.
- Kena pajak final 10%, jadi bersihnya sekitar **Rp40.900** masuk rekening tiap tanggal 15.

Kecil? Inget, ini per Rp10 juta. Dan poin pentingnya: angka ini **pasti**, gak peduli pasar lagi drama apa, karena kuponnya fixed. Tiga tahun kemudian, pokok Rp10 juta lo balik utuh.

Nah, yang tipe **floating with floor** kayak ST016 beda cara mainnya. Kuponnya ngikutin BI-Rate, disesuaikan tiap 3 bulan, dengan "lantai" yang gak bisa ditembus ke bawah. ST016 tenor 2 tahun floor-nya 6,05% — itu udah BI-Rate waktu itu plus spread 1,30%. Sekarang BI-Rate udah naik ke 5,75%. Artinya apa? Kalau BI-Rate bertahan di situ sampai penyesuaian berikutnya di 11 Agustus, imbalan ST016 *bisa* ikut naik jadi sekitar 7,05%. Ini ilustrasi mekanisme ya, bukan janji — angkanya tetap nunggu penetapan resmi.

Jadi: suku bunga lagi tren naik → floating diuntungin. Suku bunga tren turun → fixed yang menang, dan floating dilindungi floor. Itu logika dasarnya.

> [VISUAL: Infografis simulasi Rp10 juta → Rp545rb/tahun → Rp45,4rb/bulan → potong pajak 10% → Rp40,9rb bersih]
> [VISUAL: Animasi grafik — mekanisme floating with floor: garis BI-Rate naik-turun, garis kupon ngikutin tapi mentok di floor]

### SECTION 4 — Amannya di Mana, Risikonya di Mana (6:00–7:30)
Kenapa SBN sering disebut instrumen paling aman di Indonesia? Karena pembayaran pokok dan kuponnya **dijamin undang-undang**, dibayar dari APBN. Negara gagal bayar warganya sendiri itu skenario yang jauh lebih ekstrem daripada bank kesulitan — dan deposito aja penjaminannya lewat LPS dengan batas tertentu.

Tapi "aman" bukan berarti tanpa risiko. Dua yang perlu lo tau:

**Risiko likuiditas.** SBR dan ST gak bisa dijual sebelum jatuh tempo. Ada fasilitas *early redemption* buat nyairin sebagian di jendela waktu tertentu — tapi terbatas dan ada syaratnya. Jadi jangan taruh dana darurat di sini.

**Risiko harga pasar.** ORI dan SR bisa dijual sebelum jatuh tempo, tapi harganya ngikutin pasar. Kalau suku bunga naik, harga obligasi lama cenderung turun — lo bisa rugi kalau maksa jual. Dipegang sampai jatuh tempo? Pokok balik 100%.

Satu lagi yang sering kelewat: **pajak**. Kupon SBN kena pajak final cuma **10%**. Bandingin bunga deposito yang kena **20%**. Selisih 10% itu, buat dana ratusan juta, bukan angka kecil.

> [VISUAL: Chart perbandingan pajak — bar 10% (SBN) vs 20% (deposito)]
> [VISUAL: Animasi grafik hubungan terbalik suku bunga vs harga obligasi]

### SECTION 5 — Cara Beli & Jadwal Sisa Tahun Ini (7:30–8:45)
Belinya gampang dan full online: lewat mitra distribusi resmi — bank, sekuritas, atau aplikasi fintech yang terdaftar. Daftar SID (Single Investor Identification), pesan pas masa penawaran buka, bayar, selesai. Minimal **Rp1 juta**.

Kalender sisa 2026 — catat, jadwal ini tentatif dari Kemenkeu:
- **ORI030: 6–30 Juli** — paling dekat. Kuponnya diumumkan menjelang pembukaan, cek di situs resmi DJPPR atau mitra distribusi.
- SR025: 21 Agustus–11 September
- SBR015: 28 September–22 Oktober
- ST017: 6 November–2 Desember

> [VISUAL: Timeline jadwal SBN ritel 2026, highlight ORI030]
> [VISUAL: Screen recording — halaman SBN di salah satu mitra distribusi (tampilkan alur pemesanan, blur data pribadi)]

### CTA (8:45–9:30)
Jadi, obligasi SBN itu intinya: lo minjemin duit ke negara, dibayar kupon rutin tiap bulan, pokok balik pas jatuh tempo, dijamin undang-undang, pajaknya lebih ringan dari deposito. Bukan instrumen buat kaya cepat — ini instrumen buat duit lo kerja pelan tapi pasti.

Kalau video ini bikin lo lebih ngerti SBN, bantu channel ini dengan like dan subscribe — biar makin banyak orang Indonesia yang melek finansial. Tulis di komentar: lo tim kupon fixed atau floating? Sampai ketemu di video Moovon Finance berikutnya.

**Sekali lagi: ini konten edukasi, bukan ajakan beli produk tertentu. Selalu riset sendiri sebelum investasi.**

---

## CHARTS: (spec untuk render_chart — final saat Fase 2)
```json
[
  {"type": "line", "title": "BI-Rate 2026: Naik 3x dalam Sebulan", "section": 0, "x": ["Jan–Apr", "20 Mei", "9 Jun", "18 Jun"], "series": [{"label": "BI-Rate (%)", "data": [4.75, 5.25, 5.50, 5.75]}], "source": "Bank Indonesia"},
  {"type": "comparison_table", "title": "4 Keluarga SBN Ritel", "section": 2, "columns": ["Seri", "Prinsip", "Kupon", "Bisa Dijual Lagi?"], "rows": [["ORI", "Konvensional", "Tetap", "Ya"], ["SR", "Syariah", "Tetap", "Ya"], ["SBR", "Konvensional", "Mengambang + floor", "Tidak"], ["ST", "Syariah", "Mengambang + floor", "Tidak"]], "source": "DJPPR Kemenkeu"},
  {"type": "bar", "title": "Kupon SBN Ritel 2026 (% per tahun)", "section": 2, "categories": ["ORI029 3th", "ORI029 6th", "SR024 3th", "SR024 5th", "ST016 2th*", "ST016 4th*"], "data": [5.45, 5.80, 5.55, 5.90, 6.05, 6.25], "note": "*floor (minimal), bisa naik ikut BI-Rate", "source": "DJPPR Kemenkeu, per Juli 2026"},
  {"type": "bar", "title": "Pajak Imbal Hasil: SBN vs Deposito", "section": 4, "categories": ["Kupon SBN", "Bunga Deposito"], "data": [10, 20], "source": "PP 91/2021"},
  {"type": "timeline", "title": "Jadwal SBN Ritel Sisa 2026 (tentatif)", "section": 5, "events": [{"label": "ORI030", "date": "6–30 Jul"}, {"label": "SR025", "date": "21 Agu–11 Sep"}, {"label": "SBR015", "date": "28 Sep–22 Okt"}, {"label": "ST017", "date": "6 Nov–2 Des"}], "source": "DJPPR Kemenkeu"}
]
```

## Sumber (diakses 2 Juli 2026)
- https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_2812626.aspx (BI-Rate 5,75%)
- https://www.cnnindonesia.com/ekonomi/20260618143411-78-1370442/bi-rate-naik-25-bps-lagi-jadi-575-persen-per-18-juni (riwayat kenaikan)
- https://www.bareksa.com/berita/sbn/2026-01-23/kupon-obligasi-negara-ritel-ori029-resmi-545-58-hampir-2x-deposito (kupon ORI029)
- https://www.infonasional.com/pemerintah-tawarkan-sukuk-ritel-sr024-kupon-5-90-persen (SR024)
- https://www.bareksa.com/berita/sbn/2026-05-12/kupon-st016-floating-with-floor-ada-proteksi-batas-minimum-imbalan (ST016 floor & spread)
- https://www.ocbc.id/en/article/2026/01/26/jadwal-sbn-ritel-2026-lengkap-ori-sr-st-dan-sbr-dari-januari-desember (jadwal 2026)
- https://money.kompas.com/read/2026/05/20/101021726/st016-masih-dibuka-hingga-3-juni-ini-jadwal-lengkap-sbn-ritel-2026 (jadwal)
- https://bibit.id/sbn (ORI030 mulai 6 Juli)
- https://klikpajak.id/blog/surat-berharga-negara/ (pajak 10% final)
- https://money.kompas.com/read/2026/05/09/104811126/sukuk-tabungan-st016-sudah-bisa-dibeli-minimal-investasi-rp-1-juta (minimal Rp1 juta)
