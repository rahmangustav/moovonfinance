# SOP Loop Produksi — Moovon Finance

## TRIGGER
Jalan saat user ketik: **"Bikin video Moovon tentang [topik]"**.

## FASE 1 — DRY-RUN (Riset + Script) → STOP
1. Riset data terbaru via web-search (WAJIB, jangan dari memori internal). Catat sumber + tanggal.
2. Cek `memory/production_log.md` — jangan bahas topik yang persis sama dengan video lama.
3. Bikin outline & script (gaya sesuai `memory/style_moovon.md`, disclaimer di 30 detik pertama).
4. Tandai bagian yang butuh "Screen recording chart" / "Animasi grafik" / chart statis (spec CHARTS: JSON).
5. Simpan ke `assets/draft_script_moovon.md`.
6. **STOP. Tunggu approval user.** User cek kebenaran angka & alur logika sendiri.

## FASE 2 — EKSEKUSI (hanya setelah user bilang "Data aman, lanjut render")
1. Generate Audio (edge-tts `id-ID-GadisNeural`, WordBoundary untuk SRT).
2. **VISUAL via CANVA (keputusan user 2026-07-03):** desain slide per section di Canva
   (generate-design → create-from-candidate → export PNG 1920x1080) sesuai isi script.
   - Chart data TETAP lokal (`scripts/chart_templates.py`) — akurasi angka non-negotiable.
   - WAJIB review visual: AI Canva pernah nyelipin duit dolar AS. Cek tiap slide
     sebelum dipakai; tunjukkan ke user (checkpoint review visual baru).
   - Thumbnail juga via Canva (pola terbukti di video SBN, design `DAHOQKIpIsw`).
3. Compile lokal (moviepy/FFmpeg): audio + slide Canva + chart lokal + subtitle burn.
4. Upload YouTube setelah user approve hasil compile.
5. Update `state.json` di root project tiap langkah.

## FASE 3 — FINISHING
1. Video final di `output/`.
2. Draft metadata: 5 opsi judul (SEO, non-clickbait), deskripsi (timestamp + disclaimer), tags.
3. Catat hasil ke `memory/production_log.md`.

## GUARDRAIL
- API error / data market gak ketemu → **STOP, eskalasi ke user.** Jangan lanjut dengan data tebakan.
- Jaringan shell kadang mati (DNS gagal) — kalau web-search/edge-tts gagal, lapor, jangan hang.

## ESKALASI
Topik abu-abu secara regulasi (platform investasi bodong, skema ponzi, dsb) → **tanya user dulu** cara penyampaiannya biar channel gak kena demonetize.

## MAKER-CHECKER
JANGAN generate audio / render video sebelum user secara eksplisit approve ("Data aman, lanjut render").
