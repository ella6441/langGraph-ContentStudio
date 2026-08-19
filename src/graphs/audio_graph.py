"""Audio generation graph with LangGraph"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from pathlib import Path
import os

from src.schemas.models import AudioOutput
from src.tts.tts_provider import create_tts_provider, TTSProvider
from src.tts.audio_utils import merge_audio_streams, generate_audio
from src.utils.word_counter import count_words
from configs.config import config


class AudioSegmentState(BaseModel):
    """State for audio generation"""
    text: str
    speaker: str
    voice_id: Optional[str] = None
    output_path: Optional[str] = None
    audio_bytes: Optional[bytes] = None
    duration_seconds: float = 0.0


class AudioGraphState(BaseModel):
    """State for full audio graph"""
    content: str
    segments: List[AudioSegmentState] = []
    speaker_to_voice_mapping: Dict[str, str] = {}
    tts_provider: Optional[TTSProvider] = None
    output_dir: str = "./audio_output"
    final_audio_path: Optional[str] = None
    approved: bool = False


# Voice mapping for different speakers
DEFAULT_VOICE_MAPPING = {
    "host": "21m00Tcm4TlvDq8ikWAM",  # Rachel - warm, engaging
    "expert": "IZSifZKynQvn3XoKmLc5",  # Joshua - professional
    "narrator": "ThT5KcBeYPX3keUQqHcr",  # Bill - neutral
    "speaker_1": "21m00Tcm4TlvDq8ikWAM",
    "speaker_2": "IZSifZKynQvn3XoKmLc5",
}


def parse_speakers(state: AudioGraphState) -> AudioGraphState:
    """Parse content to identify speakers and segments"""
    content = state.content
    segments = []
    
    # Simple parsing: look for ### SPEAKER: or [SPEAKER] patterns
    current_speaker = "host"
    current_text = ""
    
    for line in content.split('\n'):
        # Check for speaker marker
        if line.startswith("### "):
            # Save previous segment
            if current_text.strip():
                segment = AudioSegmentState(
                    text=current_text.strip(),
                    speaker=current_speaker
                )
                segments.append(segment)
            
            # Parse new speaker
            parts = line.replace("### ", "").split("(Speaker: ")
            if len(parts) > 1:
                current_speaker = parts[1].rstrip(")")
            
            current_text = ""
        elif line.startswith("### Segment") or line.startswith("## "):
            # Skip headers but mark segment break
            if current_text.strip():
                segment = AudioSegmentState(
                    text=current_text.strip(),
                    speaker=current_speaker
                )
                segments.append(segment)
            current_text = ""
        else:
            current_text += line + "\n"
    
    # Add final segment
    if current_text.strip():
        segment = AudioSegmentState(
            text=current_text.strip(),
            speaker=current_speaker
        )
        segments.append(segment)
    
    state.segments = segments
    
    # Setup speaker-to-voice mapping
    unique_speakers = set(s.speaker for s in segments)
    speaker_mapping = {}
    
    for i, speaker in enumerate(unique_speakers):
        if speaker in DEFAULT_VOICE_MAPPING:
            speaker_mapping[speaker] = DEFAULT_VOICE_MAPPING[speaker]
        else:
            # Fallback to default voices
            voices_list = list(DEFAULT_VOICE_MAPPING.values())
            speaker_mapping[speaker] = voices_list[i % len(voices_list)]
    
    state.speaker_to_voice_mapping = speaker_mapping
    
    return state


async def initialize_tts(state: AudioGraphState) -> AudioGraphState:
    """Initialize TTS provider"""
    try:
        provider = create_tts_provider(
            provider_type="elevenlabs",
            api_key=config.ELEVENLABS_API_KEY
        )
    except (ValueError, ImportError):
        # Fallback to mock provider if ElevenLabs not configured
        provider = create_tts_provider(provider_type="mock")
    
    state.tts_provider = provider
    
    # Create output directory
    Path(state.output_dir).mkdir(parents=True, exist_ok=True)
    
    return state


async def synthesize_segments(state: AudioGraphState) -> AudioGraphState:
    """Synthesize audio for each segment"""
    provider = state.tts_provider
    if not provider:
        raise ValueError("TTS provider not initialized")
    
    for i, segment in enumerate(state.segments):
        if not segment.text.strip():
            continue
        
        # Get voice ID for speaker
        voice_id = state.speaker_to_voice_mapping.get(
            segment.speaker,
            config.ELEVENLABS_VOICE_ID
        )
        
        # Generate output path
        output_path = os.path.join(
            state.output_dir,
            f"segment_{i:03d}_{segment.speaker}.mp3"
        )
        
        # Generate audio
        audio_info = await generate_audio(
            text=segment.text,
            provider=provider,
            output_path=output_path,
            voice_id=voice_id,
            metadata={"speaker": segment.speaker, "segment": i}
        )
        
        segment.output_path = output_path
        segment.duration_seconds = audio_info.get("estimated_duration_seconds", 0)
    
    state.segments = state.segments  # Ensure state is updated
    
    return state


async def merge_audio(state: AudioGraphState) -> AudioGraphState:
    """Merge all audio segments into final output"""
    segments = state.segments
    output_paths = [s.output_path for s in segments if s.output_path]
    
    if not output_paths:
        raise ValueError("No audio files to merge")
    
    final_output_path = os.path.join(
        state.output_dir,
        "complete_audio.mp3"
    )
    
    merge_info = await merge_audio_streams(
        audio_paths=output_paths,
        output_path=final_output_path,
        crossfade_duration_ms=100
    )
    
    state.final_audio_path = final_output_path
    
    return state


async def generate_metadata(state: AudioGraphState) -> AudioGraphState:
    """Generate audio metadata"""
    if not state.final_audio_path:
        raise ValueError("Final audio path not set")
    
    # This is handled during merge_audio, just return state
    return state


def create_audio_graph(use_async: bool = True):
    """
    Create audio generation graph
    
    Args:
        use_async: Whether to use async operations
        
    Returns:
        Compiled LangGraph workflow
    """
    
    workflow = StateGraph(AudioGraphState)
    
    # Add nodes
    workflow.add_node("parse_speakers", parse_speakers)
    workflow.add_node("initialize_tts", lambda s: initialize_tts(s))
    workflow.add_node("synthesize", lambda s: synthesize_segments(s))
    workflow.add_node("merge", lambda s: merge_audio(s))
    
    # Add edges
    workflow.set_entry_point("parse_speakers")
    workflow.add_edge("parse_speakers", "initialize_tts")
    workflow.add_edge("initialize_tts", "synthesize")
    workflow.add_edge("synthesize", "merge")
    workflow.add_edge("merge", END)
    
    # Compile
    app = workflow.compile()
    
    return app


async def generate_audio_from_script(
    script: str,
    output_dir: str = "./audio_output",
    speaker_voice_mapping: Optional[Dict[str, str]] = None
) -> AudioOutput:
    """
    Generate audio from script
    
    Args:
        script: Complete script with speaker markers
        output_dir: Directory to save audio files
        speaker_voice_mapping: Optional custom voice mapping
        
    Returns:
        AudioOutput with result info
    """
    
    graph = create_audio_graph()
    
    initial_state = AudioGraphState(
        content=script,
        output_dir=output_dir
    )
    
    if speaker_voice_mapping:
        initial_state.speaker_to_voice_mapping = speaker_voice_mapping
    
    result = graph.invoke(initial_state)
    
    # Get file info
    if result.final_audio_path and os.path.exists(result.final_audio_path):
        file_size_mb = os.path.getsize(result.final_audio_path) / (1024 * 1024)
        
        # Estimate duration from word count
        word_count = count_words(script)
        estimated_duration = word_count / 130 * 60  # ~130 words per minute
        
        return AudioOutput(
            audio_path=result.final_audio_path,
            duration_seconds=estimated_duration,
            sample_rate=44100,
            format="mp3",
            size_mb=round(file_size_mb, 2),
            metadata={
                "num_segments": len(result.segments),
                "speakers": list(result.speaker_to_voice_mapping.keys()),
                "word_count": word_count
            }
        )
    
    raise ValueError("Audio generation failed")


# Convenience function for podcast audio
async def generate_podcast_audio(
    segments,
    output_dir: str = "./audio_output"
) -> AudioOutput:
    """
    Generate audio for podcast segments
    
    Args:
        segments: List of PodcastSegment objects
        output_dir: Output directory
        
    Returns:
        AudioOutput
    """
    
    # Convert segments to script format
    script = "## PODCAST AUDIO\n\n"
    for segment in segments:
        script += f"### {segment.topic} (Speaker: {segment.speaker})\n\n"
        script += segment.content + "\n\n"
    
    return await generate_audio_from_script(script, output_dir)
