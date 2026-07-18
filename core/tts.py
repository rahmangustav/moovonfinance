import asyncio
import base64
import os
import re
import edge_tts

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

VOICE = "id-ID-GadisNeural"
RATE = "-2%"   # varian B (dipilih user 12 Jul 2026): sedikit lebih santai dari +2%
PITCH = "+0Hz"

# ─── Mastering (varian B, 12 Jul 2026) ────────────────────────────────────────
# Rantai: highpass 70Hz → kompresi ringan → EQ presence 3,2kHz → loudnorm
# linear 2-tahap ke -14 LUFS (standar YouTube; audio lama cuma -19,9) →
# kompensasi +0,85dB karena encoder mp3 (libmp3lame build imageio) terukur
# "memakan" ~0,5dB. Hasil terverifikasi: -14,0 LUFS / -1,0 dBTP di file mp3.
MASTER_PRE = ("highpass=f=70,"
              "acompressor=threshold=-20dB:ratio=2.5:attack=12:release=180:makeup=3dB,"
              "equalizer=f=3200:t=q:w=1:g=1.5")
MASTER_I, MASTER_TP, MASTER_LRA = -14.0, -1.0, 11.0
MASTER_MP3_COMP = "0.85dB"

# ─── ElevenLabs (voice natural) — dipakai bila ELEVENLABS_API_KEY tersedia ─────
ELEVEN_KEY   = os.getenv("ELEVENLABS_API_KEY", "")
# Default: "Sarah" (voice premade hangat). Ganti via .env ELEVENLABS_VOICE_ID.
ELEVEN_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
ELEVEN_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
_ELEVEN_MAX  = 2200   # batas aman karakter per request (aman utk semua tier)

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


# ─── Backend ElevenLabs ───────────────────────────────────────────────────────
def _split_for_tts(text: str, limit: int = _ELEVEN_MAX) -> list[str]:
    """Pecah teks jadi potongan <= limit karakter di batas kalimat."""
    sents = re.split(r"(?<=[.!?])\s+", text)
    chunks, cur = [], ""
    for s in sents:
        if cur and len(cur) + len(s) + 1 > limit:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def _eleven_chunk(text: str):
    """Sintesis 1 potongan via ElevenLabs with-timestamps.
    Return (audio_bytes, characters, char_start_s, char_end_s)."""
    import requests
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE}"
           f"/with-timestamps?output_format=mp3_44100_128")
    r = requests.post(
        url,
        headers={"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": ELEVEN_MODEL,
            "voice_settings": {
                "stability": 0.45, "similarity_boost": 0.75,
                "style": 0.15, "use_speaker_boost": True,
            },
        },
        timeout=180,
    )
    r.raise_for_status()
    d = r.json()
    audio = base64.b64decode(d["audio_base64"])
    al = d.get("alignment") or d.get("normalized_alignment") or {}
    return (audio, al.get("characters", []),
            al.get("character_start_times_seconds", []),
            al.get("character_end_times_seconds", []))


def _chars_to_words(chars, starts, ends, offset=0.0):
    """Gabung karakter beralignment → daftar (start, end, word) dalam detik."""
    words, cw, ws, we = [], "", None, 0.0
    for ch, st, en in zip(chars, starts, ends):
        if ch.isspace():
            if cw:
                words.append((ws + offset, we + offset, cw)); cw, ws = "", None
        else:
            if ws is None:
                ws = st
            cw += ch; we = en
    if cw:
        words.append((ws + offset, we + offset, cw))
    return words


def _generate_audio_eleven(script: str, output_path: str) -> list[dict]:
    from pathlib import Path
    from moviepy import AudioFileClip, concatenate_audioclips
    from subtitle import to_srt

    cleaned = clean_script(script)
    chunks  = _split_for_tts(cleaned)
    out_dir = Path(output_path).parent
    tmp, words, offset = [], [], 0.0
    for i, ch in enumerate(chunks):
        audio, chars, st, en = _eleven_chunk(ch)
        p = out_dir / f"_eleven_{i}.mp3"
        p.write_bytes(audio); tmp.append(p)
        words += _chars_to_words(chars, st, en, offset)
        with AudioFileClip(str(p)) as a:
            offset += a.duration
        print(f"   🎙️  ElevenLabs potongan {i + 1}/{len(chunks)} ok", flush=True)

    clips = [AudioFileClip(str(p)) for p in tmp]
    final = concatenate_audioclips(clips)
    final.write_audiofile(output_path, logger=None)
    for c in clips:
        c.close()
    final.close()
    for p in tmp:
        p.unlink(missing_ok=True)
    master_audio(output_path)

    segments = _boundaries_to_segments(words)
    to_srt(segments, str(Path(output_path).with_suffix(".srt")))
    print(f"Audio (ElevenLabs {ELEVEN_VOICE}) saved: {output_path} — {len(segments)} segmen")
    return segments


def master_audio(audio_path: str) -> None:
    """Mastering in-place (varian B): loudness standar YouTube -14 LUFS.

    Time-invariant (gain/EQ saja, loudnorm mode linear) sehingga timing
    word-boundary/SRT TIDAK bergeser. Gagal → audio asli dibiarkan (aman).
    """
    import json as _json
    import subprocess
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    base = f"loudnorm=I={MASTER_I}:TP={MASTER_TP}:LRA={MASTER_LRA}"
    # Tahap 1: ukur
    r = subprocess.run(
        [ffmpeg, "-i", audio_path, "-af", f"{MASTER_PRE},{base}:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
    if not m:
        print("   ⚠️  Mastering dilewati: pengukuran loudnorm gagal.")
        return
    meas = _json.loads(m.group(0))
    # Tahap 2: terapkan linear + kompensasi encoder mp3
    ln = (f"{base}:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
          f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
          f":offset={meas['target_offset']}:linear=true")
    tmp = f"{audio_path}.master.mp3"
    r = subprocess.run(
        [ffmpeg, "-y", "-i", audio_path,
         "-af", f"{MASTER_PRE},{ln},volume={MASTER_MP3_COMP}",
         "-ar", "44100", "-b:a", "128k", tmp], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        print(f"   ⚠️  Mastering dilewati: {r.stderr[-200:]}")
        return
    os.replace(tmp, audio_path)
    print(f"   🎚️  Mastering ok: -14 LUFS (varian B) → {audio_path}")


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
    from subtitle import to_srt

    # Prioritas: ElevenLabs (voice natural) bila key tersedia; fallback edge-tts.
    if ELEVEN_KEY:
        try:
            return _generate_audio_eleven(script, output_path)
        except Exception as e:
            print(f"⚠️  ElevenLabs gagal ({type(e).__name__}: {e}) — fallback edge-tts")

    cleaned = clean_script(script)
    # Batas waktu keras: kalau stream edge-tts macet (connected tapi berhenti
    # kirim data), batalkan agar loop retry pemanggil bisa mengulang.
    async def _run():
        return await asyncio.wait_for(_synthesize(cleaned, output_path), timeout=300)
    segments = asyncio.run(_run())
    master_audio(output_path)

    srt_path = str(Path(output_path).with_suffix(".srt"))
    to_srt(segments, srt_path)

    print(f"Audio saved: {output_path}")
    print(f"Subtitle (akurat dari TTS): {srt_path} — {len(segments)} segmen")
    return segments
