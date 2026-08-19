#  Mini NotebookLM Studio with LangGraph

A complete AI-powered content creation studio for generating high-quality TED Talks and Podcasts with LangGraph workflows, human-in-the-loop approval, and professional audio generation.

##  Features

### Phase C: TED Talk Generation
- **Linear workflow**: `plan_talk` → `gather_context` → `write_talk` → `critique_script` → `revise`
- **Word count enforcement**: Strict word limit (default 2250 words for 18-min talks) via code, not just prompts
- **Critique loop**: Automatic revision based on quality scores with configurable thresholds
- **Human-in-the-loop**: `interrupt()` integration for manual approval at critical points
- **Checkpointing**: SqliteSaver for workflow state persistence and resumability
- **LangSmith monitoring**: Full integration for production observability

### Phase D: Podcast Generation
- **Parallel research**: Fan-out architecture for concurrent topic research
- **Dynamic segmentation**: Multi-segment writing with budget-aware word limits
- **Adaptive workflow**: Segment-level critique and revision with independent speaker assignment
- **Audio graph**: Separate `audio_graph.py` with multi-speaker TTS support (ElevenLabs)
- **Self-contained approval flow**: Independent human approval for audio generation

### Audio & TTS
- **Protocol-based TTS layer**: Abstract `TTSProvider` with ElevenLabs and mock implementations
- **Multi-speaker support**: Different voices for host, expert, narrator roles
- **Audio merging**: Crossfade support for seamless segment transitions
- **Format flexibility**: MP3 output with configurable bitrate

### Backend
- **FastAPI server**: RESTful API for workflow orchestration
- **Session management**: Persistent session tracking for long-running generations
- **Background tasks**: Async workflow execution without blocking the API
- **WebSocket ready**: Built-in hooks for real-time progress updates

##  Architecture

```
NotebookLM Studio/
├── src/
│   ├── graphs/                    # LangGraph workflows
│   │   ├── ted_talk_graph.py      # TED Talk workflow (linear)
│   │   ├── podcast_graph.py       # Podcast workflow (parallel + serial)
│   │   └── audio_graph.py         # Audio generation (multi-speaker TTS)
│   │
│   ├── schemas/                   # Pydantic models
│   │   └── models.py              # All data models
│   │
│   ├── tts/                       # Text-to-Speech layer
│   │   ├── tts_provider.py        # TTSProvider abstraction
│   │   └── audio_utils.py         # Audio processing utilities
│   │
│   ├── utils/                     # Utilities
│   │   ├── word_counter.py        # Word counting & enforcement
│   │   └── validators.py          # Content validators
│   │
│   └── backend/                   # FastAPI application
│       └── app.py                 # REST API endpoints
│
├── configs/
│   └── config.py                  # Configuration management
│
├── examples/                      # Usage examples
│   ├── example_ted_talk.py       # Full TED talk pipeline
│   └── example_podcast.py        # Full podcast pipeline
│
├── main.py                        # CLI entry point
├── run_api.py                     # API server entry point
├── requirements.txt               # Dependencies
└── .env.example                   # Environment variables template
```

##  Quick Start

### 1. Installation

```bash
# Clone or setup the project
cd notebooklm-studio

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY=sk-...
# - ELEVENLABS_API_KEY=your-key
# - LANGCHAIN_API_KEY=optional (for LangSmith tracing)
```

### 2. Generate a TED Talk

```bash
python examples/example_ted_talk.py
```

This will:
1. Create a TED talk outline on your chosen topic
2. Gather contextual research
3. Write a complete 2250-word script
4. Critique and revise until quality threshold (7/10) is met
5. Generate professional audio via ElevenLabs

### 3. Generate a Podcast

```bash
python examples/example_podcast.py
```

This will:
1. Research the topic in parallel (5 different aspects)
2. Break content into 4 segments with word budgets
3. Assign different speakers to segments
4. Generate and refine the full script
5. Create multi-speaker audio

### 4. Start the API Server

