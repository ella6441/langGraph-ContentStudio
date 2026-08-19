"""Example: Generate a complete TED talk with audio"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas.models import TalkBrief
from src.graphs.ted_talk_graph import generate_ted_talk
from src.graphs.audio_graph import generate_audio_from_script


async def main():
    """Generate TED talk with audio"""
    
    print("🎯 Complete TED Talk Generation Pipeline")
    print("=" * 50)
    
    # Step 1: Create brief
    brief = TalkBrief(
        topic="Building Sustainable Technology for the Future",
        key_points=[
            "Environmental impact of tech",
            "Green computing principles",
            "Solar-powered data centers",
            "Carbon-neutral digital infrastructure"
        ],
        target_audience="Technology leaders and sustainability advocates",
        duration_minutes=18
    )
    
    print(f"\n📝 Brief: {brief.topic}")
    print(f"Maximum words: {brief.max_words}")
    
    # Step 2: Generate talk
    print("\n⏳ Generating talk...")
    talk_result = await generate_ted_talk(brief)
    
    print(f"✅ Talk generated!")
    print(f"   Word count: {talk_result['word_count']}")
    print(f"   Quality score: {talk_result['critique_score']}/10")
    print(f"   Revisions needed: {talk_result['revisions']}")
    
    # Step 3: Generate audio
    print("\n⏳ Generating audio...")
    try:
        audio_result = await generate_audio_from_script(
            script=talk_result['talk'],
            output_dir="./output/ted_talk"
        )
        
        print(f"✅ Audio generated!")
        print(f"   File: {audio_result.audio_path}")
        print(f"   Duration: {audio_result.duration_seconds:.0f} seconds")
        print(f"   Size: {audio_result.size_mb} MB")
    
    except Exception as e:
        print(f"⚠️  Audio generation skipped: {e}")
    
    # Save script
    output_dir = Path("./output/ted_talk")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "script.txt", "w", encoding="utf-8") as f:
        f.write(talk_result['talk'])
    
    print(f"\n📄 Script saved to output/ted_talk/script.txt")
    print("\n✨ Pipeline complete!")


if __name__ == "__main__":
    asyncio.run(main())
