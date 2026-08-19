"""Pydantic models for TED Talk and Podcast workflows"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TalkBrief(BaseModel):
    """Brief for TED Talk generation"""
    topic: str = Field(..., description="Main topic of the talk")
    key_points: List[str] = Field(..., description="Key points to cover")
    target_audience: str = Field(..., description="Target audience profile")
    duration_minutes: int = Field(default=18, description="Duration in minutes")
    max_words: int = Field(default=2250, description="Approximate word count for 18 min talk")
    language: str = Field(default="en", description="Language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "The Future of AI",
                "key_points": ["Current capabilities", "Limitations", "Ethical concerns", "Future roadmap"],
                "target_audience": "Tech enthusiasts and general public",
                "duration_minutes": 18,
                "max_words": 2250,
                "language": "en"
            }
        }


class CritiqueResult(BaseModel):
    """Critique feedback for talk/podcast segment"""
    score: float = Field(..., ge=0, le=10, description="Quality score 0-10")
    feedback: str = Field(..., description="Detailed feedback")
    issues: List[str] = Field(default_factory=list, description="Specific issues found")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    word_count: int = Field(..., description="Word count of the content")
    needs_revision: bool = Field(..., description="Whether revision is needed")


class TalkState(BaseModel):
    """State for TED Talk generation workflow"""
    brief: Optional[TalkBrief] = None
    context: Optional[str] = None
    initial_talk: Optional[str] = None
    critique: Optional[CritiqueResult] = None
    final_talk: Optional[str] = None
    approved: bool = False
    revisions: int = 0
    max_revisions: int = 3


class PodcastSegment(BaseModel):
    """Individual podcast segment"""
    segment_id: str = Field(..., description="Unique segment identifier")
    topic: str = Field(..., description="Segment topic")
    content: Optional[str] = None
    speaker: str = Field(default="host", description="Speaker/narrator")
    word_count: Optional[int] = None
    audio_path: Optional[str] = None


class PodcastQuery(BaseModel):
    """Query for podcast episode"""
    topic: str = Field(..., description="Episode topic")
    num_segments: int = Field(default=4, description="Number of segments")
    target_duration_minutes: int = Field(default=30, description="Target duration")
    language: str = Field(default="en", description="Language code")
    speakers: List[str] = Field(default_factory=lambda: ["host", "expert"], description="Speaker voices")
    

class PodcastState(BaseModel):
    """State for Podcast generation workflow"""
    query: Optional[PodcastQuery] = None
    research_results: Optional[Dict[str, Any]] = None
    segments: List[PodcastSegment] = Field(default_factory=list)
    full_script: Optional[str] = None
    critique: Optional[CritiqueResult] = None
    approved: bool = False
    revisions: int = 0
    max_revisions: int = 2


class AudioOutput(BaseModel):
    """Audio generation output"""
    audio_path: str = Field(..., description="Path to generated audio file")
    duration_seconds: float = Field(..., description="Audio duration in seconds")
    sample_rate: int = Field(default=44100, description="Audio sample rate")
    format: str = Field(default="mp3", description="Audio format")
    size_mb: float = Field(..., description="File size in MB")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ApprovalRequest(BaseModel):
    """Request for human approval"""
    content_type: str = Field(..., description="Type: 'talk' or 'podcast'")
    content: str = Field(..., description="Content to review")
    word_count: int = Field(..., description="Word count")
    critiqueScore: float = Field(..., description="Existing critique score")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApprovalResponse(BaseModel):
    """Response to approval request"""
    approved: bool = Field(..., description="Approval decision")
    feedback: Optional[str] = None
    request_revision: bool = Field(default=False)
    notes: Optional[str] = None


class StudioSession(BaseModel):
    """Studio session state"""
    session_id: str = Field(..., description="Unique session identifier")
    session_type: str = Field(..., description="Type: 'ted_talk' or 'podcast'")
    status: str = Field(default="initialized", description="Current status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = None
    content: Optional[str] = None
    audio_output: Optional[AudioOutput] = None
    approvals: List[ApprovalResponse] = Field(default_factory=list)
