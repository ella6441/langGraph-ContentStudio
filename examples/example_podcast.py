"""Example: Generate a complete podcast with audio"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas.models import PodcastQuery
from src.graphs.podcast_graph import generate_podcast
from src.graphs.audio_graph import generate_podcast_audio


async def main():
    """Generate podcast with audio"""
    
    print("🎙️  Complete Podcast Generation Pipeline")
    print("=" * 50)
    
    # Step 1: Create query
    query = PodcastQuery(
        topic="Remote Work: The New Frontier of Productivity",
        num_segments=4,
        target_duration_minutes=30,
        speakers=["host", "expert"]
    )
    
    print(f"\n📻 Topic: {query.topic}")
    print(f"Segments: {query.num_segments}")
    print(f"Target duration: {query.target_duration_minutes} minutes")
    
    # Step 2: Generate podcast
    print("\n⏳ Generating podcast...")
    podcast_result = await generate_podcast(query)
    
    print(f"✅ Podcast generated!")
    print(f"   Total words: {podcast_result['word_count']}")
    print(f"   Quality score: {podcast_result['critique_score']}/10")
    print(f"   Revisions: {podcast_result['revisions']}")
    
    # Show segment breakdown
    print(f"\n📋 Segments:")
    for i, segment in enumerate(podcast_result['segments'], 1):
        print(f"   {i}. {segment.topic} ({segment.word_count} words) - Speaker: {segment.speaker}")
    
    # Step 3: Generate audio
    print("\n⏳ Generating audio...")
    try:
        audio_result = await generate_podcast_audio(
            segments=podcast_result['segments'],
            output_dir="./output/podcast"
        )
        
        print(f"✅ Audio generated!")
        print(f"   File: {audio_result.audio_path}")
        print(f"   Duration: {audio_result.duration_seconds:.0f} seconds")
        print(f"   Size: {audio_result.size_mb} MB")
    
    except Exception as e:
        print(f"⚠️  Audio generation skipped: {e}")
    
    # Save script
    output_dir = Path("./output/podcast")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "script.txt", "w", encoding="utf-8") as f:
        f.write(podcast_result['script'])
    
    print(f"\n📄 Script saved to output/podcast/script.txt")
    print("\n✨ Pipeline complete!")


if __name__ == "__main__":
    asyncio.run(main())
