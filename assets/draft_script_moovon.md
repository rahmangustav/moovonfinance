# DRAFT SCRIPT — Bedah Saham BMRI (Bank Mandiri)
**Status:** DRAFT — MENUNGGU REVIEW (jangan render sebelum approval)
**Tanggal riset:** 3 Juli 2026
**Estimasi durasi:** ± 9–10 menit (~1.400 kata)
**Visual:** Fase 2 pakai workflow baru — slide didesain di Canva per section + chart matplotlib lokal

---

## FACT SHEET (semua angka dari web, diakses 3 Juli 2026)

| Data | Angka | Sumber |
|---|---|---|
| Laba bersih FY2025 (konsolidasi, atribusi pemilik) | **Rp56,3 T** (+0,93% dari Rp55,78 T di 2024) | IDN Financials, Indopremier, Databoks |
| Kredit FY2025 (konsolidasi) | Rp1.895 T (+13,4% yoy) | IDN Financials |
| NPL gross akhir 2025 | **0,96%**, coverage ratio 253% | IDN Financials |
| Pendapatan bunga bersih 2025 | Rp106 T (+4,38%); non-bunga Rp48,5 T (+14,5%) | IDN Financials |
| DPK 2025 | Rp2.106 T (+23,9%); dana murah Rp1.431 T (+12,6%) | IDN Financials |
| Aset 2025 | Rp2.829,95 T (+16,6%); CAR 20,4% | IDN Financials |
| Laba Q1 2026 | **Rp15,4 T** (+16,6% yoy); ROE 22,1%; NPL 0,98%; CAR 19,7% | Bisnis, iNews, IDX Channel, Databoks |
| Harga saham (2 Jul 2026) | **Rp3.900** (rebound harian +2,36%; -3,7% sebulan; **-17,7% setahun**) | TradingEconomics |
| Kapitalisasi pasar | Rp367,4 T (per 2 Jul, -11,2% seminggu) | TradingView/Stockbit |
| Dividen tahun buku 2025 | **Rp476,9569/saham** (interim Rp100 + final Rp376,9569); yield TTM ±12,1–12,2% di harga sekarang | Bareksa (4 Mei 2026) |
| Konsensus analis | 17 analis, rata-rata TP **Rp5.301** (kisaran 3.600–7.300) → upside ±36% dari 3.900 | TradingView |
| TP sekuritas individual | Samuel 5.700 · MNC 6.050 · BRI Danareksa 6.200 (proy. yield 8,3%) · Macquarie 6.240 · CGS 6.700 · UBS 7.950 | Investortrust |
| Konteks koreksi 30 Jun | IHSG -3,05% ke 5.643; bank besar rontok (BBRI -3,87% ke 2.730) | Databoks Katadata |
| Penyebab tekanan | Sensitivitas BI-Rate (5,75%, naik 3x dlm sebulan), net sell asing, sentimen reshuffle kabinet, tarif impor AS 32% berlaku 1 Agustus | Investortrust, Investor.id |

**⚠️ CATATAN KONSISTENSI DATA (untuk review lo):**
1. Angka kredit Q1 2026 (Rp1.530 T) dan DPK Q1 (Rp1.675 T) kemungkinan **bank-only**, beda basis dari angka FY2025 yang konsolidasi (Rp1.895 T / Rp2.106 T) — script sengaja TIDAK membandingkan keduanya langsung.
2. Laba Q1 2025 (±Rp13,2 T) adalah turunan aritmetika dari "+16,6%", bukan angka yang diberitakan langsung — di script cuma disebut pertumbuhannya, bukan angka Q1 2025.
3. Yield dividen ±12% adalah TTM di harga sekarang (karena harga turun); proyeksi analis pakai asumsi beda (7–8,3%). Script membedakan keduanya.

---

## SCRIPT

### HOOK (0:00–0:35)
Ada yang aneh di saham Bank Mandiri. Kuartal pertama tahun ini labanya naik 16,6 persen — salah satu yang paling kencang di antara bank besar. Tapi harga sahamnya? Turun hampir 18 persen dalam setahun, dan minggu lalu ikut rontok bareng IHSG. Laba naik, harga turun. Buat sebagian orang ini alarm. Buat sebagian lagi, ini... diskon. Kita bedah datanya, bukan feeling-nya.

Dan sebelum mulai: **konten ini untuk tujuan edukasi, bukan merupakan nasihat keuangan (financial advice).** Bukan ajakan beli atau jual. Keputusan tetap di tangan lo.

> [CANVA: hook slide — teks "LABA NAIK 16%, SAHAM TURUN 18%?" gaya kontras hijau/merah]

### SECTION 1 — Kenalan Dulu: Sebesar Apa Bank Mandiri (0:35–2:00)
Bank Mandiri itu bank dengan aset terbesar di Indonesia. Akhir 2025, asetnya tembus dua ribu delapan ratus tiga puluh triliun rupiah — naik 16,6 persen dalam setahun. Kalau BRI yang pernah kita bedah itu rajanya kredit mikro dan UMKM, Mandiri main di lapangan yang beda: kredit korporasi dan wholesale — perusahaan-perusahaan gede, BUMN, proyek — ditambah mesin digital yang lagi ngebut, aplikasi Livin' by Mandiri.