```bash
python run_api.py
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

##  API Endpoints

### TED Talk
- `POST /api/ted-talk/generate` - Start generation
- `GET /api/ted-talk/status/{session_id}` - Check progress
- `GET /api/ted-talk/approve/{session_id}` - Approve content

### Podcast
- `POST /api/podcast/generate` - Start generation
- `GET /api/podcast/status/{session_id}` - Check progress
- `GET /api/podcast/approve/{session_id}` - Approve content

### Audio
- `POST /api/audio/generate` - Generate audio from approved content
- `GET /api/audio/download/{session_id}` - Download generated audio

### Management
- `GET /api/sessions` - List all sessions
- `GET /api/session/{session_id}` - Get session details
- `DELETE /api/session/{session_id}` - Delete session

##  Key Design Decisions

### 1. Word Count Enforcement (Code Level)
```python
# In ted_talk_graph.py, not in prompt
talk_text = enforce_word_limit(talk_text, brief.max_words, mode="truncate")
```
- **Why**: Prompts often don't respect word limits reliably
- **Implementation**: Explicit token counting and truncation at node level
- **Podcast**: Dynamic budget allocation across segments with clamping

### 2. Linear vs Parallel Architecture
- **TED Talk**: Strictly linear `plan → context → write → critique → revise`
- **Podcast**: Parallel research, serial writing (with speaker rotation)
- **Rationale**: Different content types benefit from different workflows

### 3. Multi-Speaker Audio (Podcast)
```python
# Parse speaker markers from script
### Research Findings (Speaker: expert)

# Auto-assign voices
speaker_to_voice_mapping = {
    "host": "21m00Tcm4TlvDq8ikWAM",      # Rachel - warm
    "expert": "IZSifZKynQvn3XoKmLc5",    # Joshua - professional
}
```
- **Why**: More engaging and feels like real podcast production
- **Extensible**: Custom voice mappings supported

### 4. Checkpointing & Interrupts
```python
# Compile with checkpointing
app = workflow.compile(
    checkpointer=SqliteSaver(db=config.DATABASE_URL),
    interrupt_before=["critique"]  # Pause for human review
)
```
- **Benefit**: Resume workflows if connection drops
- **Human control**: Interrupt at critique stage for approval gates

##  Configuration

All settings via `configs/config.py`, overridable with environment variables:

```python
# Content
TED_TALK_MAX_WORDS=2250              # ~18 minute talk
PODCAST_SEGMENT_MAX_WORDS=800        # Per segment budget
MAX_REVISIONS_TED=3                  # Max revision loops
MAX_REVISIONS_PODCAST=2
CRITIQUE_THRESHOLD=7.0               # Minimum acceptable score (0-10)

# API
API_HOST=0.0.0.0
API_PORT=8000

# LLM
OPENAI_MODEL=gpt-4                   # Or gpt-3.5-turbo
OPENAI_API_KEY=sk-...

# TTS
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=notebooklm-studio
```

##  Workflow States

### TED Talk State
```python
class TalkState:
    brief: TalkBrief              # Input requirements
    context: str                  # Research & outline
    initial_talk: str             # First draft
    critique: CritiqueResult      # Quality assessment
    final_talk: str               # Final version
    approved: bool                # Human approval
    revisions: int                # Number of iterations
```

### Podcast State
```python
class PodcastState:
    query: PodcastQuery           # Input requirements
    research_results: dict        # Parallel research findings
    segments: List[Segment]       # Individual segments
    full_script: str              # Assembled script
    critique: CritiqueResult      # Quality assessment
    approved: bool                # Human approval
    revisions: int                # Number of iterations
```

##  Example Usage (Python)

```python
from src.schemas.models import TalkBrief
from src.graphs.ted_talk_graph import generate_ted_talk

async def create_talk():
    brief = TalkBrief(
        topic="AI Safety and Alignment",
        key_points=["Challenges", "Approaches", "Timeline"],
        target_audience="Technical audience",
        duration_minutes=18
    )
    
    result = await generate_ted_talk(brief)
    print(result['talk'])           # The full script
    print(result['word_count'])     # Actual word count
    print(result['critique_score']) # Quality 0-10

