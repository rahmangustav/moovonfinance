# Style Guide — Moovon Finance

## Identitas Channel
- **Nama:** Moovon Finance
- **Niche:** Finance — personal finance, investasi, analisis market, melek finansial (Indonesia).
- **Audience:** Investor pemula, anak muda/profesional yang mau ngatur duit, orang awam yang mau paham istilah ekonomi.

## Suara & Gaya
Objektif, terpercaya, analitis tapi dibawain santai — kayak ngobrol sama temen yang pinter finansial. Gak kaku, gak sok akademis. Bahasa Indonesia sehari-hari, istilah teknis selalu dijelasin sekali dengan analogi sederhana.

## PANTANGAN (hard rules)
1. **JANGAN** ngasih rekomendasi beli/jual aset spesifik (pom-pom saham/kripto).
2. **JANGAN** pakai data angka salah/kadaluarsa. HALUSINASI DATA = DOSA BESAR — semua angka wajib dari web-search/tool dengan sumber & tanggal.
3. **JANGAN** clickbait yang nakut-nakutin (contoh terlarang: "EKONOMI HANCUR BESOK!").
4. **JANGAN** lupa disclaimer.

## Aturan Khusus Finance
1. **FACT-CHECKING WAJIB:** data suku bunga BI, inflasi, harga saham, PDB, dll → ambil dari web-search/tool terbaru, catat sumber + tanggal akses. Dilarang ngarang dari memori internal model.
2. **DISCLAIMER WAJIB** di 30 detik pertama script. Frasa VOICE-OVER (natural, JANGAN pakai kata Inggris "advice"/"financial advice" — kaku/robotik di TTS):
   > "Seperti biasa, konten ini cuma untuk edukasi ya — ini bukan saran jual atau beli."
   Disclaimer juga wajib ada di deskripsi video (di deskripsi teks boleh lebih formal, tapi tetap tanpa "(financial advice)").
   **ATURAN UMUM NARASI:** hindari kata/istilah Inggris & tanda kurung penjelas di teks yang dibacakan TTS — tulis apa adanya dalam Bahasa Indonesia lisan biar terdengar natural.
3. **VISUAL DATA:** kalau bahas angka, prompt visual harus minta "chart", "grafik perbandingan", atau "infografis" — jangan cuma B-roll orang ngitung duit. Ikuti sistem desain FinanceViz (CLAUDE.md root project).

## Judul & Metadata
- 5 opsi judul: SEO friendly, jujur, gak clickbait murahan.
- Deskripsi: lengkap dengan timestamp + disclaimer.
- Tags relevan niche finance Indonesia.

## Anggaran kata naskah Shorts (pelajaran 12 Jul 2026)

Shorts WAJIB <60 dtk. Patokan kecepatan `id-ID-GadisNeural` untuk naskah padat
angka: **±1,6 kata/detik** — JAUH lebih lambat dari perkiraan intuitif, karena
angka dibaca panjang ("15,5 triliun" → "lima belas koma lima triliun").

- Target aman: **±85 kata TOTAL** (HOOK + BODY + CLOSE) → ±55 dtk.
- 115 kata → 72,8 dtk = LEWAT BATAS (kejadian nyata di Short BBRI, harus render ulang).
- Kalau kepanjangan: buang angka sekunder (pertumbuhan kredit, target analis),
  bukan memampatkan kalimat. Satu ide besar per Short.
- `shorts.py` memang memperingatkan bila >58 dtk, tapi TETAP merender — cek
  durasi di log sebelum lanjut, jangan asal upload.
