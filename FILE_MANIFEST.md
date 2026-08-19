"""
FILE MANIFEST - NotebookLM Studio Project
==========================================

Complete inventory of all project files and their purposes.
"""

# ============================================================================
# CORE APPLICATION FILES
# ============================================================================

CORE_FILES = {
    "main.py": {
        "purpose": "CLI entry point for direct workflow execution",
        "lines": 55,
        "functions": [
            "main() - Async main function demonstrating TED talk + podcast generation"
        ],
        "dependencies": ["src.graphs", "src.schemas"]
    },
    
    "run_api.py": {
        "purpose": "API server entry point",
        "lines": 45,
        "functions": [
            "Main: Starts FastAPI server with uvicorn"
        ],
        "dependencies": ["src.backend", "configs"]
    },
    
    "setup.py": {
        "purpose": "Project setup and initialization script",
        "lines": 90,
        "functions": [
            "setup_environment() - Creates .env, directories, validates Python"
        ]
    }
}

# ============================================================================
# LangGraph WORKFLOWS
# ============================================================================

WORKFLOW_FILES = {
    "src/graphs/ted_talk_graph.py": {
        "purpose": "TED talk generation workflow (Phase C)",
        "lines": 460,
        "nodes": [
            "plan_talk() - Create outline",
            "gather_context() - Research topic",
            "write_talk() - Write full script",
            "critique_script() - Quality assessment",
            "revise_talk() - Revise based on feedback"
        ],
        "functions": [
            "should_revise() - Conditional routing",
            "create_ted_talk_graph() - Graph factory",
            "generate_ted_talk() - Async wrapper"
        ],
        "state_type": "TalkState"
    },
    
    "src/graphs/podcast_graph.py": {
        "purpose": "Podcast generation workflow (Phase D)",
        "lines": 370,
        "nodes": [
            "research_topic_parallel() - Parallel research (5 aspects)",
            "segment_content() - Create segments with word budgets",
            "assemble_full_script() - Combine with intro/outro",
            "critique_podcast() - Quality evaluation",
            "revise_podcast() - Revise full script"
        ],
        "functions": [
            "should_revise_podcast() - Conditional routing",
            "create_podcast_graph() - Graph factory",
            "generate_podcast() - Async wrapper"
        ],
        "state_type": "PodcastState"
    },
    
    "src/graphs/audio_graph.py": {
        "purpose": "Audio generation with multi-speaker TTS",
        "lines": 380,
        "nodes": [
            "parse_speakers() - Extract speaker info from script",
            "initialize_tts() - Setup TTS provider",
            "synthesize_segments() - Generate audio per segment",
            "merge_audio() - Combine with crossfade"
        ],
        "functions": [
            "create_audio_graph() - Graph factory",
            "generate_audio_from_script() - Async wrapper",
            "generate_podcast_audio() - Podcast-specific helper"
        ],
        "state_type": "AudioGraphState"
    }
}

# ============================================================================
# DATA MODELS & SCHEMAS
# ============================================================================

SCHEMA_FILES = {
    "src/schemas/models.py": {
        "purpose": "Pydantic models for all data types",
        "lines": 230,
        "models": [
            "TalkBrief - Input for TED talk generation",
            "CritiqueResult - Quality assessment output",
            "TalkState - Workflow state for talks",
            "PodcastSegment - Individual podcast segment",
            "PodcastQuery - Input for podcast generation",
            "PodcastState - Workflow state for podcasts",
            "AudioOutput - Generated audio metadata",
            "ApprovalRequest - Human review request",
            "ApprovalResponse - Approval decision",
            "StudioSession - Session tracking"
        ]
    }
}

# ============================================================================
# TEXT-TO-SPEECH LAYER
# ============================================================================

TTS_FILES = {
    "src/tts/tts_provider.py": {
        "purpose": "TTS provider abstraction and implementations",
        "lines": 250,
        "classes": [
            "TTSProvider - Abstract base class",
            "ElevenLabsProvider - ElevenLabs implementation",
            "MockTTSProvider - Testing/mock implementation"
        ],
        "functions": [
            "create_tts_provider() - Factory function"
        ]
    },
    
    "src/tts/audio_utils.py": {
        "purpose": "Audio processing utilities",
        "lines": 200,
        "functions": [
            "generate_audio() - Synthesize text to audio",
            "merge_audio_streams() - Combine audio files",
            "get_audio_duration() - Get audio length",
            "adjust_audio_speed() - Change playback speed"
        ]
    }
}

# ============================================================================
# UTILITIES
# ============================================================================

