#!/usr/bin/env python
"""Setup script for NotebookLM Studio"""
import os
import sys
from pathlib import Path

def setup_environment():
    """Setup project environment"""
    
    print("NotebookLM Studio - Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Python 3.9+ required")
        sys.exit(1)
    
    print("Python version OK")
    
    # Create .env if needed
    env_path = Path(".env")
    if not env_path.exists():
        print("\nCreating .env file...")
        with open(".env", "w") as f:
            f.write("""# NotebookLM Studio Configuration
# Fill in your API keys

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# ElevenLabs
ELEVENLABS_API_KEY=your-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# LangSmith (Optional)
LANGCHAIN_API_KEY=your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=notebooklm-studio

# Database
DATABASE_URL=sqlite:///./notebooklm_studio.db

# Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Content Limits
TED_TALK_MAX_WORDS=2250
PODCAST_SEGMENT_MAX_WORDS=800

# Workflow
MAX_REVISIONS_TED=3
MAX_REVISIONS_PODCAST=2
CRITIQUE_THRESHOLD=7.0

# Environment
ENVIRONMENT=development
""")
        print(".env file created - please fill in your API keys")
    else:
        print(".env file already exists")
    
    # Create output directories
    output_dirs = [
        "output/ted_talk",
        "output/podcast",
        "output/audio",
        "audio_output",
        ".checkpoints"
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("Output directories created")
    
    # Print next steps
    print("""
✨ Setup complete!

Next steps:
1. Edit .env file with your API keys:
   - OPENAI_API_KEY (from openai.com)
   - ELEVENLABS_API_KEY (from elevenlabs.io)
   
2. Install dependencies:
   pip install -r requirements.txt
   
3. Run examples:
   python examples/example_ted_talk.py
   python examples/example_podcast.py
   
4. Start API server:
   python run_api.py
   
5. Visit http://localhost:8000/docs for API documentation

📚 Documentation:
   - README.md: Overview and usage guide
   - ARCHITECTURE.md: Detailed system design
   - examples/: Real-world usage examples
""")

if __name__ == "__main__":
    setup_environment()
