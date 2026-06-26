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
    Transcribes audio and generates an SRT file with 'Logical Flow' chunking.
    Groups words based on punctuation, natural pauses, and phrase logic.
    For short form videos, it limits chunking to 1-2 words at a time.
    """
    if not model:
        logger.error("Whisper model is not loaded. Cannot generate subtitles.")
        return None

    logger.info(f"Starting Whisper transcription for: {audio_path} ({video_format})")
    try:
        # Get word-level timestamps from Whisper
        result = model.transcribe(audio_path, word_timestamps=True)
        
        words = []
        for segment in result['segments']:
            words.extend(segment['words'])

        srt_content = ""
        index = 1
        
        buffer = []
        max_words_per_line = 2 if video_format == "short form" else 5
        
        for i, w in enumerate(words):
            word_text = w['word'].strip()
            buffer.append(w)
            
            # Check for logical break points:
            # 1. Ends with sentence-ending punctuation (. ? !)
            is_end_of_sentence = any(p in word_text for p in ['.', '?', '!'])
            
            # 2. Ends with a comma and the buffer is reasonably long
            is_comma_break = (',' in word_text) and len(buffer) >= (2 if video_format == "short form" else 3)
            
            # 3. Buffer reached hard limit
            is_full = len(buffer) >= max_words_per_line
            
            # 4. Long silence after the word (gap > 0.4 seconds)
            is_long_pause = False
            if i < len(words) - 1:
                gap = words[i+1]['start'] - w['end']
                if gap > 0.4:
                     is_long_pause = True

            # If any trigger is met, flush the buffer to a new SRT block
            if is_end_of_sentence or is_comma_break or is_full or is_long_pause:
                start = format_timestamp(buffer[0]['start'])
                end = format_timestamp(buffer[-1]['end'])
                text = " ".join([word['word'].strip() for word in buffer])
                
                # Filter out accidental empty blocks
                if text:
                    srt_content += f"{index}\n{start} --> {end}\n{text}\n\n"
                    index += 1
                
                buffer = []
        
        # Flush remaining words
        if buffer:
            start = format_timestamp(buffer[0]['start'])
            end = format_timestamp(buffer[-1]['end'])
            text = " ".join([word['word'].strip() for word in buffer])
            srt_content += f"{index}\n{start} --> {end}\n{text}\n\n"

        # Save SRT file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        logger.info(f"Successfully generated logical flow subtitles: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Transcription process failed: {e}")
        return None
