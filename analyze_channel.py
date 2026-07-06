"""Audit cepat channel YouTube Moovon: statistik channel + per-video.
Pakai token OAuth yang sudah ada (scope youtube.readonly cukup).
"""
import sys
from datetime import datetime, timezone
from core.youtube_uploader import get_youtube_client


def main():
    yt = get_youtube_client()

    # 1. Channel milik sendiri
    ch = yt.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()
    if not ch.get("items"):
        print("Tidak ada channel untuk akun ini.")
        return
    c = ch["items"][0]
    st = c["statistics"]
    title = c["snippet"]["title"]
    subs = int(st.get("subscriberCount", 0))
    views = int(st.get("viewCount", 0))
    vids = int(st.get("videoCount", 0))
    uploads_pl = c["contentDetails"]["relatedPlaylists"]["uploads"]

    print("=" * 60)
    print(f"CHANNEL: {title}")
    print(f"  Subscriber : {subs}")
    print(f"  Total view : {views}")
    print(f"  Total video: {vids}")
    print("=" * 60)

    # 2. Semua video dari playlist uploads
    video_ids = []
    page = None
    while True:
        r = yt.playlistItems().list(
            part="contentDetails", playlistId=uploads_pl, maxResults=50, pageToken=page
        ).execute()
        for it in r["items"]:
            video_ids.append(it["contentDetails"]["videoId"])
        page = r.get("nextPageToken")
        if not page:
            break

    # 3. Ambil statistik + detail per video (batch 50)
    rows = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        r = yt.videos().list(
            part="snippet,statistics,contentDetails,status", id=",".join(batch)
        ).execute()
        for v in r["items"]:
            s = v["statistics"]
            snip = v["snippet"]
            dur = v["contentDetails"]["duration"]
            is_short = "S" in dur and "M" not in dur and "H" not in dur  # kasar: durasi < 1 menit
            rows.append({
                "id": v["id"],
                "title": snip["title"],
                "published": snip["publishedAt"],
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "privacy": v["status"]["privacyStatus"],
                "dur": dur,
                "short": is_short,
            })

    rows.sort(key=lambda x: x["published"], reverse=True)

    print(f"\n{'TGL':<11} {'VIEW':>5} {'LIKE':>4} {'KOM':>3} {'PRIV':<8} {'TIPE':<6} JUDUL")
    print("-" * 100)
    for r in rows:
        tgl = r["published"][:10]
        tipe = "SHORT" if r["short"] else "LONG"
        judul = r["title"][:48]
        print(f"{tgl:<11} {r['views']:>5} {r['likes']:>4} {r['comments']:>3} "
              f"{r['privacy']:<8} {tipe:<6} {judul}")

    # 4. Ringkasan agregat
    longs = [r for r in rows if not r["short"]]
    shorts = [r for r in rows if r["short"]]
    pub = [r for r in rows if r["privacy"] == "public"]

    def agg(name, lst):
        if not lst:
            print(f"  {name}: 0 video")
            return
        tv = sum(r["views"] for r in lst)
        print(f"  {name}: {len(lst)} video | total {tv} view | rata2 {tv/len(lst):.1f} view/video")

    print("\n" + "=" * 60)
    print("RINGKASAN")
    agg("Video panjang", longs)
    agg("Shorts", shorts)
    agg("Publik (semua)", pub)
    print("=" * 60)


if __name__ == "__main__":
    main()
