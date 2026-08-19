"""
Configuration examples for NotebookLM Studio
"""

# Example 1: Minimal TED Talk Configuration
ted_talk_minimal = {
    "topic": "Climate Change",
    "key_points": ["Causes", "Impact", "Solutions"],
    "target_audience": "General audience",
    # Uses defaults:
    # - duration_minutes: 18
    # - max_words: 2250
    # - language: "en"
}

# Example 2: Customized TED Talk
ted_talk_custom = {
    "topic": "Quantum Computing in Practice",
    "key_points": [
        "History of quantum computing",
        "Current capabilities",
        "Practical applications",
        "Challenges ahead",
        "Future prospects"
    ],
    "target_audience": "Software developers and researchers",
    "duration_minutes": 20,
    "max_words": 2500,
    "language": "en"
}

# Example 3: Minimal Podcast Configuration
podcast_minimal = {
    "topic": "Remote Work Culture",
    "num_segments": 3,
    "target_duration_minutes": 25,
    # Uses defaults:
    # - language: "en"
    # - speakers: ["host", "expert"]
}

# Example 4: Customized Podcast with Multiple Speakers
podcast_custom = {
    "topic": "The Future of Sustainable Technology",
    "num_segments": 5,
    "target_duration_minutes": 45,
    "language": "en",
    "speakers": ["host", "scientist", "entrepreneur", "policymaker"]
}

# Example 5: TED Talk for Different Audiences
ted_talks_by_audience = {
    "executive_summary": {
        "topic": "AI in Business",
        "key_points": ["ROI", "Implementation", "Risk Management", "Competitive Advantage"],
        "target_audience": "C-suite executives",
        "duration_minutes": 15,
        "max_words": 1875
    },
    "technical_deep_dive": {
        "topic": "AI in Business",
        "key_points": ["Architecture", "Algorithms", "Data Pipeline", "Infrastructure", "Scale"],
        "target_audience": "Software engineers",
        "duration_minutes": 20,
        "max_words": 2500
    },
    "general_audience": {
        "topic": "AI in Business",
        "key_points": ["What is AI", "How companies use it", "Jobs impact", "Society benefits"],
        "target_audience": "General public",
        "duration_minutes": 18,
        "max_words": 2250
    }
}

# Example 6: Batch Configuration File (JSON format)
batch_config = """
{
  "talks": [
    {
      "topic": "Artificial Intelligence",
      "key_points": ["Machine Learning", "GPT Models", "Applications"],
      "target_audience": "Tech enthusiasts",
      "duration_minutes": 18,
      "max_words": 2250
    },
    {
      "topic": "Climate Solutions",
      "key_points": ["Renewable Energy", "Carbon Capture", "Policy"],
      "target_audience": "Business leaders",
      "duration_minutes": 18,
      "max_words": 2250
    }
  ],
  "podcasts": [
    {
      "topic": "The future of work",
      "num_segments": 4,
      "target_duration_minutes": 30,
      "speakers": ["host", "researcher", "business_leader"]
    },
    {
      "topic": "Deep learning breakthroughs",
      "num_segments": 3,
      "target_duration_minutes": 25,
      "speakers": ["host", "expert"]
    }
  ]
}
"""

# Example 7: Custom Workflow Configuration (Python)
workflow_config = {
    "talk": {
        "max_revisions": 3,
        "critique_threshold": 7.0,
        "word_enforcement": "truncate",  # or "error", "summarize"
        "enable_approval_gate": True,
        "timeout_seconds": 300
    },
    "podcast": {
        "max_revisions": 2,
        "critique_threshold": 7.0,
        "parallel_research": True,
        "speakers_distribution": "round_robin",
        "enable_approval_gate": True,
        "timeout_seconds": 300
    },
    "audio": {
        "format": "mp3",
        "bitrate": "128k",
        "sample_rate": 44100,
        "crossfade_ms": 100,
        "tts_provider": "elevenlabs"  # or "mock" for testing
    }
}

# Example 8: Database Backup Configuration
backup_config = {
    "database": {
        "source": "notebooklm_studio.db",
        "backups_dir": "./backups",
        "auto_backup_interval_hours": 24,
        "keep_latest_backups": 7
    }
}

# Example 9: Monitoring Configuration
monitoring_config = {
    "langsmith": {
        "enabled": True,
        "api_key": "${LANGCHAIN_API_KEY}",
        "project_name": "notebooklm-studio",
        "sample_rate": 1.0  # Sample all runs
    },
    "metrics": {
        "collect_token_usage": True,
        "collect_timing": True,
        "collect_costs": True
    },
    "notifications": {
        "slack": {
            "enabled": False,
            "webhook_url": "${SLACK_WEBHOOK_URL}",
            "notify_on": ["completion", "error"]
        },
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "recipients": ["admin@example.com"]
        }
    }
}

# Example 10: Multi-Language Configuration
languages_config = {
    "english": {
        "language": "en",
        "llm_model": "gpt-4",
        "tts_voice_default": "21m00Tcm4TlvDq8ikWAM"
    },
    "hebrew": {
        "language": "he",
        "llm_model": "gpt-4",
        "tts_voice_default": "21m00Tcm4TlvDq8ikWAM"  # Need Hebrew voice
    },
    "spanish": {
        "language": "es",
        "llm_model": "gpt-4",
        "tts_voice_default": "21m00Tcm4TlvDq8ikWAM"  # Need Spanish voice
    }
}

if __name__ == "__main__":
    print("Configuration Examples for NotebookLM Studio")
    print("=" * 50)
    
    print("\n1. TED Talk Examples:")
    print("   - Minimal config available")
    print("   - Custom config available")
    print("   - Subject-specific configs available")
    
    print("\n2. Podcast Examples:")
    print("   - Minimal config available")
    print("   - Multi-speaker config available")
    
    print("\n3. Batch Processing:")
    print("   - See batch_config JSON variable")
    
    print("\n4. Advanced Options:")
    print("   - Workflow configuration")
    print("   - Monitoring setup")
    print("   - Multi-language support")
    
    print("\n📄 Save batch_config as 'config.json' and use:")
    print("   python -c 'import asyncio; from main import batch_generation;")
    print("   asyncio.run(batch_generation(\"config.json\"))'")
