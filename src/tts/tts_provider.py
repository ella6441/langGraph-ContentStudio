"""TTS Provider abstraction layer"""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import io

try:
    from elevenlabs import client as elevenlabs_client
    from elevenlabs.client import ElevenLabs as ElevenLabsSDK
except ImportError:
    ElevenLabsSDK = None


class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    async def synthesize(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        output_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            voice_id: Optional voice identifier
            output_path: Optional path to save audio
            metadata: Optional metadata for synthesis
            
        Returns:
            Audio bytes
        """
        pass
    
    @abstractmethod
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices"""
        pass


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS implementation"""
    
    def __init__(self, api_key: str, default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Initialize ElevenLabs provider
        
        Args:
            api_key: ElevenLabs API key
            default_voice_id: Default voice to use
        """
        if ElevenLabsSDK is None:
            raise ImportError("elevenlabs package not installed")
        
        self.client = ElevenLabsSDK(api_key=api_key)
        self.default_voice_id = default_voice_id
        self._voices_cache = None
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Synthesize text to speech using ElevenLabs"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        voice_id = voice_id or self.default_voice_id
        
        # Run API call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        audio_bytes = await loop.run_in_executor(
            None,
            self._synthesize_sync,
            text,
            voice_id
        )
        
        if output_path:
            async with asyncio.Lock():
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
        
        return audio_bytes
    
    def _synthesize_sync(self, text: str, voice_id: str) -> bytes:
        """Synchronous synthesis call"""
        audio = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1",
        )
        
        # Collect audio bytes
        audio_bytes = io.BytesIO()
        for chunk in audio:
            audio_bytes.write(chunk)
        
        return audio_bytes.getvalue()
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices from ElevenLabs"""
        if self._voices_cache is not None:
            return self._voices_cache
        
        loop = asyncio.get_event_loop()
        voices = await loop.run_in_executor(
            None,
            self._get_voices_sync
        )
        
        # Cache the result
        self._voices_cache = {
            v["voice_id"]: {
                "name": v["name"],
                "category": v.get("category", ""),
                "description": v.get("description", "")
            }
            for v in voices["voices"]
        }
        
        return self._voices_cache
    
    def _get_voices_sync(self) -> Dict[str, Any]:
        """Synchronous get voices call"""
        return self.client.voices.get_all()


class MockTTSProvider(TTSProvider):
    """Mock TTS provider for testing"""
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Return mock audio bytes"""
        # Simulate audio (MP3 header + minimal data)
        mock_audio = b'ID3' + b'\x00' * 100
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(mock_audio)
        
        return mock_audio
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Return mock voices"""
        return {
            "default_male": {"name": "Default Male", "category": "male"},
            "default_female": {"name": "Default Female", "category": "female"},
        }


def create_tts_provider(
    provider_type: str = "elevenlabs",
    api_key: Optional[str] = None,
    **kwargs
) -> TTSProvider:
    """
    Factory function to create TTS provider
    
    Args:
        provider_type: Type of provider ("elevenlabs" or "mock")
        api_key: API key for provider
        **kwargs: Additional provider arguments
        
    Returns:
        TTSProvider instance
    """
    if provider_type == "elevenlabs":
        if not api_key:
            from configs.config import config
            api_key = config.ELEVENLABS_API_KEY
        
        if not api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        return ElevenLabsProvider(api_key=api_key, **kwargs)
    
    elif provider_type == "mock":
        return MockTTSProvider()
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
