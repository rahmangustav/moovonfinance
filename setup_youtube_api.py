"""
Jalankan script ini setelah kamu download client_secrets.json dari Google Cloud Console.
Script ini akan membuka browser untuk login dan menyimpan token otomatis.
"""
from modules.youtube_uploader import get_youtube_client

if __name__ == "__main__":
    print("Menghubungkan ke YouTube API...")
    youtube = get_youtube_client()

    response = youtube.channels().list(part="snippet", mine=True).execute()
    channel = response["items"][0]["snippet"]

    print(f"\nBerhasil terhubung!")
    print(f"Channel: {channel['title']}")
    print(f"Token tersimpan di config/token.json")
