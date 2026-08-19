"""Main entry point for NotebookLM Studio"""
import asyncio
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.schemas.models import TalkBrief, PodcastQuery
from src.graphs.ted_talk_graph import generate_ted_talk
from src.graphs.podcast_graph import generate_podcast
from src.graphs.audio_graph import generate_audio_from_script


async def main():
    """Main async function"""
    print("NotebookLM Studio with LangGraph")
    print("=" * 50)
    
    # Example 1: Generate a TED Talk
    print("\nGenerating TED Talk...")
    
    talk_brief = TalkBrief(
        topic="The Future of Artificial Intelligence",
        key_points=[
            "Current capabilities and limitations",
            "Near-term practical applications",
            "Long-term societal implications",
            "Ethical considerations and safeguards"
        ],
        target_audience="Tech enthusiasts and decision makers",
        duration_minutes=18,
        max_words=2250,
        language="en"
    )
    
    try:
        talk_result = await generate_ted_talk(talk_brief)
        print(f"TED Talk Generated!")
        print(f"   - Word count: {talk_result['word_count']}")
        print(f"   - Revisions: {talk_result['revisions']}")
        print(f"   - Score: {talk_result['critique_score']}")
        print(f"\n📄 Preview (first 500 chars):")
        print(talk_result['talk'][:500] + "..." if talk_result['talk'] else "No content generated")
    except Exception as e:
        print(f"Error generating TED talk: {e}")
    
    # Example 2: Generate a Podcast
    print("\n\nGenerating Podcast...")
    
    podcast_query = PodcastQuery(
        topic="The Psychology of Decision Making in Business",
        num_segments=4,
        target_duration_minutes=30,
        language="en",
        speakers=["host", "expert"]
    )
    
    try:
        podcast_result = await generate_podcast(podcast_query)
        print(f"Podcast Generated!")
        print(f"   - Segments: {len(podcast_result['segments'])}")
        print(f"   - Total word count: {podcast_result['word_count']}")
        print(f"   - Revisions: {podcast_result['revisions']}")
        print(f"   - Score: {podcast_result['critique_score']}")
        print(f"\nPreview (first 500 chars):")
        print(podcast_result['script'][:500] + "..." if podcast_result['script'] else "No content generated")
    except Exception as e:
        print(f"Error generating podcast: {e}")


if __name__ == "__main__":
    asyncio.run(main())
