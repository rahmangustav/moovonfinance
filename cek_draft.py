#!/usr/bin/env python3
"""Pemeriksaan pra-render untuk draft naskah Moovon — gagalkan SEKARANG, bukan nanti.

KENAPA ADA: render satu video makan ~10 menit encode plus TTS, dan sebagian
kegagalan baru ketahuan di ujung — saat pemilik sudah menunggu. Dua contoh nyata
yang sudah pernah terjadi di repo ini:
  - Judul 102 karakter → upload ditolak YouTube (`invalidTitle`) SETELAH render
    dan unggah selesai.
  - Persentase donut tidak berjumlah 100 → angka di tengah donut tampil "99%"
    dan potongan ternormalisasi diam-diam.

Skrip ini membaca draft lewat parser pipeline yang SUNGGUHAN (`produce.parse_draft`
+ `visuals.parse_sections` + `visuals._match_charts_to_sections`), bukan parser
tiruan — jadi kalau lolos di sini, ia lolos di render.

TIDAK merender, TIDAK memanggil TTS, TIDAK menyentuh jaringan. Aman dijalankan
kapan saja, termasuk saat draft masih menunggu persetujuan pemilik.

Pakai:
    .venv/bin/python cek_draft.py assets/draft_script_moovon.md
    .venv/bin/python cek_draft.py            # default: assets/draft_script_moovon.md

Keluar dengan kode 1 kalau ada MASALAH (bukan sekadar peringatan), jadi bisa
dipakai sebagai gerbang sebelum render.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "core"))

from produce import parse_draft  # noqa: E402
import visuals  # noqa: E402
from moovon_theme import verdict  # noqa: E402

BATAS_JUDUL = 100          # batas keras YouTube
BATAS_DESKRIPSI = 4900     # ambang aman (batas asli 5000)

# Kata Inggris yang bikin voice-over Indonesia terdengar kaku/robotik.
# Aturan gaya kanal: narasi TTS Bahasa Indonesia lisan, tanpa istilah Inggris
# dan tanpa tanda kurung penjelas.
KATA_INGGRIS = (
    "financial advice", "advice", "disclaimer", "earnings", "revenue",
    "net income", "guidance", "outlook", "valuation", "buyback",
)

masalah, peringatan = [], []


def cek(nama: str, ok: bool, pesan_gagal: str, keras: bool = True) -> None:
    if ok:
        print(f"  ✅ {nama}")
        return
    print(f"  {'❌' if keras else '⚠️ '} {nama} — {pesan_gagal}")
    (masalah if keras else peringatan).append(f"{nama}: {pesan_gagal}")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/draft_script_moovon.md")
    if not path.exists():
        sys.exit(f"Draft tidak ada: {path}")

    print(f"PEMERIKSAAN PRA-RENDER — {path.name}\n")
    d = parse_draft(path)

    # ── Judul & metadata ──────────────────────────────────────────────
    print("Judul & metadata")
    judul = (d.get("title") or "").strip()
    cek(f"judul terisi ({len(judul)} karakter)", bool(judul), "judul kosong")
    cek(f"judul <= {BATAS_JUDUL} karakter", len(judul) <= BATAS_JUDUL,
        f"{len(judul)} karakter — YouTube menolak dengan invalidTitle")
    cek("topic/kata kunci terisi", bool((d.get("topic") or "").strip()),
        "kosong — SEO deskripsi jadi lemah", keras=False)
    cek("thumbnail_text terisi", bool((d.get("thumbnail_text") or "").strip()),
        "kosong — sampul jatuh ke judul panjang", keras=False)

    # ── Struktur naskah ───────────────────────────────────────────────
    print("\nStruktur naskah")
    script = d.get("script") or ""
    secs = visuals.parse_sections(script)
    cek(f"section ter-parse ({len(secs)})", len(secs) >= 3,
        f"cuma {len(secs)} — penanda [LABEL] mungkin salah tulis")
    kosong = [s.get("label", "?") for s in secs if not str(s.get("content", "")).strip()]
    cek("tidak ada section kosong", not kosong, f"kosong: {', '.join(kosong)}")
    ada_cta = any("CTA" in str(s.get("label", "")).upper() or
                  "PENUTUP" in str(s.get("label", "")).upper() for s in secs)
    cek("ada section penutup/CTA", ada_cta, "tak ada — slide penutup wajib")

    # ── Aturan konten wajib ───────────────────────────────────────────
    print("\nAturan konten")
    cek("disclaimer edukasi di 30 detik pertama",
        "edukasi" in script[:1200].lower(),
        "tidak ditemukan di pembuka — aturan kanal mewajibkan")
    kurung = re.findall(r"\([^)]{3,}\)", script)
    # Pesan dirakit TERPISAH: argumen f-string dievaluasi duluan, jadi menulis
    # kurung[0] langsung di pemanggilan akan meledak saat daftarnya kosong —
    # persis yang terjadi saat alat ini pertama dijalankan.
    pesan_kurung = (f"{len(kurung)} ditemukan, mis. {kurung[0][:40]!r} — bikin TTS kaku"
                    if kurung else "")
    cek("tanpa tanda kurung penjelas di narasi", not kurung, pesan_kurung, keras=False)
    eng = sorted({m.lower() for m in re.findall(
        r"\b(" + "|".join(KATA_INGGRIS) + r")\b", script, re.I)})
    cek("tanpa kata Inggris di narasi", not eng,
        f"ditemukan: {', '.join(eng)}", keras=False)

    # ── Chart ─────────────────────────────────────────────────────────
    print("\nChart")
    charts = d.get("charts") or []
    print(f"  ({len(charts)} chart)")
    for i, c in enumerate(charts, 1):
        tipe = c.get("type", "?")
        cek(f"chart {i} ({tipe}) punya judul", bool(str(c.get("judul", "")).strip()),
            "judul kosong", keras=False)
        if tipe == "donut":
            # Kunci yang BENAR adalah `persentase` — bukan values/data. Renderer
            # menulis angka tengah donut dari sum(persentase) yang dibulatkan,
            # jadi jumlah 99,9 aman (tampil 100%) tapi 99,0 akan tampil "99%".
            pers = c.get("persentase") or []
            total = sum(float(x) for x in pers) if pers else 0.0
            cek(f"chart {i} donut berjumlah ~100 (kini {total:g})",
                abs(round(total) - 100) < 1,
                f"jumlah {total:g} — angka tengah donut akan tampil salah")
            cek(f"chart {i} label vs nilai sama banyak",
                len(c.get("labels") or []) == len(pers),
                f"{len(c.get('labels') or [])} label vs {len(pers)} nilai")

    if charts and secs:
        cocok = visuals._match_charts_to_sections(secs, charts)
        tersisip = sum(len(x) for x in cocok)
        cek(f"semua chart dapat tempat ({tersisip}/{len(charts)})",
            tersisip == len(charts),
            f"{len(charts) - tersisip} chart tak tersisip — cek field 'section'")

    # ── Blok opsional ─────────────────────────────────────────────────
    print("\nBlok opsional")
    val = d.get("valuation")
    if val:
        harga, wajar = val.get("harga"), val.get("nilai_wajar")
        cek("valuation punya harga & nilai_wajar", bool(harga and wajar), "salah satu kosong")
        if harga and wajar:
            label, _, mos = verdict(float(harga), float(wajar))
            print(f"      margin of safety {mos * 100:+.1f}% → verdict: {label} "
                  f"(sama seperti yang akan dirender di gauge)")
            print("      pastikan nilai_wajar dari riset, bukan karangan")
    else:
        print("  (tanpa blok VALUATION — wajar untuk video edukasi)")
    snap = d.get("snapshot")
    if snap:
        m = snap.get("metrics") or []
        cek(f"snapshot punya metrics ({len(m)})", bool(m), "kosong")
        salah = [x for x in m if not isinstance(x, (list, tuple)) or len(x) < 2]
        cek("format metrics benar", not salah, f"{len(salah)} baris tak berbentuk [label, nilai, warna]")
    else:
        print("  (tanpa blok SNAPSHOT)")

    # ── Kesimpulan ────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    if masalah:
        print(f"❌ {len(masalah)} MASALAH — perbaiki sebelum render:")
        for m in masalah:
            print(f"   - {m}")
    if peringatan:
        print(f"⚠️  {len(peringatan)} peringatan (tidak memblokir):")
        for p in peringatan:
            print(f"   - {p}")
    if not masalah and not peringatan:
        print("✅ Bersih — siap dirender begitu pemilik menyetujui.")
    elif not masalah:
        print("✅ Tidak ada masalah pemblokir — siap dirender.")
    sys.exit(1 if masalah else 0)


if __name__ == "__main__":
    main()
