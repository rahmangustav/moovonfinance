"""Backfill: set defaultAudioLanguage + defaultLanguage = 'id' untuk semua video
channel yang labelnya salah/kosong (YouTube kadang salah menebak audio = Inggris).

Butuh scope tulis (youtube.force-ssl). Kalau token lama cuma readonly, hapus dulu
config/token.json lalu jalankan sekali untuk login ulang:

    rm config/token.json
    .venv/bin/python backfill_audio_lang.py

Aman diulang (idempoten): video yang sudah 'id' dilewati.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "core"))
from youtube_uploader import get_youtube_client

TARGET = "id"


def main():
    yt = get_youtube_client()

    # Ambil semua video dari playlist uploads channel sendiri
    ch = yt.channels().list(part="contentDetails", mine=True).execute()
    pl = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    vids, tok = [], None
    while True:
        r = yt.playlistItems().list(
            part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok
        ).execute()
        vids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break

    fixed = skipped = failed = 0
    for i in range(0, len(vids), 50):
        chunk = vids[i:i + 50]
        r = yt.videos().list(part="snippet", id=",".join(chunk)).execute()
        for v in r["items"]:
            sn = v["snippet"]
            if sn.get("defaultAudioLanguage") == TARGET:
                skipped += 1
                continue
            body = {
                "id": v["id"],
                "snippet": {
                    "title": sn["title"],
                    "categoryId": sn.get("categoryId", "25"),
                    "description": sn.get("description", ""),
                    "tags": sn.get("tags", []),
                    "defaultLanguage": TARGET,
                    "defaultAudioLanguage": TARGET,
                },
            }
            try:
                yt.videos().update(part="snippet", body=body).execute()
                print(f"  fixed  {v['id']} | {sn['title'][:55]}")
                fixed += 1
            except Exception as e:
                print(f"  FAILED {v['id']} | {e}")
                failed += 1

    print(f"\nTotal {len(vids)} video | diperbaiki {fixed} | sudah benar {skipped} | gagal {failed}")


if __name__ == "__main__":
    main()