Kenapa ini penting? Karena karakter bisnisnya beda. Kredit korporasi itu marginnya lebih tipis dari mikro, tapi risikonya juga lebih terkendali. Dan itu kelihatan banget di satu angka yang bakal kita bahas nanti: rasio kredit macetnya termasuk yang paling rendah di industri.

> [CANVA: slide profil — logo/siluet Mandiri + 3 angka kunci: aset Rp2.830 T, kredit Rp1.895 T, DPK Rp2.106 T]

### SECTION 2 — Kinerja: Mesinnya Masih Ngebut (2:00–4:00)
Kita lihat rapornya. Tahun 2025 penuh, laba bersih Mandiri Rp56,3 triliun. Naiknya memang tipis — cuma 0,9 persen dari tahun sebelumnya — tapi inget, 2025 itu tahun yang berat buat perbankan: suku bunga tinggi, ekonomi melambat. Yang menarik justru mesin di baliknya. Kredit tumbuh 13,4 persen jadi seribu delapan ratus sembilan puluh lima triliun. Dana pihak ketiga naik 23,9 persen. Pendapatan non-bunga — fee dari Livin', transaksi, treasury — melonjak 14,5 persen jadi Rp48,5 triliun.

Terus masuk 2026, kuartal pertama: laba Rp15,4 triliun, naik 16,6 persen dibanding periode yang sama tahun lalu. Return on equity 22 persen — artinya tiap seratus rupiah modal, setahun bisa jadi laba dua puluh dua rupiah. Buat bank sebesar ini, itu angka yang sehat banget.

Jadi kalau lihat dapurnya doang: gak ada tanda-tanda mesin rusak. Justru lagi kenceng.

> [CHART: bar pertumbuhan FY2025 & Q1 2026 (%)]
> [CANVA: big-number "Rp15,4 T — laba kuartal I 2026, +16,6%"]

### SECTION 3 — Terus Kenapa Sahamnya Turun? (4:00–6:00)
Nah, ini bagian pentingnya. Harga saham BMRI sekarang di sekitar tiga ribu sembilan ratus rupiah. Setahun terakhir turun hampir 18 persen. Akhir Juni kemarin bahkan ikut kena panic selling waktu IHSG anjlok tiga persen sehari dan saham bank besar rontok berjamaah.

Penyebabnya bukan dari dalam dapur Mandiri — tapi dari luar. Setidaknya ada empat: Pertama, Bank Indonesia naikin suku bunga tiga kali dalam sebulan sampai ke 5,75 persen, dan saham bank memang paling sensitif sama ini karena biaya dana naik. Kedua, investor asing lagi keluar — net sell terus-terusan di saham BUMN. Ketiga, sentimen politik: isu reshuffle kabinet bikin pasar gugup sama saham pelat merah. Keempat, dari luar negeri: tarif impor Amerika 32 persen buat produk Indonesia yang mulai berlaku 1 Agustus, bikin pasar waswas soal ekonomi ke depan.

Poinnya gini: laba naik, harga turun — itu artinya pasar lagi menghukum sektor dan negaranya, bukan perusahaannya. Tapi hati-hati, ini bukan berarti besok langsung balik. Sentimen kayak gini bisa lama, dan harga bisa turun lebih dalam dulu sebelum pulih.

> [CANVA: slide 4 faktor tekanan — ikon BI rate, asing keluar, politik, tarif AS]
> [CHART: table profil saham BMRI]

### SECTION 4 — Kualitas Aset & Dividen: Dua Jangkar (6:00–7:45)
Di tengah tekanan kayak gini, ada dua angka yang bikin BMRI beda. Pertama, kualitas aset. Rasio kredit macet alias NPL gross-nya cuma nol koma sembilan enam persen di akhir 2025 — dan di kuartal satu 2026 masih terjaga di nol koma sembilan delapan. Bandingin sama BRI yang NPL-nya tiga koma dua sembilan persen karena main di segmen mikro yang lebih rawan. Dan Mandiri udah nyiapin "dana jaga-jaga" alias pencadangan dua setengah kali lipat dari kredit macetnya. Konservatif.

Kedua, dividen. Untuk tahun buku 2025, Mandiri bagi Rp476,96 per saham. Di harga sekarang, itu setara imbal hasil sekitar dua belas persen — angka yang gede karena harganya lagi turun. Catatan penting: yield segede ini gak otomatis keulang tiap tahun; kalau harga naik atau laba berubah, yield-nya ikut berubah. Proyeksi analis untuk ke depan lebih konservatif, di kisaran tujuh sampai delapan persen. Tetap termasuk yang tertinggi di bursa.

> [CHART: bar NPL gross BMRI 0,96% vs BBRI 3,29%]
> [CANVA: big-number "Rp476,96/saham — dividen tahun buku 2025"]

