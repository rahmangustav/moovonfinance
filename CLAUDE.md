# Moovon Finance — Pipeline Slide Video (v2.0 "SINYAL")

Channel YouTube analisis saham Indonesia, sudut pandang **value investing**
(fokus BUMN & bank besar). Output: video slideshow MP4 1920x1080 via pipeline
Python (PIL + ffmpeg). Balas selalu dalam **Bahasa Indonesia 100%**.

> **v2.0 = full on-brand.** Identitas lama (navy + gold, Space Grotesk + IBM
> Plex Mono, slide foto full-bleed) sudah DIGANTI TOTAL. Video sekarang 100%
> slide on-brand tanpa foto. Jangan pakai jalur lama lagi.

## Pipeline aktif

Entry point tunggal: **`produce.py`**
- `python produce.py render`  → TTS + slide on-brand + chart + compile + thumbnail
  ke `output/run_<timestamp>/`
- `python produce.py upload <run_dir> [--privacy public|unlisted|private]`
- `python produce.py upload <run_dir> --at next`  → **jadwal ke slot default 17:30 WIB (Sel/Rab/Kam)**; YouTube publish otomatis
- `python produce.py upload <run_dir> --at "2026-07-07 17:30"`  → jadwal ke waktu spesifik (WIB)

**Jam upload (WIB):** default publish **17:30 Selasa/Rabu/Kamis** — 1-2 jam sebelum
puncak nonton malam 19:00-22:00. Jangan asal jam; pakai `--at`. Refine pakai data
YouTube Studio "kapan penonton online" begitu subscriber/jam-tayang cukup.

Draft naskah: `assets/draft_script_moovon.md` + `state.json`.

**Shorts 9:16 (`shorts.py`) — HOOK-FIRST (rombak 6 Jul 2026):**
- `python shorts.py script <file.txt>` → **mode utama**: Short mandiri, TTS+subtitle
  baru. Narasi diawali HOOK jadi payoff terdengar DI DETIK 1 (kunci retensi).
  Format skrip: `TICKER:` / `HOOK:` / `BODY:` / `CLOSE:` (opsional). Contoh:
  `assets/short_template.txt`.
- `python shorts.py <run_dir> [--start N] [--cut N] [--hook "a|b"]` → pakai-ulang
  audio video panjang, ambil JENDELA mulai kalimat hook (bukan detik 0/intro).
- Shorts = top-of-funnel utama (data: Shorts 20–34 views vs video panjang 0–7).

**Blok opsional di draft (otomatis jadi slide, angka wajib dari riset):**
- `## VALUATION:` `{"harga":.., "nilai_wajar":.., "catatan":".."}` → gauge Margin
  of Safety otomatis disisipkan setelah section valuasi (verdict BELI/TAHAN/HINDARI
  ditentukan `moovon_theme.verdict()`).
- `## SNAPSHOT:` `{"judul":"..", "metrics":[["Laba","14,7 T","up"], ...]}` → grid
  metrik otomatis setelah section fundamental (warna: up/down/neutral/null).

**Thumbnail = on-brand otomatis** dari slide cover v2.0 (1280x720 JPG), BUKAN foto.

Modul:
- `moovon_theme.py` — **SUMBER KEBENARAN desain** (lihat di bawah).
- `render_slides.py` — renderer slide on-brand: `render_cover`, `render_section`
  (naratif + mode statement bila judul kosong), `render_valuation` (gauge),
  `render_snapshot`, `render_closing`. Pola acuan untuk slide baru.
- `core/visuals.py` — `create_video`: rakit video dari slide on-brand + chart,
  TTS, subtitle burn. TIDAK ada foto/ddgs/Ken Burns.
- `core/chart_templates.py` + `core/moovon_style.py` — chart matplotlib tema
  GELAP v2.0 (line/bar/donut/table/timeline).
- `core/tts.py` (edge-tts `id-ID-GadisNeural` + SRT word-boundary), `core/thumbnail.py`,
  `core/youtube_uploader.py`, `core/subtitle.py` (fallback whisper).
- `core/image_fetcher.py` — **TIDAK dipakai lagi** (video tanpa foto).

## Aturan Desain (WAJIB)

