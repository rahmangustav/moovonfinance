_MODEL = None
_MAX_SECS = 6.0   # batas wall-clock per segmen — sinkron dgn core.tts._boundaries_to_segments


def _get_model():
    from faster_whisper import WhisperModel
    global _MODEL
    if _MODEL is None:
        print("   📥 Loading Whisper model...")
        _MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _MODEL


def _group_words(words) -> list[dict]:
    """Kelompokkan word-boundary whisper (objek ber-atribut .start/.end/.word)
    jadi segmen subtitle {start, end, text}. Dipenggal per kalimat (. ! ?),
    baris kepanjangan (>72 char), atau saat sudah >= _MAX_SECS detik — tanpa
    batas waktu, jeda bicara panjang tanpa tanda baca bisa membuat satu
    subtitle menggantung lama di layar."""
    result = []
    buf = []

    for word in words:
        buf.append(word)
        text = "".join(w.word for w in buf).strip()
        is_boundary = text.endswith(('.', '!', '?'))
        is_long = len(text) > 72
        is_slow = (buf[-1].end - buf[0].start) >= _MAX_SECS

        if is_boundary or is_long or is_slow:
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


def transcribe(audio_path: str) -> list[dict]:
    """Transcribe audio → list of {start, end, text} subtitle segments."""
    try:
        model = _get_model()
        segments, _ = model.transcribe(audio_path, word_timestamps=True, language="id")
        words = [w for seg in segments for w in (seg.words or [])]
        return _group_words(words)

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
