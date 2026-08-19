"""Audio utilities"""
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
import io

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


async def generate_audio(
    text: str,
    provider,
    output_path: str,
    voice_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate audio from text using TTS provider
    
    Args:
        text: Text to synthesize
        provider: TTSProvider instance
        output_path: Path to save audio
        voice_id: Optional voice ID
        metadata: Optional metadata
        
    Returns:
        Audio info dict
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    audio_bytes = await provider.synthesize(
        text=text,
        voice_id=voice_id,
        output_path=output_path,
        metadata=metadata
    )
    
    # Get file size
    file_size_mb = len(audio_bytes) / (1024 * 1024)
    
    # Estimate duration (rough estimate: ~40KB per second for 128kbps MP3)
    duration_seconds = len(audio_bytes) / 40000
    
    return {
        "audio_path": output_path,
        "size_bytes": len(audio_bytes),
        "size_mb": round(file_size_mb, 2),
        "estimated_duration_seconds": round(duration_seconds, 1),
        "format": "mp3"
    }


async def merge_audio_streams(
    audio_paths: List[str],
    output_path: str,
    crossfade_duration_ms: int = 0
) -> Dict[str, Any]:
    """
    Merge multiple audio files
    
    Args:
        audio_paths: List of audio file paths
        output_path: Output file path
        crossfade_duration_ms: Crossfade duration in milliseconds
        
    Returns:
        Merge result info
    """
    if AudioSegment is None:
        raise ImportError("pydub package not installed")
    
    if not audio_paths:
        raise ValueError("No audio files provided")
    
    # Load first audio
    combined = AudioSegment.from_mp3(audio_paths[0])
    
    # Merge remaining audio files
    for audio_path in audio_paths[1:]:
        audio = AudioSegment.from_mp3(audio_path)
        
        if crossfade_duration_ms > 0:
            combined = combined.append(audio, crossfade=crossfade_duration_ms)
        else:
            combined = combined.append(audio)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Export combined audio
    combined.export(output_path, format="mp3", bitrate="128k")
    
    file_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
    
    return {
        "output_path": output_path,
        "duration_ms": len(combined),
        "duration_seconds": len(combined) / 1000,
        "size_mb": round(file_size_mb, 2),
        "num_segments": len(audio_paths)
    }


def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of audio file in seconds
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    if AudioSegment is None:
        raise ImportError("pydub package not installed")
    
    audio = AudioSegment.from_file(audio_path)
    return len(audio) / 1000.0


def adjust_audio_speed(
    audio_path: str,
    output_path: str,
    speed_factor: float = 1.0
) -> str:
    """
    Adjust audio playback speed
    
    Args:
        audio_path: Input audio path
        output_path: Output audio path
        speed_factor: Speed multiplier (1.0 = normal, 1.5 = 1.5x faster)
        
    Returns:
        Output path
    """
    if AudioSegment is None:
        raise ImportError("pydub package not installed")
    
    audio = AudioSegment.from_file(audio_path)
    
    # Speed adjustment using frame rate manipulation
    if speed_factor != 1.0:
        audio = audio.speedup(speed_factor)
    
    audio.export(output_path, format="mp3")
    return output_path