IMPORTANT: Sumber kebenaran desain adalah `moovon_theme.py`. JANGAN pernah
hard-code warna, ukuran font, atau nama font di skrip render. Selalu import
dari modul itu (`from moovon_theme import RGB, SIZE, FONT_FILES, font, verdict,
new_canvas, finalize, DISCLAIMER, ...`).

- Kanvas selalu 1920x1080 (16:9). Ambil dari `WIDTH, HEIGHT, MARGIN_X, MARGIN_Y`.
- Render pakai **supersampling 2x** lalu diperkecil LANCZOS (`new_canvas()` →
  render di koordinat × S → `finalize()`).
- Palet (ambil dari `RGB`):
  - `bg` hitam-hangat `#0F1311` = latar. `panel`/`panel_2` = kartu. `line` = hairline.
  - `text` ivory hangat = teks utama. `text_soft`/`text_dim` = sekunder.
  - `brand` **CITRON `#C6F24E`** = aksen tanda tangan. HANYA untuk furniture
    (logo, garis, highlight, pin harga, header tabel). BUKAN untuk verdict.
  - Sinyal: `up` hijau = diskon/undervalue/naik, `down` merah = premium/turun,
    `neutral` amber = TAHAN.
- Semua ANGKA & TICKER pakai font mono (JetBrains Mono). Judul & bodi pakai
  Archivo (varian Expanded untuk angka/judul hero). Tidak bisa ditawar.
- Satu ide besar per slide. Maksimal 6 baris teks; teks jangan menabrak status bar.
- Logo kiri-atas, ticker emiten kanan-atas (kapsul outline citron), status bar
  gaya terminal di bawah. Chrome bersama ada di `render_slides._chrome()`.

## Elemen Tanda Tangan

Setiap pembahasan valuasi WAJIB memakai gauge **Margin of Safety**
(`render_valuation`): track dengan pin citron = harga, pita hijau = zona nilai
wajar, **arsiran citron = besarnya diskon** (celah harga↔nilai wajar adalah
bintang visual channel). Verdict (BELI/TAHAN/HINDARI) + warnanya DITENTUKAN OLEH
`verdict(price, fair)` di `moovon_theme.py` — jangan tentukan manual. Aturan:
BELI hanya bila margin of safety >= 15%.

## Slide Penutup

YOU MUST menampilkan CTA subscribe + teks `DISCLAIMER` (edukasi, bukan
rekomendasi) di setiap slide penutup (`render_closing`).

## Font (folder `fonts/`)

- Archivo: `Archivo-Black/ExtraBold/SemiBold/Medium/Regular.ttf`
  + `ArchivoExp-Black.ttf`, `ArchivoExp-SemiBold.ttf` (Expanded, angka besar)
- JetBrains Mono: `JetBrainsMono-Bold/SemiBold/Medium/Regular.ttf`
- Peta role → file ada di `FONT_FILES`. Panggil lewat helper `font(role, size)`.
  (Chart matplotlib mendaftarkan font ini via `moovon_style._pick_font()`.)

## Aturan Konten (WAJIB)

- Disclaimer edukasi di **30 detik pertama** + di deskripsi. Frasa voice-over:
  _"Seperti biasa, konten ini cuma untuk edukasi ya — ini bukan saran jual atau beli."_
  **Narasi TTS: JANGAN pakai kata Inggris (mis. "financial advice") atau tanda
  kurung penjelas** — kaku/robotik saat dibacakan. Tulis Bahasa Indonesia lisan natural.
- No pom-pom saham, no clickbait nakut-nakutin.
- Angka HARUS dari riset web nyata — **dilarang mengarang** dari memori model.
- Alur: draft → **STOP tunggu "Data aman, lanjut render"** → render → review →
  **upload publik butuh persetujuan eksplisit**.

## Rujukan

`render_slides.py` = contoh render (cover, section, valuasi/gauge, snapshot,
penutup). Pakai polanya untuk slide baru; selalu tarik nilai dari `moovon_theme.py`.
SOP `memory/sop_loop.md` · gaya `memory/style_moovon.md` · log
`memory/production_log.md` · glossary `memory/kamus_istilah.md` · `state.json`.

## Gaya Komunikasi

Selalu balas dalam **Bahasa Indonesia 100%**. Jangan campur bahasa Inggris.
