import feedparser
import json
import re
import random
from pathlib import Path

RSS_FEEDS = [
    "https://www.cnbcindonesia.com/rss",
    "https://feeds.kontan.co.id/rss/investasi",
    "https://investor.id/rss",
    "https://www.bisnis.com/rss",
    "https://keuangan.kontan.co.id/rss",
    "https://market.bisnis.com/rss",
    "https://ekonomi.kompas.com/rss",
    "https://www.liputan6.com/bisnis/rss",
    "https://finance.detik.com/rss",
    "https://www.cnbcindonesia.com/market/rss",
    "https://investasi.kontan.co.id/rss",
    "https://www.tempo.co/rss/bisnis",
]

BACKUP_TOPICS = [
    "Cara membaca laporan keuangan perusahaan",
    "Apa itu Price to Earnings Ratio (PER)?",
    "Cara menghitung nilai wajar saham dengan DCF",
    "Perbedaan saham growth dan value investing",
    "Cara analisis fundamental saham Indonesia",
    "Apa itu dividen dan bagaimana cara memilih saham dividen?",
    "Cara membaca laporan keuangan BEI untuk pemula",
    "Strategi dollar cost averaging di pasar saham",
    "Apa itu saham blue chip dan kenapa penting untuk investor?",
    "Cara diversifikasi portofolio saham yang benar",
    "Perbedaan reksa dana saham vs investasi saham langsung",
    "Cara membaca grafik candlestick untuk pemula",
    "Apa itu analisis teknikal dan bagaimana menggunakannya?",
    "Cara menghitung return on equity (ROE) sebuah perusahaan",
    "Pengertian market cap dan cara menggunakannya dalam investasi",
    "Strategi investasi jangka panjang untuk milenial Indonesia",
    "Apa itu obligasi dan perbedaannya dengan saham?",
    "Cara memilih broker saham yang terpercaya di Indonesia",
    "Apa itu IPO dan apakah layak dibeli oleh investor ritel?",
    "Cara mengelola risiko investasi saham di pasar volatil",
    "Apa itu ETF dan keuntungannya dibanding reksa dana biasa?",
    "Cara membaca neraca keuangan perusahaan tbk",
    "Strategi buy the dip: kapan tepat membeli saham turun?",
    "Apa itu earning per share (EPS) dan cara interpretasinya?",
    "Perbedaan trading dan investing saham untuk pemula",
]

USED_TOPICS_FILE = Path("output/used_topics.json")
FINANCE_KEYWORDS = ["saham", "investasi", "bursa", "IDX", "IHSG", "emiten", "profit", "dividen", "reksa", "keuangan", "portofolio", "obligasi", "pasar modal"]


# ─── Normalisasi & dedup fuzzy ────────────────────────────────────────────────
_STOPWORDS = {
    "yang", "dan", "dari", "untuk", "pada", "dengan", "atau", "ini", "itu",
    "juga", "akan", "adalah", "dalam", "bisa", "ada", "para", "oleh", "sebagai",
    "karena", "tidak", "jadi", "saat", "hingga", "usai", "soal", "simak", "cek",
    "kabar", "berita", "terbaru", "hari", "bakal", "kata", "buat", "kini", "per",
    "resmi", "mulai", "punya", "banyak", "lebih", "masih", "sudah", "capai", "kok",
}

_SIM_THRESHOLD = 0.5  # Jaccard >= ini → dianggap topik sama (beda sumber/wording).
#                       Sengaja agak longgar: headline berita pendek, tujuan utama
#                       mengurangi pengulangan cerita yang sama.


def _tokens(title: str) -> set:
    """Set kata signifikan dari judul (buang stopword & kata sangat pendek)."""
    words = re.findall(r"[a-z0-9]+", (title or "").lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _sig(title: str) -> str:
    """Signature stabil: token signifikan diurutkan (untuk disimpan sebagai used)."""
    return " ".join(sorted(_tokens(title)))


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _is_dup(tokens: set, existing: list) -> bool:
    """True bila `tokens` mirip (Jaccard >= threshold) dengan salah satu di existing."""
    return any(_jaccard(tokens, e) >= _SIM_THRESHOLD for e in existing)


def _load_used_sets() -> list:
    """Muat signature used → list token-set. Toleran file hilang/rusak/format lama."""
    if not USED_TOPICS_FILE.exists():
        return []
    try:
        data = json.loads(USED_TOPICS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [set(s.split()) for s in data.get("signatures", []) if s]


def _save_used_topic(title: str):
    raw = []
    if USED_TOPICS_FILE.exists():
        try:
            raw = json.loads(USED_TOPICS_FILE.read_text(encoding="utf-8")).get("signatures", [])
        except Exception:
            raw = []
    sig = _sig(title)
    if sig and sig not in raw:
        raw.append(sig)
    raw = raw[-500:]  # batasi pertumbuhan file
    USED_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USED_TOPICS_FILE.write_text(
        json.dumps({"signatures": raw}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_trending_topics(max_topics: int = 5) -> list[dict]:
    seen = _load_used_sets()          # dedup terhadap histori + antar-topik run ini
    topics = []

    feeds = RSS_FEEDS[:]
    random.shuffle(feeds)             # rotasi sumber agar tidak selalu feed yang sama

    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue
        for entry in feed.entries[:8]:
            title = (entry.get("title") or "").strip()
            toks = _tokens(title)
            if len(toks) < 2 or _is_dup(toks, seen):
                continue
            topics.append({
                "title": title,
                "summary": (entry.get("summary", "") or "")[:300],
                "source": feed.feed.get("title", feed_url),
                "published": entry.get("published", ""),
            })
            seen.append(toks)

    if len(topics) < max_topics:
        backups = BACKUP_TOPICS[:]
        random.shuffle(backups)
        for t in backups:
            toks = _tokens(t)
            if _is_dup(toks, seen):
                continue
            topics.append({"title": t, "summary": "", "source": "Evergreen", "published": ""})
            seen.append(toks)
            if len(topics) >= max_topics * 3:
                break

    if not topics:
        # semua sudah dipakai — reset histori dan mulai ulang
        USED_TOPICS_FILE.write_text(json.dumps({"signatures": []}, ensure_ascii=False), encoding="utf-8")
        return get_trending_topics(max_topics)

    random.shuffle(topics)            # acak urutan agar pick_best tak bias urutan feed
    return topics[:max_topics * 3]    # kirim lebih banyak agar pick_best punya pilihan


def _score(topic: dict) -> int:
    title = topic["title"].lower()
    return sum(1 for kw in FINANCE_KEYWORDS if kw.lower() in title)


def pick_best_topic(topics: list[dict]) -> dict:
    """Pilih topik relevan-finansial, tapi acak-terbobot di antara tier teratas
    supaya tidak selalu memilih topik yang sama (mengurangi pengulangan)."""
    if not topics:
        raise ValueError("Tidak ada topik untuk dipilih")

    scored = [(_score(t), t) for t in topics]
    max_score = max(s for s, _ in scored)
    tier = [t for s, t in scored if s >= max(1, max_score - 1)]
    if not tier:                      # semua skor 0 → pakai semua kandidat
        tier = [t for _, t in scored]

    weights = [_score(t) + 1 for t in tier]
    chosen = random.choices(tier, weights=weights, k=1)[0]
    _save_used_topic(chosen["title"])
    return chosen
