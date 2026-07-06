"""Fase 0 bersih-bersih: unlist video off-niche + duplikat lama.
Set privacyStatus -> unlisted (reversibel, bukan hapus).
Skip video yang sudah unlisted/private atau tak ditemukan.
"""
from core.youtube_uploader import get_youtube_client

# Dari growth plan (project-moovon-growth-plan)
OFFNICHE = [
    "G4C76HH5mhw", "tx8NK4Y-Y7c", "2hqcCCDYPYg", "6i0jDdPgTu0", "zOqXxbeFPI4",
    "4Vjdh4WYpVY", "FtEIWLbtfNE", "NujG4TlESgM", "2enNCHm89cE", "R4DUTurrL_A",
    "EB90ZxBiST8", "bFNp0NHFh2Y", "iAWIrbnKfZg", "OI_lrjMsnPo", "_Ct_b467QUM",
    "7v6ccNWZy28", "PMm4XMu5Kss",
]
DUPLIKAT = {
    "c8aZ9_VW9ps": "BBRI versi lama",
    "FId3xkUS0CY": "BMRI versi lama",
    "scEbyVKy3CA": "BBCA foto (versi lama)",
}
KEEP = {"LLg7NYh0lXE", "ymRoSeUyPO8", "4cB59WQqSQo"}  # jangan disentuh

TARGETS = OFFNICHE + list(DUPLIKAT.keys())


def main():
    yt = get_youtube_client()
    unlisted, skipped, missing = [], [], []

    # Ambil status + judul semua target (batch 50)
    info = {}
    for i in range(0, len(TARGETS), 50):
        batch = TARGETS[i:i + 50]
        r = yt.videos().list(part="snippet,status", id=",".join(batch)).execute()
        for v in r["items"]:
            info[v["id"]] = v

    for vid in TARGETS:
        if vid in KEEP:
            continue
        v = info.get(vid)
        if not v:
            missing.append(vid)
            print(f"[MISSING] {vid} — tak ditemukan (mungkin sudah dihapus)")
            continue
        title = v["snippet"]["title"][:55]
        cur = v["status"]["privacyStatus"]
        if cur != "public":
            skipped.append(vid)
            print(f"[SKIP {cur:<8}] {vid}  {title}")
            continue
        # Bangun body status: ubah privacy, pertahankan field lain
        status = v["status"]
        body = {
            "id": vid,
            "status": {
                "privacyStatus": "unlisted",
                "selfDeclaredMadeForKids": status.get("selfDeclaredMadeForKids", False),
                "embeddable": status.get("embeddable", True),
                "publicStatsViewable": status.get("publicStatsViewable", True),
                "license": status.get("license", "youtube"),
            },
        }
        yt.videos().update(part="status", body=body).execute()
        unlisted.append(vid)
        tag = DUPLIKAT.get(vid, "off-niche")
        print(f"[UNLIST -> ] {vid}  ({tag})  {title}")

    print("\n" + "=" * 50)
    print(f"Di-unlist   : {len(unlisted)}")
    print(f"Dilewati    : {len(skipped)} (sudah unlisted/private)")
    print(f"Tak ada     : {len(missing)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
