"""
Channel profiles.

Everything that differs between channels lives here — art direction, voice,
and the personas used for writing and art direction. The pipeline itself is
shared, so a fix made once applies to every channel.

Select with the CHANNEL environment variable:
    CHANNEL=weird_history python main.py
"""

import importlib
import os
from dataclasses import dataclass

DEFAULT_CHANNEL = "facts"


@dataclass(frozen=True)
class Channel:
    key: str
    name: str
    voice: str
    rate: str
    style_prompt: str      # art direction wrapped around every image prompt
    script_persona: str    # how script_analyzer segments and frames a script
    art_director: str      # how prompt_generator writes scene descriptions
    thumbnail_brief: str   # art direction for the single thumbnail image


def load_channel(key=None):
    """
    Load a channel profile by key, falling back to the CHANNEL env var.
    """
    key = key or os.getenv("CHANNEL", DEFAULT_CHANNEL)
    try:
        module = importlib.import_module(f"channels.{key}")
    except ModuleNotFoundError as exc:
        available = ", ".join(available_channels())
        raise ValueError(
            f"Unknown channel '{key}'. Available: {available}"
        ) from exc
    return module.CHANNEL


def available_channels():
    here = os.path.dirname(__file__)
    return sorted(
        f[:-3] for f in os.listdir(here)
        if f.endswith(".py") and not f.startswith("_")
    )
