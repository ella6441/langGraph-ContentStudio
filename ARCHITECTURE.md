# Architecture & Workflow Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ TED Talk   │  │ Podcast    │  │ Audio Generation      │  │
│  │ Endpoints  │  │ Endpoints  │  │ & Management          │  │
│  └─────┬──────┘  └─────┬──────┘  └──────────┬───────────┘  │
│        │                │                   │               │
└────────┼────────────────┼───────────────────┼───────────────┘
         │                │                   │
         ▼                ▼                   ▼
    ┌─────────────────────────────────────────┐
    │      LangGraph Workflows                │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │ TED Talk Workflow (Linear)        │  │  <- Phase C
    │  │ plan → context → write → critique │  │
    │  │  ↑                          ↓      │  │
    │  │  └────── revise ◄──────────┘      │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │ Podcast Workflow (Parallel+Serial)  │
    │  │ research ⟹ segment → assemble →    │  │ <- Phase D
    │  │   critique → revise ◄──────┘       │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    │  ┌──────────────────────────────────┐  │
    │  │ Audio Graph (Multi-Speaker TTS)   │  │
    │  │ parse → tts_init → synthesize →   │  │
    │  │   merge → metadata                │  │
    │  └──────────────────────────────────┘  │
    │                                         │
    └─────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
    ┌──────────┐  ┌────────────┐  ┌──────────────┐
    │Checkpointer  State Mgmt  │  │Word Counter  │
    │SqliteSaver   Pydantic   │  │& Validators  │
    └──────────┘  └────────────┘  └──────────────┘
         │                          │
         ▼                          ▼
    ┌──────────────────────────────────────┐
    │  External Services                   │
    │  ┌───────┐  ┌────────────┐ ┌────────┐│
    │  │OpenAI │  │ElevenLabs  │ │LangSmith
    │  │ GPT-4 │  │ TTS Service│ │Tracing ││
    │  └───────┘  └────────────┘ └────────┘│
    └──────────────────────────────────────┘
```

## Detailed Workflow Diagrams

### TED Talk Generation (Linear Workflow)

```
REQUEST
   │
   ├─ TalkBrief(topic, key_points, duration, max_words)
   │
   ▼
┌──────────────────────────────────────────────────────┐
│                  PLAN TALK NODE                      │
│  LLM: Generate detailed outline & structure         │
│  Output: TalkState.context = plan_text              │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│               GATHER CONTEXT NODE                    │
│  LLM: Research & provide contextual information     │
│  Input: brief.topic, brief.key_points               │
│  Output: TalkState.context += research_findings    │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│                WRITE TALK NODE                       │
│  LLM: Write complete talk script                    │
│  Input: TalkState.context (outline + research)      │
│  Processing: Enforce word limit via code             │
│    - Count words explicitly: count_words(text)      │
│    - Truncate if needed: enforce_word_limit()       │
│  Output: TalkState.initial_talk                     │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│              CRITIQUE SCRIPT NODE                    │
│  LLM: Evaluate quality, structure, engagement       │
│  Input: TalkState.initial_talk + brief.topic        │
│  Output: TalkState.critique = CritiqueResult        │
│    - score (0-10)                                   │
│    - feedback (detailed)                            │
│    - issues (list)                                  │
│    - suggestions (list)                             │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│           CONDITIONAL DECISION                       │
│  if critique.score >= THRESHOLD and revisions < MAX:│
│    → Route to REVISE                               │
│  else:                                              │
│    → Finalize and END                              │
└──────────────────────────────────────────────────────┘
   │
   ├─ [score too low & revisions available]
   │                ▼
   │┌──────────────────────────────────────────────────┐
   ││               REVISE NODE                        │
   ││  LLM: Rewrite based on critique feedback        │
   ││  Input: TalkState.initial_talk + critique data  │
   ││  Processing:                                    │
   ││    - Enforce word limit again                  │
   ││    - Increment TalkState.revisions              │
   ││  Output: TalkState.initial_talk (revised)       │
   ││          → Loop back to CRITIQUE                │
   │└──────────────────────────────────────────────────┘
   │                ▼
   │         [back to CRITIQUE]
   │
   └─ [score acceptable OR max revisions reached]
                   ▼
            ┌──────────────────┐
            │ Set final_talk   │
            │ Return result    │
            └──────────────────┘
                   │
                   ▼
              OUTPUT
          TalkState with:
          - final_talk (approved content)
          - critique_score (final score)
          - revisions (number of revisions)
          - word_count (actual)
