"""Word counting utilities"""
import re
from typing import Tuple


def count_words(text: str) -> int:
    """
    Count words in text with language support
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split by whitespace and filter out empty strings
    words = text.split()
    return len(words)


def enforce_word_limit(text: str, max_words: int, mode: str = "truncate") -> str:
    """
    Enforce word limit on text
    
    Args:
        text: Input text
        max_words: Maximum allowed words
        mode: "truncate" (cut off), "summarize" (stub), or "error" (raise)
        
    Returns:
        Adjusted text
        
    Raises:
        ValueError: If mode is "error" and text exceeds limit
    """
    word_count = count_words(text)
    
    if word_count <= max_words:
        return text
    
    if mode == "error":
        raise ValueError(f"Text exceeds word limit: {word_count} > {max_words}")
    
    elif mode == "truncate":
        words = text.split()
        truncated = " ".join(words[:max_words])
        # Add ellipsis
        return truncated + "..."
    
    elif mode == "summarize":
        # Placeholder - in production use summarization model
        return enforce_word_limit(text, max_words, mode="truncate")
    
    return text


def estimate_reading_time(text: str, words_per_minute: int = 150) -> Tuple[int, int]:
    """
    Estimate reading time
    
    Args:
        text: Input text
        words_per_minute: Average reading speed
        
    Returns:
        Tuple of (minutes, seconds)
    """
    word_count = count_words(text)
    total_seconds = int((word_count / words_per_minute) * 60)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return minutes, seconds


def estimate_speech_time(text: str, words_per_minute: int = 130) -> Tuple[int, int]:
    """
    Estimate speaking time (slower than reading)
    
    Args:
        text: Input text
        words_per_minute: Average speaking speed (typically 120-150 for presentations)
        
    Returns:
        Tuple of (minutes, seconds)
    """
    return estimate_reading_time(text, words_per_minute)
