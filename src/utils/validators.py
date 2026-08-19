"""Validation utilities"""
from typing import Dict, Any
from src.utils.word_counter import count_words


def validate_word_count(text: str, expected: int, tolerance_percent: float = 10.0) -> Dict[str, Any]:
    """
    Validate word count with tolerance
    
    Args:
        text: Text to validate
        expected: Expected word count
        tolerance_percent: Acceptable deviation percentage
        
    Returns:
        Validation result dict
    """
    actual = count_words(text)
    tolerance_words = int(expected * tolerance_percent / 100)
    lower_bound = expected - tolerance_words
    upper_bound = expected + tolerance_words
    
    is_valid = lower_bound <= actual <= upper_bound
    deviation_percent = ((actual - expected) / expected * 100) if expected > 0 else 0
    
    return {
        "is_valid": is_valid,
        "actual_words": actual,
        "expected_words": expected,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "deviation_percent": round(deviation_percent, 2),
        "message": f"Word count: {actual} (expected ~{expected} ±{tolerance_words})"
    }


def validate_critique_score(score: float, threshold: float = 7.0) -> Dict[str, Any]:
    """
    Validate critique score
    
    Args:
        score: Score 0-10
        threshold: Minimum acceptable score
        
    Returns:
        Validation result
    """
    return {
        "is_acceptable": score >= threshold,
        "score": score,
        "threshold": threshold,
        "message": f"Score {score}/10 {'✓ Acceptable' if score >= threshold else '✗ Needs improvement'}"
    }


def validate_content_structure(content: str, min_paragraphs: int = 1) -> Dict[str, Any]:
    """
    Validate content structure
    
    Args:
        content: Content to validate
        min_paragraphs: Minimum required paragraphs
        
    Returns:
        Validation result
    """
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    has_valid_structure = len(paragraphs) >= min_paragraphs
    
    return {
        "is_valid": has_valid_structure,
        "paragraph_count": len(paragraphs),
        "min_required": min_paragraphs,
        "message": f"Structure: {len(paragraphs)} paragraphs found"
    }
