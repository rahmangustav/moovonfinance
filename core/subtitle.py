_MODEL = None


def _get_model():
    from faster_whisper import WhisperModel
    global _MODEL
    if _MODEL is None:
        print("   📥 Loading Whisper model...")
        _MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _MODEL


def transcribe(audio_path: str) -> list[dict]:
    """Transcribe audio → list of {start, end, text} subtitle segments."""
    try:
        model = _get_model()
        segments, _ = model.transcribe(audio_path, word_timestamps=True, language="id")

        result = []
        buf = []

        for seg in segments:
            for word in (seg.words or []):
                buf.append(word)
                text = "".join(w.word for w in buf).strip()
                is_boundary = text.endswith(('.', '!', '?'))
                is_long = len(text) > 72

                if (is_boundary or is_long) and buf:
                    result.append({
                        'start': buf[0].start,
                        'end':   buf[-1].end,
                        'text':  text,
                    })
                    buf = []

        if buf:
            result.append({
                'start': buf[0].start,
                'end':   buf[-1].end,
                'text':  "".join(w.word for w in buf).strip(),
            })

        return result

    except Exception as e:
        print(f"   ⚠️  Transcription failed: {e}")
        return []


def _ts(sec: float) -> str:
    h  = int(sec // 3600)
    m  = int((sec % 3600) // 60)
    s  = int(sec % 60)
    ms = int((sec % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(segments: list[dict], path: str):
    with open(path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{_ts(seg['start'])} --> {_ts(seg['end'])}\n{seg['text']}\n\n")
