#!/usr/bin/env python3
"""
Moovon Finance — Pipeline otomatis YouTube
Jalankan: python main.py
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from modules.research import get_trending_topics, pick_best_topic
from modules.script_writer import write_script
from modules.tts import generate_audio
from modules.video_maker import create_video
from modules.thumbnail import create_thumbnail
from modules.youtube_uploader import upload_video

OUTPUT_DIR = Path("output")


def run():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print("\n🔍 [1/5] Riset topik...")
    topics = get_trending_topics(max_topics=10)
    topic = pick_best_topic(topics)
    print(f"   Topik terpilih: {topic['title']}")

    print("\n✍️  [2/5] Menulis skrip dengan AI...")
    script_data = write_script(topic)
    script_path = run_dir / "script.txt"
    script_path.write_text(script_data["raw"], encoding="utf-8")
    print(f"   Judul: {script_data['title']}")

    print("\n🎙️  [3/5] Membuat voiceover...")
    audio_path = str(run_dir / "audio.mp3")
    generate_audio(script_data["script"], audio_path)

    print("\n🎬 [4/5] Membuat video...")
    video_path = str(run_dir / "video.mp4")
    vk = script_data.get("visual_keywords", {})
    charts = script_data.get("charts", [])
    print(f"   Keywords visual: {vk}")
    print(f"   Chart data: {len(charts)} grafik")
    create_video(
        script_data["title"],
        script_data["script"],
        audio_path,
        video_path,
        topic_keywords=topic.get("title", ""),
        visual_keywords=vk,
        charts=charts,
    )

    print("\n🖼️  [4b] Membuat thumbnail...")
    thumb_path = str(run_dir / "thumbnail.jpg")
    create_thumbnail(script_data["title"], thumb_path)

    print("\n🚀 [5/5] Upload ke YouTube...")
    video_id = upload_video(
        video_path=video_path,
        title=script_data["title"],
        description=script_data["description"],
        tags=script_data["tags"],
        thumbnail_path=thumb_path,
    )

    print(f"\n✅ Selesai! Video live di: https://youtube.com/watch?v={video_id}")
    print(f"   File tersimpan di: {run_dir}")


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY belum diset di file .env")
        sys.exit(1)
    run()
