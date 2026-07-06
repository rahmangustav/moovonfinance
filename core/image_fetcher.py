import os
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path(__file__).parent.parent / "output" / ".img_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")

_SESSION = requests.Session()
_SESSION.headers["User-Agent"] = "MoovonFinance/1.0"


def fetch_image(query: str) -> str | None:
    """Return local path to a downloaded image, or None if unavailable."""
    cache_key = hashlib.md5(query.lower().encode()).hexdigest()[:14]
    cached = CACHE_DIR / f"{cache_key}.jpg"
    if cached.exists():
        return str(cached)

    url = _from_pexels(query) if PEXELS_KEY else _from_ddgs(query)
    if not url:
        url = _from_ddgs(query)  # fallback even if pexels failed

    if url:
        try:
            r = _SESSION.get(url, timeout=12)
            ct = r.headers.get("content-type", "")
            if r.status_code == 200 and "image" in ct:
                cached.write_bytes(r.content)
                return str(cached)
        except Exception:
            pass

    return None


def _from_pexels(query: str) -> str | None:
    try:
        r = _SESSION.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=8,
        )
        photos = r.json().get("photos", [])
        if photos:
            return photos[0]["src"]["large2x"]
    except Exception:
        pass
    return None


_BLOCKED_URL_KEYWORDS = [
    "webinar", "conference", "seminar", "workshop", "summit", "congress",
    "expo", "forum", "event", "meeting", "poster", "banner", "flyer",
    "infographic", "infografi", "outlook", "report", "presentation",
    "slideshow", "slide", "ppt", "chart-",
    "istock", "shutterstock", "gettyimages", "dreamstime",
    "depositphotos", "alamy", "123rf", "bigstockphoto",
    "vecteezy", "freepik", "adobestock",
]


def _from_ddgs(query: str) -> str | None:
    try:
        from ddgs import DDGS
        results = list(DDGS().images(query, max_results=20))
        for res in results:
            url = res.get("image", "")
            w   = int(res.get("width", 0) or 0)
            h   = int(res.get("height", 0) or 0)
            url_lower   = url.lower()
            has_img_ext = any(ext in url_lower for ext in (".jpg", ".jpeg", ".png", ".webp"))
            is_blocked  = any(kw in url_lower for kw in _BLOCKED_URL_KEYWORDS)
            if url.startswith("http") and has_img_ext and w >= 600 and h >= 380 and not is_blocked:
                return url
    except Exception:
        pass
    return None
