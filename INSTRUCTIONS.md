"""Detailed Setup and Usage Instructions"""

# ============================================================================
# INSTALLATION & CONFIGURATION
# ============================================================================

## Prerequisites
- Python 3.9+
- OpenAI API key (https://platform.openai.com/)
- ElevenLabs API key (https://elevenlabs.io/)
- Optional: LangSmith API key for monitoring (https://smith.langchain.com/)

## Step 1: Clone and Setup
```bash
cd /path/to/notebooklm-studio
python setup.py
```

## Step 2: Configure Environment Variables
Edit `.env` file:
```
OPENAI_API_KEY=sk-your-key
ELEVENLABS_API_KEY=your-key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
ENVIRONMENT=development
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "from src.schemas.models import TalkBrief; print('Installation OK')"
```

# ============================================================================
# RUNNING EXAMPLES
# ============================================================================

## Generate a TED Talk
```bash
python examples/example_ted_talk.py
```

Output:
- Script: `output/ted_talk/script.txt`
- Audio (if TTS enabled): `output/ted_talk/complete_audio.mp3`

## Generate a Podcast
```bash
python examples/example_podcast.py
```

Output:
- Script: `output/podcast/script.txt`
- Segments with speaker info
- Audio (if TTS enabled): `output/podcast/complete_audio.mp3`

## Run API Server
```bash
python run_api.py
```

Server starts at: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

# ============================================================================
# API USAGE (CURL Examples)
# ============================================================================

## 1. Generate TED Talk
```bash
curl -X POST http://localhost:8000/api/ted-talk/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Future of AI",
    "key_points": ["Current capabilities", "Limitations", "Ethics"],
    "target_audience": "Tech enthusiasts",
    "duration_minutes": 18,
    "max_words": 2250,
    "language": "en"
  }'

# Response:
# {"session_id": "abc-123", "status": "processing", ...}
```

## 2. Check Status
```bash
curl http://localhost:8000/api/ted-talk/status/abc-123
```

## 3. Approve Content
```bash
curl "http://localhost:8000/api/ted-talk/approve/abc-123?approved=true"
```

## 4. Generate Audio
```bash
curl -X POST http://localhost:8000/api/audio/generate \
  -d "session_id=abc-123"
```

## 5. Download Audio
```bash
curl http://localhost:8000/api/audio/download/abc-123 \
  --output my_talk.mp3
```

# ============================================================================
# PYTHON USAGE
# ============================================================================

## Simple TED Talk Generation
```python
import asyncio
from src.schemas.models import TalkBrief
from src.graphs.ted_talk_graph import generate_ted_talk

async def main():
    brief = TalkBrief(
        topic="Renewable Energy",
        key_points=["Solar", "Wind", "Storage", "Integration"],
        target_audience="Business leaders",
    )
    
    result = await generate_ted_talk(brief)
    
    print(f"Talk generated:")
    print(f"  Words: {result['word_count']}")
    print(f"  Score: {result['critique_score']}/10")
    print(f"  Script preview: {result['talk'][:200]}...")

asyncio.run(main())
```

## With Audio Generation
```python
import asyncio
from src.schemas.models import TalkBrief
from src.graphs.ted_talk_graph import generate_ted_talk
from src.graphs.audio_graph import generate_audio_from_script

async def main():
    # Generate talk
    brief = TalkBrief(topic="...", key_points=[...], ...)
    talk_result = await generate_ted_talk(brief)
    
    # Generate audio
    audio_result = await generate_audio_from_script(
        script=talk_result['talk'],
        output_dir="./output/audio"
    )
    
    print(f"Audio generated: {audio_result.audio_path}")
    print(f"Duration: {audio_result.duration_seconds:.0f}s")

asyncio.run(main())
```

## Podcast with Custom Speakers
```python
from src.graphs.audio_graph import generate_audio_from_script

async def main():
    podcast_script = """
### Introduction (Speaker: host)
Welcome to our podcast...

### Expert Discussion (Speaker: researcher)
The latest research shows...
"""
    
    # Custom voice mapping
    voices = {
        "host": "21m00Tcm4TlvDq8ikWAM",      # Different voice
        "researcher": "IZSifZKynQvn3XoKmLc5"
    }
    
    audio = await generate_audio_from_script(
        script=podcast_script,
        output_dir="./podcast_audio",
        speaker_voice_mapping=voices
    )
```

# ============================================================================
# CONFIGURATION REFERENCE
# ============================================================================

## Environment Variables
```
# API Keys (Required)
OPENAI_API_KEY=sk-xxxx
ELEVENLABS_API_KEY=xxxx

# API Keys (Optional)
LANGCHAIN_API_KEY=xxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=notebooklm-studio

# Model Configuration
OPENAI_MODEL=gpt-4                 # gpt-4 or gpt-3.5-turbo
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite:///./notebooklm_studio.db

# Content Limits (word counts)
TED_TALK_MAX_WORDS=2250            # For 18-min talk
PODCAST_SEGMENT_MAX_WORDS=800      # Per segment

# Workflow Settings
MAX_REVISIONS_TED=3                # Max revision loops
MAX_REVISIONS_PODCAST=2
CRITIQUE_THRESHOLD=7.0             # Min acceptable score
LLM_TIMEOUT=60                     # Seconds
APPROVAL_TIMEOUT=300               # Seconds (5 min)

# Environment
ENVIRONMENT=development            # development|production|testing
```

## Available Voice IDs (ElevenLabs)
- `21m00Tcm4TlvDq8ikWAM` - Rachel (Female, warm)
- `IZSifZKynQvn3XoKmLc5` - Joshua (Male, professional)
- `ThT5KcBeYPX3keUQqHcr` - Bill (Male, neutral)
- `pFZP5JQG7iQjIQuC4Iy3` - Callum (Male, excited)
- `21m00Tcm4TlvDq8ikWAM` - Jessica (Female, friendly)

See ElevenLabs documentation for full list.

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

## Problem: "OPENAI_API_KEY not configured"
**Solution:** Check .env file exists and has valid key:
```bash
cat .env | grep OPENAI_API_KEY
```

## Problem: "ElevenLabs API key not found"
**Solution:** The system falls back to mock TTS for testing.
To use real TTS, set ELEVENLABS_API_KEY in .env:
```
ELEVENLABS_API_KEY=your-actual-key
```

## Problem: Word count exceeds limit
**Solution:** This is handled automatically:
- Code enforces word limit via `enforce_word_limit()` function
- Text is truncated if needed
- Each node respects the configured limits

## Problem: "LangSmith tracing not working"
**Solution:** 
1. Set LANGCHAIN_TRACING_V2=true in .env
2. Set LANGCHAIN_API_KEY to your LangSmith API key
3. Set LANGCHAIN_PROJECT to project name
4. Restart the application

## Problem: "Audio file not generating"
**Solution:** Check:
1. Is ElevenLabs configured? Check .env
2. Is content approved? Audio only generates for approved content
3. Check audio_output/ directory exists
4. Check logs for TTS provider errors

## Problem: "Workflow running slowly"
**Solution:**
1. Use gpt-3.5-turbo instead of gpt-4 (faster, cheaper)
2. Reduce MAX_REVISIONS_TED/PODCAST
3. Increase CRITIQUE_THRESHOLD to skip more revisions
4. Disable LangSmith tracing in .env

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

## Token Cost Estimates
- TED Talk: ~9,500-13,500 tokens
- Podcast: ~20,500-24,500 tokens

## Speed Optimization
```python
# Use faster model
OPENAI_MODEL=gpt-3.5-turbo

# Reduce revisions
MAX_REVISIONS_TED=1
MAX_REVISIONS_PODCAST=0

# Increase score threshold to avoid revisions
CRITIQUE_THRESHOLD=8.0
```

## Resource Monitoring
Monitor via LangSmith dashboard:
- Token usage per workflow
- Latency per node
- Error rates

## Database Backups
Backup SQLite database:
```bash
cp notebooklm_studio.db notebooklm_studio.db.backup
```

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

## Environment Setup
```bash
export ENVIRONMENT=production
export DEBUG=false
export OPENAI_MODEL=gpt-4
```

## Running as Service (systemd)
Create `/etc/systemd/system/notebooklm.service`:
```ini
[Unit]
Description=NotebookLM Studio API
After=network.target

[Service]
Type=simple
User=notebooklm
WorkingDirectory=/path/to/notebooklm-studio
ExecStart=/usr/bin/python3 run_api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl start notebooklm
sudo systemctl enable notebooklm
sudo journalctl -u notebooklm -f  # View logs
```

## Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_api.py"]
```

Build and run:
```bash
docker build -t notebooklm-studio .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e ELEVENLABS_API_KEY=... \
  notebooklm-studio
```

## Process Manager (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 src.backend.app:create_app
```

# ============================================================================
# MONITORING & DEBUGGING
# ============================================================================

## Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all LangChain/LangGraph operations will be verbose
```

## LangSmith Debugging
1. Go to https://smith.langchain.com/
2. Login with your API key
3. Select your project (notebooklm-studio)
4. View live traces of all API calls

## Database Inspection
```bash
sqlite3 notebooklm_studio.db

# List tables
.tables

# View checkpoints
SELECT * FROM storage LIMIT 5;

# View sessions info
.schema
```

## API Debugging
```bash
# Test endpoint
curl -v http://localhost:8000/health

# Check API docs
curl http://localhost:8000/openapi.json | python -m json.tool
```

# ============================================================================
# SUPPORT & RESOURCES
# ============================================================================

## Documentation Files
- `README.md` - Overview and quick start
- `ARCHITECTURE.md` - System design and workflows
- `ADVANCED_USAGE.md` - Custom integrations
- `examples/` - Working code examples

## External Resources
- LangGraph Docs: https://python.langchain.com/docs/langgraph
- FastAPI Docs: https://fastapi.tiangolo.com/
- ElevenLabs API: https://api.elevenlabs.io/docs
- OpenAI API: https://platform.openai.com/docs

## Getting Help
1. Check the examples directory
2. Review architecture documentation
3. Enable debug logging
4. Check LangSmith traces
5. Review application logs

---

**Happy generating! 🎬🎙️**
