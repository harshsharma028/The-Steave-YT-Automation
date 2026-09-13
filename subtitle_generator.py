import os
import whisper
from datetime import timedelta
from config import WHISPER_MODEL
from utils import setup_logger

logger = setup_logger("SubtitleGenerator")

# Pre-load Whisper model globally to save time during multiple calls
try:
    model = whisper.load_model(WHISPER_MODEL)
except Exception as e:
    logger.error(f"Failed to load Whisper model '{WHISPER_MODEL}': {e}")
    model = None

def format_timestamp(seconds):
    """
    Formats raw seconds into the standard SRT timestamp format: HH:MM:SS,mmm
    """
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_subtitles(audio_path, output_path, video_format="long form"):
    """
    Transcribe audio → SRT subtitles with smart chunking.
    Groups words by punctuation/pauses. Short-form: 1-2 words/line. Long-form: 5 words/line.
    """
    if not model:
        logger.error("❌ Whisper model not loaded")
        return None

    logger.info(f"📝 Transcribing: {audio_path} ({video_format})")
    try:
        # Get word-level timestamps via Whisper transcription
        result = model.transcribe(audio_path, word_timestamps=True)

        words = []
        for segment in result['segments']:
            words.extend(segment['words'])

        srt_content = ""
        index = 1
        buffer = []
        max_words = 2 if video_format == "short form" else 5

        for i, w in enumerate(words):
            word_text = w['word'].strip()
            buffer.append(w)

            # Detect chunk boundaries (smart line breaking):
            # 1. Period, question, exclamation → end of sentence
            ends_sentence = any(p in word_text for p in ['.', '?', '!'])
            # 2. Comma → phrase break (if buffer has enough words)
            min_for_comma = 2 if video_format == "short form" else 3
            has_comma = (',' in word_text) and len(buffer) >= min_for_comma
            # 3. Max words per line reached
            is_full = len(buffer) >= max_words
            # 4. Long pause (>0.4s) after word → natural breath point
            has_pause = (i < len(words) - 1 and (words[i+1]['start'] - w['end']) > 0.4)

            # Flush buffer if any break point triggered
            if ends_sentence or has_comma or is_full or has_pause:
                if buffer:
                    start = format_timestamp(buffer[0]['start'])
                    end = format_timestamp(buffer[-1]['end'])
                    text = " ".join([w['word'].strip() for w in buffer])
                    srt_content += f"{index}\n{start} --> {end}\n{text}\n\n"
                    index += 1
                    buffer = []

        # Flush final buffer
        if buffer:
            start = format_timestamp(buffer[0]['start'])
            end = format_timestamp(buffer[-1]['end'])
            text = " ".join([w['word'].strip() for w in buffer])
            srt_content += f"{index}\n{start} --> {end}\n{text}\n\n"

        # Save SRT file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        logger.info(f"✓ Subtitles generated: {index-1} lines → {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"❌ Transcription failed: {str(e)[:80]}")
        return None
