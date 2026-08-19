"""
Advanced Usage Guide for NotebookLM Studio
===========================================

This document covers advanced usage patterns, customization,
and integration scenarios for NotebookLM Studio.
"""

# ============================================================================
# 1. CUSTOM WORKFLOW PIPELINES
# ============================================================================

"""
Example 1: Chaining Multiple Workflows
----------------------------------------
Generate a TED talk, then podcast on the same topic, then create audio.
"""

import asyncio
from src.schemas.models import TalkBrief, PodcastQuery
from src.graphs.ted_talk_graph import generate_ted_talk
from src.graphs.podcast_graph import generate_podcast
from src.graphs.audio_graph import generate_audio_from_script

async def multi_format_generation():
    # First: Generate TED talk
    talk_brief = TalkBrief(
        topic="Climate Change Solutions",
        key_points=["Renewable energy", "Policy", "Innovation", "Individual action"],
        target_audience="General public"
    )
    
    talk_result = await generate_ted_talk(talk_brief)
    talk_script = talk_result['talk']
    
    # Second: Generate podcast on same topic
    podcast_query = PodcastQuery(
        topic="Climate Change Solutions",
        num_segments=4,
        speakers=["host", "climate_scientist", "policy_expert"]
    )
    
    podcast_result = await generate_podcast(podcast_query)
    
    # Third: Generate audio formats for both
    ted_audio = await generate_audio_from_script(
        script=talk_script,
        output_dir="./output/ted_talk"
    )
    
    podcast_audio = await generate_audio_from_script(
        script=podcast_result['script'],
        output_dir="./output/podcast"
    )
    
    return {
        "talk": talk_result,
        "podcast": podcast_result,
        "ted_audio": ted_audio,
        "podcast_audio": podcast_audio
    }

# Usage:
# result = asyncio.run(multi_format_generation())


# ============================================================================
# 2. CUSTOM TTS PROVIDERS
# ============================================================================

"""
Example 2: Implementing a Custom TTS Provider
----------------------------------------------
"""

from src.tts.tts_provider import TTSProvider
from abc import abstractmethod
from typing import Optional, Dict, Any