UTILITY_FILES = {
    "src/utils/word_counter.py": {
        "purpose": "Word counting and enforcement",
        "lines": 100,
        "functions": [
            "count_words() - Count words in text",
            "enforce_word_limit() - Enforce max words",
            "estimate_reading_time() - Calculate reading duration",
            "estimate_speech_time() - Calculate speaking duration"
        ]
    },
    
    "src/utils/validators.py": {
        "purpose": "Content validation utilities",
        "lines": 80,
        "functions": [
            "validate_word_count() - Validate word count with tolerance",
            "validate_critique_score() - Validate quality score",
            "validate_content_structure() - Validate paragraph count"
        ]
    }
}

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILES = {
    "configs/config.py": {
        "purpose": "Configuration management",
        "lines": 130,
        "classes": [
            "Config - Base configuration",
            "DevelopmentConfig - Dev settings",
            "ProductionConfig - Prod settings",
            "TestingConfig - Test settings"
        ],
        "functions": [
            "get_config() - Get appropriate config"
        ]
    },
    
    ".env.example": {
        "purpose": "Environment variables template",
        "lines": 35,
        "contains": [
            "API keys (OpenAI, ElevenLabs, LangSmith)",
            "Server configuration",
            "Database settings",
            "Content limits",
            "Workflow parameters",
            "Timeout settings"
        ]
    }
}

# ============================================================================
# BACKEND & API
# ============================================================================

BACKEND_FILES = {
    "src/backend/app.py": {
        "purpose": "FastAPI application and endpoints",
        "lines": 500,
        "endpoints": {
            "TED Talk": [
                "POST /api/ted-talk/generate",
                "GET /api/ted-talk/status/{session_id}",
                "GET /api/ted-talk/approve/{session_id}"
            ],
            "Podcast": [
                "POST /api/podcast/generate",
                "GET /api/podcast/status/{session_id}",
                "GET /api/podcast/approve/{session_id}"
            ],
            "Audio": [
                "POST /api/audio/generate",
                "GET /api/audio/download/{session_id}"
            ],
            "Session Management": [
                "GET /api/sessions",
                "GET /api/session/{session_id}",
                "DELETE /api/session/{session_id}"
            ],
            "Health": [
                "GET /health",
                "GET /docs",
                "GET /redoc"
            ]
        },
        "background_tasks": [
            "_run_ted_talk_workflow()",
            "_run_podcast_workflow()",
            "_generate_audio_for_session()"
        ]
    }
}

# ============================================================================
# EXAMPLES
# ============================================================================

EXAMPLE_FILES = {
    "examples/example_ted_talk.py": {
        "purpose": "Complete TED talk generation pipeline example",
        "lines": 70,
        "demonstrates": [
            "TalkBrief creation",
            "generate_ted_talk() function",
            "Audio generation from script",
            "Output saving"
        ]
    },
    
    "examples/example_podcast.py": {
        "purpose": "Complete podcast generation pipeline example",
        "lines": 70,
        "demonstrates": [
            "PodcastQuery creation",
            "generate_podcast() function",
            "Segment breakdown",
            "Multi-speaker audio generation"
        ]
    },
    
    "examples/config_examples.py": {
        "purpose": "Configuration and usage patterns",
        "lines": 200,
        "contains": [
            "TED talk minimal and custom configs",
            "Podcast configurations",
            "Multi-audience examples",
            "Batch processing config",
            "Workflow configuration patterns",
            "Monitoring setup",
            "Multi-language support"
        ]
    }
}

# ============================================================================
# DOCUMENTATION
# ============================================================================

DOCUMENTATION_FILES = {
    "README.md": {
        "purpose": "Project overview and quick start guide",
        "lines": "600+",
        "sections": [
            "Features overview",
            "Architecture diagram",
            "Quick start (5 steps)",
            "API endpoint reference",
            "Key design decisions",
            "Configuration reference",
            "Example usage (Python)",
            "Extending the system",
            "Troubleshooting",
            "Support resources"
        ]
    },
    
    "ARCHITECTURE.md": {
        "purpose": "Detailed system design and workflow documentation",
        "lines": "800+",
        "sections": [
            "System architecture overview",
            "TED talk workflow diagram",
            "Podcast workflow diagram",
            "Audio generation workflow",
            "State flow diagrams",
            "Node specifications table",
            "Memory & token management",
            "Checkpointing details",
            "Error handling strategies",
            "Integration points"
        ]
    },
    
    "INSTRUCTIONS.md": {
        "purpose": "Detailed setup and operational guide",
        "lines": "600+",
        "sections": [
            "Prerequisite installation",
            "Step-by-step setup",
            "Running examples",
            "API usage (CURL examples)",
            "Python usage patterns",
            "Configuration reference",
            "Troubleshooting guide",
            "Performance optimization",
            "Production deployment",
            "Monitoring & debugging"
        ]
    },
    
    "ADVANCED_USAGE.md": {
        "purpose": "Advanced patterns and integrations",
        "lines": "500+",
        "examples": [
            "Custom TTS providers",
            "Database approval systems",
            "Batch generation",
            "Custom workflow nodes",
            "Metrics collection",
            "Python API client",
            "External service integrations",
            "Slack notifications",
            "Email notifications"
        ]
    },
    
    "PROJECT_SUMMARY.md": {
        "purpose": "Project completion summary and statistics",
        "lines": "200+",
        "contains": [
            "Component checklist",
            "Statistics and metrics",
            "Technology stack",
            "API endpoint summary",
            "Quick start commands",
            "Performance characteristics",
            "Known limitations",
            "Future improvements"
        ]
    }
}

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

