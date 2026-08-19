"""FastAPI application for NotebookLM Studio"""
from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os

from src.schemas.models import (
    TalkBrief, 
    PodcastQuery, 
    ApprovalRequest,
    ApprovalResponse,
    StudioSession,
    AudioOutput
)
from src.graphs.ted_talk_graph import create_ted_talk_graph, generate_ted_talk
from src.graphs.podcast_graph import create_podcast_graph, generate_podcast
from src.graphs.audio_graph import generate_audio_from_script, generate_podcast_audio
from src.tts.tts_provider import create_tts_provider
from configs.config import config


# In-memory storage for sessions (in production, use database)
SESSIONS: Dict[str, StudioSession] = {}
APPROVAL_QUEUE: Dict[str, ApprovalRequest] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown"""
    print("Starting NotebookLM Studio...")
    yield
    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="NotebookLM Studio API",
        description="Mini NotebookLM with LangGraph - TED Talks & Podcasts",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ==================== HEALTH CHECK ====================
    
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    
    # ==================== TED TALK ENDPOINTS ====================
    
    @app.post("/api/ted-talk/generate", response_model=StudioSession)
    async def generate_ted_talk_endpoint(
        brief: TalkBrief,
        background_tasks: BackgroundTasks
    ) -> StudioSession:
        """
        Start TED talk generation
        
        Args:
            brief: TalkBrief with requirements
            background_tasks: Background task runner
            
        Returns:
            StudioSession with session info
        """
        try:
            session_id = str(uuid.uuid4())
            
            session = StudioSession(
                session_id=session_id,
                session_type="ted_talk",
                status="processing",
                created_at=datetime.now().isoformat()
            )
            
            SESSIONS[session_id] = session
            
            # Run graph in background
            background_tasks.add_task(
                _run_ted_talk_workflow,
                session_id=session_id,
                brief=brief
            )
            
            return session
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/api/ted-talk/status/{session_id}")
    async def get_ted_talk_status(session_id: str) -> Dict[str, Any]:
        """Get status of TED talk generation"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSIONS[session_id]
        return {
            "session_id": session.session_id,
            "status": session.status,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "content_preview": session.content[:500] if session.content else None
        }
    
    
    @app.get("/api/ted-talk/approve/{session_id}")
    async def approve_ted_talk(session_id: str, approved: bool = True) -> Dict[str, Any]:
        """Approve or reject TED talk"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSIONS[session_id]
        session.approvals.append(
            ApprovalResponse(
                approved=approved,
                feedback="Approved via API"
            )
        )
        session.approved = approved
        session.status = "approved" if approved else "rejected"
        session.updated_at = datetime.now().isoformat()
        
        return {"status": session.status}
    
    
    # ==================== PODCAST ENDPOINTS ====================
    
    @app.post("/api/podcast/generate", response_model=StudioSession)
    async def generate_podcast_endpoint(
        query: PodcastQuery,
        background_tasks: BackgroundTasks
    ) -> StudioSession:
        """
        Start podcast generation
        
        Args:
            query: PodcastQuery with requirements
            background_tasks: Background task runner
            
        Returns:
            StudioSession with session info
        """
        try:
            session_id = str(uuid.uuid4())
            
            session = StudioSession(
                session_id=session_id,
                session_type="podcast",
                status="processing",
                created_at=datetime.now().isoformat()
            )
            
            SESSIONS[session_id] = session
            
            # Run graph in background
            background_tasks.add_task(
                _run_podcast_workflow,
                session_id=session_id,
                query=query
            )
            
            return session
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/api/podcast/status/{session_id}")
    async def get_podcast_status(session_id: str) -> Dict[str, Any]:
        """Get status of podcast generation"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSIONS[session_id]
        return {
            "session_id": session.session_id,
            "status": session.status,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "content_preview": session.content[:500] if session.content else None
        }
    
    
    @app.get("/api/podcast/approve/{session_id}")
    async def approve_podcast(session_id: str, approved: bool = True) -> Dict[str, Any]:
        """Approve or reject podcast"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSIONS[session_id]
        session.approvals.append(
            ApprovalResponse(
                approved=approved,
                feedback="Approved via API"
            )
        )
        session.approved = approved
        session.status = "approved" if approved else "rejected"
        session.updated_at = datetime.now().isoformat()
        
        return {"status": session.status}
    
    
    # ==================== AUDIO ENDPOINTS ====================
    
    @app.post("/api/audio/generate")
    async def generate_audio_endpoint(
        session_id: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """
        Generate audio for approved content
        
        Args:
            session_id: Session ID to generate audio for
            background_tasks: Background task runner
            
        Returns:
            Audio generation info
        """
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSIONS[session_id]
        
        if not session.content:
            raise HTTPException(status_code=400, detail="No content to generate audio from")
        
        if not session.approved:
            raise HTTPException(status_code=400, detail="Content must be approved first")
        
        # Generate audio in background
        background_tasks.add_task(
            _generate_audio_for_session,
            session_id=session_id
        )
        
        return {
            "status": "audio_generation_started",
            "session_id": session_id
        }
    
    
    @app.get("/api/audio/download/{session_id}")
    async def download_audio(session_id: str):
        """Download generated audio file"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSIONS[session_id]
        
        if not session.audio_output or not session.audio_output.audio_path:
            raise HTTPException(status_code=404, detail="Audio not generated yet")
        
        audio_path = session.audio_output.audio_path
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=audio_path,
            filename=f"{session.session_id}.mp3",
            media_type="audio/mpeg"
        )
    
    
    # ==================== SESSIONS ENDPOINTS ====================
    
    @app.get("/api/sessions")
    async def list_sessions() -> Dict[str, Any]:
        """List all sessions"""
        return {
            "total": len(SESSIONS),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "type": s.session_type,
                    "status": s.status,
                    "created_at": s.created_at
                }
                for s in SESSIONS.values()
            ]
        }
    
    
    @app.get("/api/session/{session_id}")
    async def get_session(session_id: str) -> StudioSession:
        """Get full session details"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SESSIONS[session_id]
    
    
    @app.delete("/api/session/{session_id}")
    async def delete_session(session_id: str) -> Dict[str, str]:
        """Delete a session"""
        if session_id not in SESSIONS:
            raise HTTPException(status_code=404, detail="Session not found")
        
        del SESSIONS[session_id]
        return {"status": "deleted"}
    
    
    # ==================== APPROVAL ENDPOINTS ====================
    
    @app.get("/api/approvals")
    async def get_pending_approvals() -> Dict[str, Any]:
        """Get pending approvals"""
        return {
            "pending": len(APPROVAL_QUEUE),
            "approvals": [
                {
                    "approval_id": k,
                    "content_type": v.content_type,
                    "word_count": v.word_count
                }
                for k, v in APPROVAL_QUEUE.items()
            ]
        }
    
    
    @app.post("/api/approve/{approval_id}")
    async def submit_approval(
        approval_id: str,
        response: ApprovalResponse
    ) -> Dict[str, str]:
        """Submit approval decision"""
        if approval_id not in APPROVAL_QUEUE:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        del APPROVAL_QUEUE[approval_id]
        
        return {
            "status": "approval_recorded",
            "decision": "approved" if response.approved else "rejected"
        }
    
    
    return app


# ==================== BACKGROUND TASKS ====================

async def _run_ted_talk_workflow(session_id: str, brief: TalkBrief):
    """Background task to run TED talk workflow"""
    try:
        session = SESSIONS[session_id]
        session.status = "generating"
        session.updated_at = datetime.now().isoformat()
        
        # Generate talk
        result = await generate_ted_talk(brief)
        
        session.content = result["talk"]
        session.status = "review_pending"
        session.updated_at = datetime.now().isoformat()
        
    except Exception as e:
        session.status = "error"
        session.updated_at = datetime.now().isoformat()
        print(f"Error in TED talk workflow: {str(e)}")


async def _run_podcast_workflow(session_id: str, query: PodcastQuery):
    """Background task to run podcast workflow"""
    try:
        session = SESSIONS[session_id]
        session.status = "generating"
        session.updated_at = datetime.now().isoformat()
        
        # Generate podcast
        result = await generate_podcast(query)
        
        session.content = result["script"]
        session.status = "review_pending"
        session.updated_at = datetime.now().isoformat()
        
    except Exception as e:
        session.status = "error"
        session.updated_at = datetime.now().isoformat()
        print(f"Error in podcast workflow: {str(e)}")


async def _generate_audio_for_session(session_id: str):
    """Background task to generate audio for session"""
    try:
        session = SESSIONS[session_id]
        
        audio_output = await generate_audio_from_script(
            script=session.content,
            output_dir=f"./audio_output/{session_id}"
        )
        
        session.audio_output = audio_output
        session.status = "complete"
        session.updated_at = datetime.now().isoformat()
        
    except Exception as e:
        session.status = "audio_error"
        session.updated_at = datetime.now().isoformat()
        print(f"Error in audio generation: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )
