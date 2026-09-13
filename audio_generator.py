import asyncio
import edge_tts
import os
from config import TTS_VOICE, TTS_RATE
from utils import setup_logger

logger = setup_logger("AudioGenerator")

async def generate_audio_async(text, output_path, voice=TTS_VOICE, rate=TTS_RATE):
    """
    Generate TTS audio via Microsoft Edge TTS (async).
    Rate nudges delivery speed, which is most of what makes a read feel
    energetic rather than like a documentary.
    """
    if not text or not text.strip():
        logger.error("❌ Empty text, cannot generate audio")
        return False

    try:
        logger.info(f"🔊 TTS: {len(text)} chars → {output_path}")
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(output_path)

        if os.path.exists(output_path):
            logger.info(f"✓ Audio saved: {output_path}")
            return True
        else:
            logger.error("❌ TTS completed but file not found")
            return False

    except Exception as e:
        logger.error(f"❌ TTS error: {str(e)[:80]}")
        return False


def generate_audio(text, output_path):
    """
    Sync wrapper for generate_audio_async.
    Runs async TTS generator in event loop.
    """
    try:
        return asyncio.run(generate_audio_async(text, output_path))
    except Exception as e:
        logger.error(f"❌ TTS event loop failed: {str(e)[:80]}")
        return False