# Run
asyncio.run(create_talk())
```

##  TTS Provider Usage

```python
from src.tts.tts_provider import create_tts_provider

# Use ElevenLabs
provider = create_tts_provider(
    provider_type="elevenlabs",
    api_key="your-key"
)

# Synthesize
audio_bytes = await provider.synthesize(
    text="Hello world",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    output_path="output.mp3"
)

# Or use mock for testing
mock_provider = create_tts_provider(provider_type="mock")
```

##  Testing

Run without real API keys (mock mode):

```python
from src.tts.tts_provider import create_tts_provider

provider = create_tts_provider(provider_type="mock")
# All TTS calls return mock audio without API calls
```

##  Monitoring & Observability

### LangSmith Integration
Automatically enabled when `LANGCHAIN_TRACING_V2=true`:
- View all workflow executions
- See node-by-node execution traces
- Monitor token usage
- Trace latency metrics

### Local Debugging
```python
# Enable SQLite checkpointer for state inspection
graph = create_ted_talk_graph(checkpointer_type="sqlite")

# Invoke with config
config = {"configurable": {"thread_id": "session-123"}}
result = graph.invoke(initial_state, config=config)
```

##  Extending the System

### Add Custom Node
```python
def my_custom_node(state: TalkState) -> TalkState:
    # Your logic here
    state.custom_field = "value"
    return state

workflow.add_node("custom", my_custom_node)
workflow.add_edge("critique", "custom")
```

### Add Custom TTS Provider
```python
from src.tts.tts_provider import TTSProvider

class GoogleTTSProvider(TTSProvider):
    async def synthesize(self, text, voice_id=None, **kwargs):
        # Your implementation
        pass
    
    async def get_available_voices(self):
        # Return voice mapping
        pass
```

### Custom Approval Handler
```python
async def my_approval_handler(approval_request):
    # Your logic: send email, Slack, database, etc.
    return ApprovalResponse(approved=True)

graph = create_ted_talk_graph(approval_handler=my_approval_handler)
```

##  Output Examples

### TED Talk Output
```
[Generated TED Talk Script - ~2250 words]
- Opening hook (60s)
- Problem introduction (2-3 min)
- Key insights (10-12 min)
- Examples and case studies (3-5 min)
- Call to action (1-2 min)

[Critique Score: 8.5/10]
[Audio generated: 18m 35s at 44.1kHz]
```

### Podcast Output
```
## PODCAST SCRIPT

### Segment 1: Current Trends (Speaker: host)
[~800 words on trending aspects]

### Segment 2: Expert Perspective (Speaker: expert)
[~800 words from expert angle]

### Segment 3: Applications (Speaker: host)
[~800 words on practical uses]

### Segment 4: Future Outlook (Speaker: expert)
[~800 words on predictions]

[Critique Score: 7.8/10]
[Audio generated: 31m 12s with multi-speaker]
```

##  Troubleshooting

### OpenAI API Key Error
```python
# Make sure .env is loaded and API key is valid
from configs.config import config
print(config.OPENAI_API_KEY)  # Should not be empty
```

### ElevenLabs TTS Fails
```python
# Falls back to mock provider automatically
# Set ELEVENLABS_API_KEY in .env
# Or use provider_type="mock" for testing
```

### Word Count Exceeds Limit
```python
# Automatic truncation + ellipsis
from src.utils.word_counter import enforce_word_limit

text = enforce_word_limit(text, max_words=2250, mode="truncate")
```

##  Dependencies

```
langgraph             # Workflow orchestration
langchain             # LLM integrations
langchain-openai      # OpenAI provider
pydantic              # Data validation
fastapi               # REST API
uvicorn               # ASGI server
elevenlabs            # TTS provider
pydub                 # Audio processing
```


##  Contributing

Contributions welcome! Areas for improvement:
- Additional TTS providers (Google Cloud, Azure)
- Database backend for production sessions
- WebSocket support for real-time progress
- Multi-language support
- Transcript editor UI

## Author

**Rivky Peretz**
[GitHub](https://github.com/rivky9523) · [Email](mailto:r0548551732@gmail.com)
