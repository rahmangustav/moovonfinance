import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def write_script(topic: dict) -> dict:
    prompt = f"""Kamu adalah penulis skrip untuk channel YouTube finance Indonesia bernama "Moovon Finance".
Buat skrip video berdurasi 5-7 menit tentang topik berikut:

Topik: {topic['title']}
Konteks tambahan: {topic.get('summary', '')}

Format skrip HARUS persis seperti ini:

JUDUL_VIDEO: [judul menarik, max 60 karakter, mengandung kata kunci]
DESKRIPSI: [deskripsi YouTube 150-200 kata, mengandung kata kunci SEO]
TAGS: [10-15 tag dipisah koma]
KEYWORDS_VISUAL: [keyword foto BAHASA INGGRIS, spesifik, untuk setiap section. Format: HOOK|keyword;INTRO|keyword;ISI UTAMA|keyword;KESIMPULAN|keyword;CTA|keyword. Contoh untuk topik saham BBCA: HOOK|Bank Central Asia stock market Indonesia;INTRO|Indonesian parliament meeting official;ISI UTAMA|bank finance growth chart Indonesia;KESIMPULAN|investment decision Indonesia economy;CTA|stock market investment Indonesia coins]
CHARTS: [OPSIONAL. Array JSON berisi 1-3 grafik data untuk memperkuat penjelasan, HANYA jika kamu punya ANGKA NYATA yang relevan. Kosongkan dengan [] jika tidak ada data pasti — JANGAN mengarang angka. Setiap objek WAJIB punya "type", "section" (nama section tempat grafik muncul, mis. "ISI UTAMA"), "judul", "sumber", dan field data sesuai tipe:
  - {{"type":"bar","section":"ISI UTAMA","judul":"...","sumber":"...","kategori":["A","B"],"nilai":[10,-5],"horizontal":false}}
  - {{"type":"line","section":"ISI UTAMA","judul":"...","sumber":"...","x":["2021","2022","2023"],"y_dict":{{"IHSG":[6,6.5,7]}}}}
  - {{"type":"donut","section":"ISI UTAMA","judul":"...","sumber":"...","labels":["Saham","Emas"],"persentase":[60,40]}}
  - {{"type":"table","section":"ISI UTAMA","judul":"...","sumber":"...","headers":["Emiten","YTD"],"rows":[["BBCA","+18%"],["TLKM","-4%"]]}}
  - {{"type":"timeline","section":"ISI UTAMA","judul":"...","sumber":"...","events":["Krisis 98","Pandemi"],"dates":["1998","2020"]}}
Tulis CHARTS dalam SATU baris JSON valid.]

SKRIP:
[HOOK - 30 detik]
(tulis narasi hook yang langsung menarik perhatian)

[INTRO - 30 detik]
(perkenalan singkat Moovon Finance dan preview isi video)

[ISI UTAMA - 4-5 menit]
(penjelasan mendalam dengan contoh nyata, data, dan analogi sederhana)
(bagi menjadi 3-4 poin utama dengan sub-judul menggunakan format ### Sub-judul)

[KESIMPULAN - 30 detik]
(rangkuman poin penting)

[CTA - 30 detik]
(ajak subscribe, like, comment, dan tonton video selanjutnya)

Gunakan bahasa Indonesia yang santai tapi berbobot. Sertakan data nyata jika relevan."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    raw = response.choices[0].message.content
    return parse_script(raw)


def parse_script(raw: str) -> dict:
    result = {
        "raw": raw,
        "title": "",
        "description": "",
        "tags": [],
        "script": "",
        "visual_keywords": {},
        "charts": [],
    }

    for line in raw.split("\n"):
        if line.startswith("JUDUL_VIDEO:"):
            result["title"] = line.replace("JUDUL_VIDEO:", "").strip()
        elif line.startswith("DESKRIPSI:"):
            result["description"] = line.replace("DESKRIPSI:", "").strip()
        elif line.startswith("TAGS:"):
            tags_raw = line.replace("TAGS:", "").strip()
            result["tags"] = [t.strip() for t in tags_raw.split(",")]
        elif line.startswith("KEYWORDS_VISUAL:"):
            raw_kw = line.replace("KEYWORDS_VISUAL:", "").strip()
            for entry in raw_kw.split(";"):
                if "|" in entry:
                    section, kw = entry.split("|", 1)
                    result["visual_keywords"][section.strip().upper()] = kw.strip()

    result["charts"] = _parse_charts(raw)

    if "SKRIP:" in raw:
        result["script"] = raw.split("SKRIP:")[1].strip()

    if not result["title"]:
        result["title"] = "Video Moovon Finance"

    return result


def _parse_charts(raw: str) -> list:
    """Ekstrak blok 'CHARTS:' (array JSON) hingga sebelum 'SKRIP:'. Toleran:
    kalau tidak ada, kosong, atau JSON tidak valid → kembalikan []."""
    m = re.search(r"CHARTS:\s*(\[.*?\])\s*(?:\n[A-Z_]+:|SKRIP:|$)", raw, re.DOTALL)
    if not m:
        return []
    try:
        charts = json.loads(m.group(1))
    except (json.JSONDecodeError, ValueError):
        return []
    if not isinstance(charts, list):
        return []
    # Hanya simpan objek yang minimal punya 'type' & 'judul'
    return [c for c in charts if isinstance(c, dict) and c.get("type") and c.get("judul")]