PROJECT_CONFIG_FILES = {
    "requirements.txt": {
        "purpose": "Python package dependencies",
        "packages": 15,
        "key_packages": [
            "langgraph",
            "langchain",
            "langchain-openai",
            "pydantic",
            "fastapi",
            "uvicorn",
            "elevenlabs",
            "pydub"
        ]
    },
    
    ".env.example": {
        "purpose": "Template for environment variables",
        "variables": 25
    },
    
    ".gitignore": {
        "purpose": "Git ignore patterns",
        "patterns": "60+",
        "ignored": [
            "Python cache files",
            ".env files",
            "Database files",
            "Audio outputs",
            "IDE settings",
            "OS files"
        ]
    }
}

# ============================================================================
# PACKAGE INITIALIZATION FILES
# ============================================================================

INIT_FILES = {
    "src/__init__.py": "Main package init",
    "src/graphs/__init__.py": "Graphs module init (exports graph factories)",
    "src/schemas/__init__.py": "Schemas module init (exports Pydantic models)",
    "src/tts/__init__.py": "TTS module init (exports providers and utilities)",
    "src/utils/__init__.py": "Utils module init (exports helper functions)",
    "src/backend/__init__.py": "Backend module init (exports Flask app)"
}

# ============================================================================
# FILE ORGANIZATION BY PURPOSE
# ============================================================================

FILES_BY_PURPOSE = {
    "Core Logic": [
        "src/graphs/ted_talk_graph.py",
        "src/graphs/podcast_graph.py",
        "src/graphs/audio_graph.py"
    ],
    
    "Data & Models": [
        "src/schemas/models.py"
    ],
    
    "Integrations": [
        "src/tts/tts_provider.py",
        "src/tts/audio_utils.py"
    ],
    
    "Utilities": [
        "src/utils/word_counter.py",
        "src/utils/validators.py"
    ],
    
    "API & Backend": [
        "src/backend/app.py"
    ],
    
    "Configuration": [
        "configs/config.py",
        ".env.example"
    ],
    
    "Entry Points": [
        "main.py",
        "run_api.py",
        "setup.py"
    ],
    
    "Examples": [
        "examples/example_ted_talk.py",
        "examples/example_podcast.py",
        "examples/config_examples.py"
    ],
    
    "Documentation": [
        "README.md",
        "ARCHITECTURE.md",
        "INSTRUCTIONS.md",
        "ADVANCED_USAGE.md",
        "PROJECT_SUMMARY.md",
        "FILE_MANIFEST.md"
    ]
}

# ============================================================================
# STATISTICS
# ============================================================================

STATISTICS = {
    "Total Files": 30,
    "Python Source Files": 18,
    "Documentation Files": 6,
    "Configuration Files": 3,
    "Example Files": 3,
    
    "Total Lines of Code": "3,500+",
    "Workflow Code": "1,210 lines",
    "Backend Code": "500 lines",
    "Data Models": "230 lines",
    "TTS Layer": "450 lines",
    "Utilities": "180 lines",
    "Configuration": "130 lines +"
    "Example Code": "340 lines",
    "Documentation": "2,400+ lines",
    
    "Number of Functions": "50+",
    "Number of Classes": "20+",
    "API Endpoints": "15+",
    "Workflow Nodes": "12+",
    "Data Models": "10+"
}

# ============================================================================
# QUICK FILE REFERENCE
# ============================================================================

if __name__ == "__main__":
    print("FILE MANIFEST - NotebookLM Studio")
    print("=" * 70)
    
    print("\n📁 CORE WORKFLOWS:")
    for file, info in WORKFLOW_FILES.items():
        print(f"  {file}")
        print(f"    Purpose: {info['purpose']}")
        print(f"    Nodes: {len(info['nodes'])}")
    
    print("\n🔌 INTEGRATIONS:")
    for file, info in TTS_FILES.items():
        print(f"  {file}")
        print(f"    Purpose: {info['purpose']}")
    
    print("\n📚 DOCUMENTATION:")
    for file, info in DOCUMENTATION_FILES.items():
        print(f"  {file} (~{info['lines']} lines)")
    
    print("\n✅ PROJECT STATISTICS:")
    for key, value in STATISTICS.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("TOTAL: 30+ files, 3,500+ lines of production-ready code")
    print("=" * 70)
