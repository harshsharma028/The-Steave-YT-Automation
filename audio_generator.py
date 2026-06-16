import asyncio
import edge_tts
import os
from config import TTS_VOICE
from utils import setup_logger

logger = setup_logger("AudioGenerator")

async def generate_audio_async(text, output_path, voice=TTS_VOICE):
    """
    Asynchronous function to generate TTS audio using Microsoft Edge TTS.
    """
    if not text:
        logger.error("TTS text is empty. Cannot generate audio.")
        return False
    
    try:
        logger.info(f"Generating audio for text snippet (Length: {len(text)} chars)")
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_path)
        
        if os.path.exists(output_path):
            logger.info(f"Audio file created successfully: {output_path}")
            return True
        else:
            logger.error("TTS completed but file was not found on disk.")
            return False
            
    except Exception as e:
        logger.error(f"TTS generation encountered an error: {e}")
        return False

def generate_audio(text, output_path):
    """
    Synchronous wrapper for generate_audio_async to allow easy integration
    in standard synchronous loops.
    """
    try:
        return asyncio.run(generate_audio_async(text, output_path))
    except Exception as e:
        logger.error(f"Failed to execute asynchronous TTS loop: {e}")
        return False
