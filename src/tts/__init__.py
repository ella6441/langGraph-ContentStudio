"""Text-to-Speech abstraction layer"""
from .tts_provider import TTSProvider, ElevenLabsProvider
from .audio_utils import generate_audio, merge_audio_streams

__all__ = [
    "TTSProvider",
    "ElevenLabsProvider",
    "generate_audio",
    "merge_audio_streams",
]