### SECTION 5 — Kata Analis & Valuasinya (7:45–8:45)
Terus pasar profesional lihatnya gimana? Konsensus tujuh belas analis yang dirangkum TradingView kasih target harga rata-rata lima ribu tiga ratus rupiah — sekitar 36 persen di atas harga sekarang. Yang paling pesimis di tiga ribu enam ratus, yang paling optimis — UBS — sampai tujuh ribu sembilan ratus lima puluh. MNC, Danareksa, Macquarie, CGS semuanya di kisaran enam ribuan, dan mayoritas rekomendasinya beli.

Tapi inget dua hal. Target harga itu opini, bukan janji — analis juga sering salah. Dan konsensus dibuat sebelum tahu gimana dampak tarif Amerika beneran kerasa. Jadi pakai ini sebagai satu bahan pertimbangan, bukan satu-satunya.

> [CHART: bar target harga 6 sekuritas + garis harga sekarang Rp3.900]

### KESIMPULAN (8:45–9:30)
Jadi, BMRI hari ini: bisnis lagi sehat — laba kuartalan naik dua digit, kredit macet terendah di kelasnya, dividen jumbo. Sahamnya lagi murah bukan karena perusahaannya bermasalah, tapi karena pasarnya lagi takut — suku bunga, asing keluar, politik, tarif. Buat investor jangka pendek, ini zona yang gak nyaman. Buat yang horizonnya panjang dan ngerti risikonya, sejarah bilang momen kayak gini justru yang sering dicari. Yang mana lo? Itu keputusan lo, sesuai profil risiko lo — dan sekali lagi, ini edukasi, bukan rekomendasi beli atau jual.

> [CANVA: slide kesimpulan — dua kolom "Fundamental ✓" vs "Sentimen ✗"]

### CTA (9:30–10:00)
Kalau lo mau saham lain dibedah kayak gini — data dulu, baru opini — tulis di komentar. Jangan lupa like, subscribe, dan nyalain lonceng, biar makin banyak orang Indonesia yang melek finansial. Sampai ketemu di video Moovon Finance berikutnya.

---

## CHARTS: (matplotlib lokal — angka terkunci dari fact sheet)
```json
[
  {"type": "bar", "section": "SECTION 2", "judul": "Mesin BMRI Tetap Tumbuh (% yoy)", "sumber": "Laporan Keuangan BMRI", "horizontal": true,
   "kategori": ["DPK 2025", "Laba Q1 2026", "Non-bunga 2025", "Kredit 2025", "Laba FY 2025"],
   "nilai": [23.9, 16.6, 14.5, 13.4, 0.9]},
  {"type": "table", "section": "SECTION 3", "judul": "Profil Saham BMRI", "sumber": "BEI & TradingView, per 2 Jul 2026",
   "headers": ["Indikator", "Nilai"],
   "rows": [["Harga Saham", "Rp3.900"], ["Kapitalisasi Pasar", "Rp367,4 T"], ["Kinerja 1 Tahun", "-17,7%"], ["Dividen / Saham (2025)", "Rp476,96"], ["Yield (TTM)", "±12%"], ["Target Konsensus (17 analis)", "Rp5.301"], ["Potensi Upside", "+36%"]]},
  {"type": "bar", "section": "SECTION 4", "judul": "NPL Gross 2025: Mandiri vs BRI (%)", "sumber": "Laporan Keuangan BMRI & BBRI 2025",
   "kategori": ["BMRI", "BBRI"], "nilai": [0.96, 3.29]},
  {"type": "bar", "section": "SECTION 5", "judul": "Target Harga Analis vs Harga Sekarang (Rp)", "sumber": "Investortrust & TradingView, Jul 2026", "horizontal": true,
   "kategori": ["Harga sekarang", "Samuel", "MNC", "BRI Danareksa", "Macquarie", "CGS", "UBS"],
   "nilai": [3900, 5700, 6050, 6200, 6240, 6700, 7950]}
]
```

## Sumber (diakses 3 Juli 2026)
- https://www.idnfinancials.com/id/news/59701/npl-sehat-bmri-catat-laba-bersih-rp5-26-triliun-pada-november-2025
- https://www.indopremier.com/ipotnews/newsDetail.php?news_id=212956 (laba FY2025 Rp56,3 T)
- https://finansial.bisnis.com/read/20260422/90/1968420/bank-mandiri-catat-laba-rp154-triliun-di-kuartal-i-2026
- https://databoks.katadata.co.id/en/market/statistics/69eaf48547e47/bank-mandiri-bmri-profit-rises-16-in-q1-2026
- https://id.tradingeconomics.com/bmri:ij (harga Rp3.900, -17,7% yoy)
- https://www.bareksa.com/berita/saham/2026-05-04/bmri-tebar-dividen-jumbo-rp47695-per-saham-yield-menarik
- https://id.tradingview.com/symbols/IDX-BMRI/forecast/ (konsensus 17 analis TP Rp5.301)
- https://investortrust.id/market/101651/intip-prospek-saham-bmri-rekomendasi-beli-dengan-target-harga-rp-5660-6200
- https://databoks.katadata.co.id/datapublish/2026/06/30/ihsg-anjlok-3-harga-saham-bank-besar-turun-selasa-30-juni-2026
- https://investor.id/market/431882/penyebab-saham-bbri-bmri-cs-anjlok
