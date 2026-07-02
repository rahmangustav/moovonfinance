import asyncio
import re
import edge_tts

VOICE = "id-ID-GadisNeural"
RATE = "+8%"
PITCH = "+0Hz"

# Batas pemenggalan baris subtitle
_MAX_CHARS = 68
_MAX_SECS = 6.0


def clean_script(script: str) -> str:
    cleaned = re.sub(r"\[.*?\]", "", script)
    cleaned = re.sub(r"#{1,3}\s*", "", cleaned)
    cleaned = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _boundaries_to_segments(words: list) -> list[dict]:
    """Ubah word-boundary edge-tts → segmen subtitle. words: list (start, end, text)
    dalam detik. Dipenggal per kalimat (tanda . ! ?), atau saat baris terlalu
    panjang / terlalu lama."""
    segments = []
    buf_text = ""
    buf_start = None
    buf_end = 0.0
    for start, end, w in words:
        if buf_start is None:
            buf_start = start
        buf_text = f"{buf_text} {w}".strip() if buf_text else w
        buf_end = end
        too_long = len(buf_text) >= _MAX_CHARS
        too_slow = (buf_end - buf_start) >= _MAX_SECS
        sentence_end = buf_text.endswith((".", "!", "?"))
        if sentence_end or too_long or too_slow:
            segments.append({"start": buf_start, "end": buf_end, "text": buf_text})
            buf_text, buf_start = "", None
    if buf_text:
        segments.append({"start": buf_start, "end": buf_end, "text": buf_text})
    return segments


async def _synthesize(text: str, audio_path: str) -> list[dict]:
    """Sintesis audio + kumpulkan word boundaries → return segmen subtitle akurat."""
    # boundary="WordBoundary" WAJIB — default edge-tts adalah SentenceBoundary
    # yang TIDAK memberi timing per-kata (bikin subtitle kosong).
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")
    words = []
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7          # 100ns → detik
                end = (chunk["offset"] + chunk["duration"]) / 1e7
                words.append((start, end, chunk["text"]))
    return _boundaries_to_segments(words)


def generate_audio(script: str, output_path: str) -> list[dict]:
    """Buat voiceover DAN SRT akurat (dari word-boundary TTS, bukan transkripsi).

    Menulis audio ke output_path dan subtitle ke <output_path tanpa ekstensi>.srt.
    Mengembalikan daftar segmen subtitle.
    """
    from pathlib import Path
    from modules.subtitle import to_srt

    cleaned = clean_script(script)
    # Batas waktu keras: kalau stream edge-tts macet (connected tapi berhenti
    # kirim data), batalkan agar loop retry pemanggil bisa mengulang.
    async def _run():
        return await asyncio.wait_for(_synthesize(cleaned, output_path), timeout=300)
    segments = asyncio.run(_run())

    srt_path = str(Path(output_path).with_suffix(".srt"))
    to_srt(segments, srt_path)

    print(f"Audio saved: {output_path}")
    print(f"Subtitle (akurat dari TTS): {srt_path} — {len(segments)} segmen")
    return segments