class AzureTTSProvider(TTSProvider):
    """Azure Speech Services TTS implementation"""
    
    def __init__(self, 
                 subscription_key: str,
                 region: str,
                 default_voice: str = "en-US-AriaNeural"):
        self.subscription_key = subscription_key
        self.region = region
        self.default_voice = default_voice
        # Would initialize Azure SDK client here
    
    async def synthesize(self,
                        text: str,
                        voice_id: Optional[str] = None,
                        output_path: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> bytes:
        """Implement Azure TTS synthesis"""
        voice = voice_id or self.default_voice
        
        # Call Azure Speech Services API
        # ssml = f'<speak version="1.0" xml:lang="en-US"><voice name="{voice}">{text}</voice></speak>'
        # audio_bytes = azure_client.synthesize(ssml)
        
        # For now, return placeholder
        audio_bytes = b'audio_data'
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
        
        return audio_bytes
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Return Azure available voices"""
        return {
            "en-US-AriaNeural": {"name": "Aria", "gender": "female"},
            "en-US-GuyNeural": {"name": "Guy", "gender": "male"},
            # ... more voices
        }

# Usage:
# provider = AzureTTSProvider(subscription_key="...", region="eastus")
# audio = await provider.synthesize("Hello", voice_id="en-US-GuyNeural")


# ============================================================================
# 3. CUSTOM APPROVAL WORKFLOWS
# ============================================================================

"""
Example 3: Database-backed Approval System
-------------------------------------------
"""

from src.schemas.models import ApprovalRequest, ApprovalResponse
from datetime import datetime
import asyncio

class DatabaseApprovalManager:
    """Manage approvals through database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def request_approval(self, 
                              session_id: str,
                              content_type: str,
                              content: str,
                              word_count: int) -> str:
        """Store approval request in database"""
        
        row = {
            "session_id": session_id,
            "content_type": content_type,
            "content": content,
            "word_count": word_count,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        # Insert into database
        # result = self.db.insert("approvals", row)
        
        return session_id  # Request ID
    
    async def check_approval(self, 
                            request_id: str,
                            timeout_seconds: int = 300) -> ApprovalResponse:
        """Poll for approval decision"""
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            # Check database for approval
            # record = self.db.query("SELECT * FROM approvals WHERE id = ?", request_id)
            
            # if record and record['status'] != 'pending':
            #     return ApprovalResponse(
            #         approved=record['status'] == 'approved',
            #         feedback=record['notes']
            #     )
            
            await asyncio.sleep(1)  # Poll every second
        
        raise TimeoutError(f"Approval not received within {timeout_seconds}s")


# ============================================================================
# 4. BATCH GENERATION
# ============================================================================

"""
Example 4: Generate Multiple Talks/Podcasts in Batch
-----------------------------------------------------
"""

import json
from pathlib import Path

async def batch_generation(config_file: str):
    """Generate multiple outputs from config file"""
    
    with open(config_file) as f:
        config = json.load(f)
    
    results = []
    
    # Generate all talks
    for talk_config in config.get("talks", []):
        brief = TalkBrief(**talk_config)
        result = await generate_ted_talk(brief)
        results.append({"type": "talk", "config": talk_config, "result": result})
        print(f"Generated talk: {brief.topic}")
    
    # Generate all podcasts
    for podcast_config in config.get("podcasts", []):
        query = PodcastQuery(**podcast_config)
        result = await generate_podcast(query)
        results.append({"type": "podcast", "config": podcast_config, "result": result})
        print(f"Generated podcast: {query.topic}")
    
    return results

# Config file format (config.json):
# {
#   "talks": [
#     {
#       "topic": "...",
#       "key_points": [...],
#       "target_audience": "..."
#     }
#   ],
#   "podcasts": [
#     {
#       "topic": "...",
#       "num_segments": 4,
#       "speakers": ["host", "expert"]
#     }
#   ]
# }

# Usage:
# results = asyncio.run(batch_generation("config.json"))


# ============================================================================
# 5. MODIFYING WORKFLOW NODES
# ============================================================================

"""
Example 5: Inject Custom Logic Into Workflows
----------------------------------------------
"""

from langgraph.graph import StateGraph, END
from src.schemas.models import TalkState

def custom_write_talk(state: TalkState) -> TalkState:
    """Custom implementation of write_talk with additional processing"""
    from src.graphs.ted_talk_graph import write_talk as original_write_talk
    
    # Run original
    state = original_write_talk(state)
    
    # Add custom post-processing
    talk = state.initial_talk
    
    # Example: Add table of contents
    toc_text = "\n\n=== TABLE OF CONTENTS ===\n"
    paragraphs = talk.split("\n\n")
    for i, para in enumerate(paragraphs[:5], 1):
        first_sentence = para.split(".")[0]
        toc_text += f"{i}. {first_sentence[:50]}...\n"
    
    state.initial_talk = toc_text + "\n\n" + talk
    
    return state

# Then use in workflow:
# workflow.add_node("write", custom_write_talk)


# ============================================================================
# 6. MONITORING & ANALYTICS
# ============================================================================

"""
Example 6: Track Metrics Across Generations
---------------------------------------------
"""

from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class GenerationMetrics:
    session_id: str
    content_type: str  # "talk" or "podcast"
    start_time: datetime
    end_time: datetime
    total_words: int
    critique_score: float
    num_revisions: int
    audio_duration_seconds: float
    tokens_used: int
    cost_usd: float
    
    @property
    def generation_time_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def cost_per_word(self) -> float:
        return self.cost_usd / self.total_words if self.total_words > 0 else 0

class MetricsCollector:
    """Collect and analyze generation metrics"""
    
    def __init__(self):
        self.metrics: List[GenerationMetrics] = []
    
    def add_metric(self, metric: GenerationMetrics):
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.metrics:
            return {}
        
        talks = [m for m in self.metrics if m.content_type == "talk"]
        podcasts = [m for m in self.metrics if m.content_type == "podcast"]
        
        return {
            "total_generations": len(self.metrics),
            "talks_count": len(talks),
            "podcasts_count": len(podcasts),
            "avg_critique_score": sum(m.critique_score for m in self.metrics) / len(self.metrics),
            "avg_generation_time": sum(m.generation_time_seconds for m in self.metrics) / len(self.metrics),
            "total_words_generated": sum(m.total_words for m in self.metrics),
            "total_cost": sum(m.cost_usd for m in self.metrics),
            "avg_cost_per_word": sum(m.cost_per_word for m in self.metrics if m.cost_per_word > 0) / len(self.metrics)
        }

# Usage:
# collector = MetricsCollector()
# # ... after generation ...
# collector.add_metric(GenerationMetrics(...))
# print(collector.get_summary())


# ============================================================================
# 7. API CLIENT LIBRARY
# ============================================================================

"""
Example 7: Python Client for NotebookLM Studio API
--------------------------------------------------
"""

import httpx
from typing import Optional

class NotebookLMClient:
    """Python client for NotebookLM Studio API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def generate_ted_talk(self, brief: TalkBrief) -> str:
        """Generate TED talk and return session ID"""
        response = await self.client.post(
            "/api/ted-talk/generate",
            json=brief.dict()
        )
        return response.json()["session_id"]
    
    async def get_status(self, session_id: str) -> Dict:
        """Get generation status"""
        response = await self.client.get(f"/api/ted-talk/status/{session_id}")
        return response.json()
    
    async def wait_for_completion(self, 
                                  session_id: str,
                                  timeout_seconds: int = 300) -> Dict:
        """Wait for generation to complete"""
        import asyncio
        
        start = datetime.now()
        
        while (datetime.now() - start).total_seconds() < timeout_seconds:
            status = await self.get_status(session_id)
            
            if status["status"] not in ["processing", "initialized"]:
                return status
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Generation did not complete within {timeout_seconds}s")
    
    async def approve_and_generate_audio(self, session_id: str) -> str:
        """Approve content and generate audio"""
        # Approve
        await self.client.get(f"/api/ted-talk/approve/{session_id}?approved=true")
        
        # Generate audio
        response = await self.client.post(
            "/api/audio/generate",
            params={"session_id": session_id}
        )
        
        return session_id
    
    async def download_audio(self, session_id: str, output_path: str):
        """Download generated audio file"""
        response = await self.client.get(f"/api/audio/download/{session_id}")
        
        with open(output_path, "wb") as f:
            f.write(response.content)

# Usage:
# async def main():
#     client = NotebookLMClient()
#     
#     brief = TalkBrief(topic="...", key_points=[...], ...)
#     session_id = await client.generate_ted_talk(brief)
#     
#     status = await client.wait_for_completion(session_id)
#     print(f"Status: {status['status']}")
#     
#     await client.approve_and_generate_audio(session_id)
#     await client.download_audio(session_id, "output.mp3")


# ============================================================================
# 8. INTEGRATIONS
# ============================================================================

"""
Example 8: Integration with External Services
----------------------------------------------
"""

# Slack Notification
async def notify_slack_on_completion(webhook_url: str, session_id: str, result: Dict):
    """Send Slack notification when generation completes"""
    import httpx
    
    message = {
        "text": "🎬 Content Generation Complete",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Session:* {session_id}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Word Count:* {result['word_count']}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Quality Score:* {result.get('critique_score', 'N/A')}/10"}},
        ]
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=message)


# Email Notification
async def send_email_notification(smtp_server: str,
                                  recipient: str,
                                  session_id: str,
                                  download_link: str):
    """Send email with download link"""
    # Use aiosmtplib for async SMTP
    # ...


# Database Logging
async def log_to_database(db_connection,
                         session_id: str,
                         metrics: GenerationMetrics):
    """Log generation details to database"""
    # Insert into generations table
    # ...


if __name__ == "__main__":
    print(__doc__)