```

### Podcast Generation (Parallel + Sequential Workflow)

```
REQUEST
   │
   ├─ PodcastQuery(topic, num_segments, duration, speakers)
   │
   ▼
┌──────────────────────────────────────────────────────┐
│             RESEARCH TOPIC (PARALLEL)                │
│  Launch 5 concurrent research queries:               │
│    • Trends & statistics                            │
│    • Expert perspectives                            │
│    • Real-world applications                        │
│    • Misconceptions                                 │
│    • Future predictions                             │
│                                                      │
│  Each runs in parallel: research_results = {        │
│    "Trends": "...",                                 │
│    "Expert": "...",                                 │
│    ...                                              │
│  }                                                   │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│              SEGMENT CONTENT NODE                    │
│  For each of N segments:                            │
│    1. Calculate word budget:                        │
│       budget = (duration_min × 150 WPM) / N_segs    │
│    2. LLM: Write segment (assign speaker)           │
│    3. Count words: enforce budget via code          │
│    4. If over: truncate to budget * 1.2            │
│       → Dynamic budget allocation                   │
│                                                      │
│  Output: List[PodcastSegment] with:                │
│    - segment_id                                     │
│    - topic (from research aspect)                   │
│    - content (script)                               │
│    - speaker (host/expert/narrator)                 │
│    - word_count                                     │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│            ASSEMBLE FULL SCRIPT                      │
│  1. LLM: Generate intro (~100 words)                │
│  2. Concatenate all segments with headers           │
│  3. LLM: Generate outro (~80 words, CTA)            │
│                                                      │
│  Output: PodcastState.full_script                   │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│              CRITIQUE PODCAST                        │
│  LLM: Quality assessment                            │
│  Output: PodcastState.critique = CritiqueResult    │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│           CONDITIONAL DECISION                       │
│  Similar to TED Talk routing                        │
└──────────────────────────────────────────────────────┘
   │
   ├─ [if needs revision & revisions < 2]
   │            ▼
   │   ┌─────────────────────┐
   │   │  REVISE NODE        │
   │   │  Rewrite full text  │
   │   │  Enforce budgets    │
   │   │  Loop to CRITIQUE   │
   │   └─────────────────────┘
   │
   └─ [else] → END with final_script

OUTPUT: PodcastState with segments & full_script
```

### Audio Generation (Multi-Speaker TTS)

```
REQUEST
   │
   ├─ Script (with ### Speaker: markers)
   │  "### Topic (Speaker: host)\n..."
   │
   ▼
┌──────────────────────────────────────────────────────┐
│           PARSE SPEAKERS NODE                        │
│  1. Split by ### markers                            │
│  2. Extract speaker names from (Speaker: X) pattern │
│  3. Build segments with speaker assignments         │
│                                                      │
│  Output: AudioGraphState.segments[]                 │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│          INITIALIZE TTS NODE                         │
│  1. Create TTSProvider (ElevenLabs or mock)         │
│  2. Build speaker → voice_id mapping:              │
│     {                                               │
│       "host": "21m00Tcm4TlvDq8ikWAM",              │
│       "expert": "IZSifZKynQvn3XoKmLc5",            │
│       ...                                           │
│     }                                               │
│  3. Create output directory                        │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│        SYNTHESIZE SEGMENTS NODE                      │
│  For each segment:                                  │
│    1. Get voice_id from speaker mapping            │
│    2. Call provider.synthesize(text, voice_id)     │
│    3. Save to: output_dir/segment_NNN_speaker.mp3  │
│    4. Update segment.output_path                    │
│    5. Estimate duration_seconds                     │
│  [All segments processed]                           │
└──────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────┐
│           MERGE AUDIO NODE                           │
│  1. Get all segment audio paths                     │
│  2. Load and sequentially merge with crossfade      │
│     (100ms fade between segments)                   │
│  3. Export to: output_dir/complete_audio.mp3        │
│  4. Get final file size and duration                │
└──────────────────────────────────────────────────────┘
   │
   ▼
OUTPUT: AudioOutput with:
   - audio_path
   - duration_seconds
   - size_mb
   - format
   - metadata (num_speakers, word_count, etc.)
```

## State Flow Diagrams

### TalkState Evolution

```
Initial State:
┌─────────────────────┐
│ brief: TalkBrief    │
│ context: None       │ ───┐
│ initial_talk: None  │    │
│ critique: None      │    │
│ final_talk: None    │    │
│ revisions: 0        │    │
└─────────────────────┘    │
                           │
After PLAN:                │
┌─────────────────────┐    │
│ context: outline    │ ◄──┘
└─────────────────────┘
        ↓
After GATHER_CONTEXT:
┌─────────────────────┐
│ context: outline +  │
│           research  │
└─────────────────────┘
        ↓
After WRITE:
┌─────────────────────┐
│ initial_talk: 2247  │
│              words  │
└─────────────────────┘
        ↓
After CRITIQUE:
┌─────────────────────┐
│ critique:           │
│  - score: 8.2       │
│  - issues: [...]    │
│  - needs_revision:  │
│    false            │
└─────────────────────┘
        ↓
Final State:
┌─────────────────────┐
│ final_talk:         │
│   approved script   │
│ approved: true      │
│ revisions: 1        │
└─────────────────────┘
```

### PodcastState Evolution

```
Initial State:
┌──────────────────────┐
│ query: PodcastQuery  │
│ research_results: {} │
│ segments: []         │
│ full_script: None    │
│ approved: false      │
└──────────────────────┘
     ↓
After RESEARCH:
┌──────────────────────┐
│ research_results: {  │
│   "Trends": "...",   │
│   "Expert": "...",   │
│   ...                │
│ }                    │
└──────────────────────┘
     ↓
After SEGMENT:
┌──────────────────────┐
│ segments: [          │
│   Segment(topic=..., │
│            speaker=  │
│            host),    │
│   Segment(..., host),│
│   ...                │
│ ]                    │
└──────────────────────┘
     ↓
After ASSEMBLE:
┌──────────────────────┐
│ full_script:         │
│   intro +            │
│   segment 1-4 +      │
│   outro              │
│ (~3200 words total)  │
└──────────────────────┘
     ↓
After CRITIQUE & APPROVE:
┌──────────────────────┐
│ critique:            │
│  - score: 7.8        │
│ approved: true       │
│ revisions: 0         │
└──────────────────────┘
```

## Node Input/Output Specifications

### TED Talk Nodes

| Node | Input | Output | Processing |
|------|-------|--------|-----------|
| plan_talk | TalkBrief | outline text | LLM: generate structure |
| gather_context | outline, topic | research text | LLM: research |
| write_talk | outline + research, max_words | script (enforced) | LLM + code enforcement |
| critique_script | script, topic | CritiqueResult | LLM + JSON parsing |
| revise | script, critique | revised script (enforced) | LLM + word limit |

### Podcast Nodes

| Node | Input | Output | Processing |
|------|-------|--------|-----------|
| research_topic | topic | {aspect: text} | 5x LLM parallel calls |
| segment_content | query, research | segments[] | 4x LLM + word budget |
| assemble_full | segments[] | full_script | Intro + segments + outro |
| critique_podcast | script, topic | CritiqueResult | LLM evaluation |
| revise | script, critique | revised script | LLM rewrite |

### Audio Nodes

| Node | Input | Output | Processing |
|------|-------|--------|-----------|
| parse_speakers | script | segments[] | Regex/string parsing |
| initialize_tts | - | provider, mapping | SDK init, config |
| synthesize | segments[], mapping | segments[] (with audio_path) | 4x TTS async calls |
| merge_audio | audio_paths[] | complete_audio.mp3 | pydub merge + crossfade |

## Memory & Token Management

### Typical Token Usage

```
TED Talk Generation:
  - plan_talk: ~2000 tokens
  - gather_context: ~2500 tokens
  - write_talk: ~4000 tokens (output 2250 words ≈ 3000 tokens)
  - critique_script: ~2000 tokens
  - revise (if needed): ~3000 tokens
  
  Total: ~9500-13500 tokens per successful generation

Podcast Generation:
  - research_topic: ~2000 × 5 = ~10000 tokens
  - segment_content: ~1500 × 4 = ~6000 tokens
  - assemble_full: ~500 tokens
  - critique_podcast: ~2000 tokens
  - revise (if needed): ~2000 tokens
  
  Total: ~20500-24500 tokens per successful generation
```

### Optimization Strategies

1. **Context Window Management**
   - Limit research snippets to first 500 chars in prompts
   - Use summaries instead of full text for long scripts

2. **Caching**
   - Research results cached within session
   - Voices list cached after first provider call

3. **Early Termination**
   - Stop revision loop if target reached
   - Skip revisions if score already high

## Checkpointing & State Persistence

### SqliteSaver Configuration

```python
checkpointer = SqliteSaver(db="sqlite:///./notebooklm_studio.db")

# Automatic state snapshots after each node:
# graph_state_v1_{thread_id}
# ├─ After "plan" node
# ├─ After "gather_context" node
# ├─ After "write" node
# └─ etc.

# Resume from checkpoint:
config = {"configurable": {"thread_id": "session-123"}}
result = graph.invoke(state, config=config)
```

### Interrupt Points

```python
# Pause before critique for human review
interrupt_before=["critique"]

# Workflow pauses and waits for input
# User reviews content via API
# Submit approval to resume

# Or for podcast:
interrupt_before=["critique"]
# Same pattern - pause before final assessment
```

## Error Handling & Fallbacks

```python
# TTS Provider Fallback
try:
    provider = ElevenLabsProvider(api_key)
except ImportError:
    provider = MockTTSProvider()  # For testing

# JSON Parsing Fallback
try:
    critique_data = json.loads(response)
except json.JSONDecodeError:
    critique_data = {
        "score": 7.0,
        "feedback": response,
        "issues": [],
        "suggestions": []
    }

# Word Count Enforcement
if word_count > max_words:
    text = truncate(text, max_words)  # Hard limit
```

## Integration Points

### With External Services

```
┌─────────────┐
│  Frontend   │
│   (React)   │
└──────┬──────┘
       │ REST API calls
       ▼
┌─────────────────────┐
│   FastAPI Server    │
│  (session mgmt)     │
└──────┬──────────────┘
       │ invoke workflows
       ▼
┌─────────────────────┐
│  LangGraph Graphs   │
└────┬────────┬───────┘
     │        │
     ▼        ▼
  OpenAI   ElevenLabs
  (GPT-4)  (TTS)
     │        │
     └────┬───┘
          ▼
  LangSmith (optional tracing)
```

### API Flow

```
1. POST /api/ted-talk/generate
   └─ FastAPI creates session
      └─ Background task invokes graph
         └─ Updates session.status

2. GET /api/ted-talk/status/{session_id}
   └─ Returns current state

3. GET /api/ted-talk/approve/{session_id}
   └─ Sets approval flag
      └─ Resumes workflow from interrupt

4. POST /api/audio/generate
   └─ Invokes audio graph
      └─ Generates audio_graph.py workflow

5. GET /api/audio/download/{session_id}
   └─ Streams MP3 file
```

---

**Key Takeaways:**
1. **Word enforcement at code level** - not just prompts
2. **Parallel research** for podcasts, linear for talks
3. **Multi-speaker TTS** with voice mapping to scripts
4. **Checkpointing** for fault tolerance and resumability
5. **Modular provider pattern** for TTS flexibility
