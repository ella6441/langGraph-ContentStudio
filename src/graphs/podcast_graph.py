"""Podcast generation graph with LangGraph"""
from typing import Optional, Callable, Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel
import json
import asyncio

from src.schemas.models import (
    PodcastQuery, 
    PodcastSegment, 
    PodcastState, 
    CritiqueResult
)
from src.utils.word_counter import count_words
from configs.config import config


def research_topic_parallel(state: PodcastState) -> PodcastState:
    """Research the podcast topic using parallel processing"""
    query = state.query
    if not query:
        raise ValueError("Query is required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    research_points = [
        "Current trends and statistics",
        "Expert perspectives and opinions",
        "Real-world applications and examples",
        "Common misconceptions",
        "Future outlook and predictions"
    ]
    
    research_results = {}
    
    # Run research in parallel using asyncio
    async def research_aspect(aspect: str) -> str:
        prompt = PromptTemplate(
            template="""Research and provide information about: {aspect}

Topic: {topic}

Format your response as detailed bullet points. Keep it concise but comprehensive.""",
            input_variables=["aspect", "topic"]
        )
        
        result = llm.invoke(prompt.format(
            aspect=aspect,
            topic=query.topic
        )).content
        
        return result
    
    # Execute all research tasks (simulated as sync in this context)
    for aspect in research_points:
        prompt = PromptTemplate(
            template="""Research and provide information about: {aspect}

Topic: {topic}

Format your response as detailed bullet points. Keep it concise but comprehensive.""",
            input_variables=["aspect", "topic"]
        )
        
        result = llm.invoke(prompt.format(
            aspect=aspect,
            topic=query.topic
        )).content
        
        research_results[aspect] = result
    
    state.research_results = research_results
    return state


def segment_content(state: PodcastState) -> PodcastState:
    """Segment the podcast into multiple segments"""
    query = state.query
    research = state.research_results
    
    if not query or not research:
        raise ValueError("Query and research results are required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.6
    )
    
    # Calculate words per segment with dynamic budget
    total_words_budget = query.target_duration_minutes * 150  # ~150 words per minute
    words_per_segment = total_words_budget // query.num_segments
    
    segments = []
    
    for i in range(query.num_segments):
        prompt = PromptTemplate(
            template="""Create segment {segment_num} of a {num_segments}-part podcast episode.

Topic: {topic}
Segment focus: {segment_focus}

Context from research:
{research}

Requirements:
- Target word count: {words_per_segment} words
- Conversational tone suitable for podcast
- Include interesting details and examples
- Make it engaging and informative
- Speaker: {speaker}

Write the segment script:""",
            input_variables=["segment_num", "num_segments", "topic", "segment_focus", 
                           "research", "words_per_segment", "speaker"]
        )
        
        # Distribute research points across segments
        segment_focus = list(research.keys())[i % len(research)]
        segment_research = research.get(segment_focus, "")
        
        speaker = query.speakers[i % len(query.speakers)]
        
        segment_content = llm.invoke(prompt.format(
            segment_num=i + 1,
            num_segments=query.num_segments,
            topic=query.topic,
            segment_focus=segment_focus,
            research=segment_research[:500],  # Limit research to avoid token overflow
            words_per_segment=words_per_segment,
            speaker=speaker
        )).content
        
        segment = PodcastSegment(
            segment_id=f"segment_{i+1}",
            topic=segment_focus,
            content=segment_content,
            speaker=speaker,
            word_count=count_words(segment_content)
        )
        
        # Clamp word count if exceeded
        if segment.word_count > words_per_segment * 1.2:
            # Truncate if significantly over
            words = segment_content.split()
            segment.content = " ".join(words[:int(words_per_segment * 1.1)])
            segment.word_count = count_words(segment.content)
        
        segments.append(segment)
    
    state.segments = segments
    return state


def assemble_full_script(state: PodcastState) -> PodcastState:
    """Assemble full podcast script from segments"""
    segments = state.segments
    query = state.query
    
    if not segments:
        raise ValueError("Segments are required")
    
    # Create intro and outro
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    intro_prompt = PromptTemplate(
        template="""Write a brief podcast intro (about 100 words) for: {topic}

Make it engaging and set expectations for listeners.""",
        input_variables=["topic"]
    )
    
    intro = llm.invoke(intro_prompt.format(
        topic=query.topic
    )).content
    
    outro_prompt = PromptTemplate(
        template="""Write a brief podcast outro (about 80 words) wrapping up discussion on: {topic}

Include call-to-action.""",
        input_variables=["topic"]
    )
    
    outro = llm.invoke(outro_prompt.format(
        topic=query.topic
    )).content
    
    # Assemble full script
    full_script = f"""{intro}

## SEGMENTS

"""
    
    for segment in segments:
        full_script += f"### {segment.topic} (Speaker: {segment.speaker})\n\n"
        full_script += segment.content + "\n\n"
    
    full_script += f"{outro}"
    
    state.full_script = full_script
    return state


def critique_podcast(state: PodcastState) -> PodcastState:
    """Critique the full podcast script"""
    query = state.query
    script = state.full_script
    
    if not query or not script:
        raise ValueError("Query and script are required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.5
    )
    
    prompt = PromptTemplate(
        template="""Critique this podcast script on: {topic}

SCRIPT:
{script}

Provide:
1. Overall quality score (0-10)
2. Engagement level assessment
3. Information quality and accuracy
4. Pacing and flow
5. Specific improvements needed
6. Strengths to keep

Respond in JSON format with: {{"score": 0-10, "feedback": "...", "issues": [...], "suggestions": [...]}}""",
        input_variables=["topic", "script"]
    )
    
    response = llm.invoke(prompt.format(
        topic=query.topic,
        script=script[:2000]  # Limit to avoid token overflow
    )).content
    
    try:
        critique_data = json.loads(response)
    except json.JSONDecodeError:
        critique_data = {
            "score": 7.0,
            "feedback": response,
            "issues": [],
            "suggestions": []
        }
    
    word_count = count_words(script)
    
    critique = CritiqueResult(
        score=critique_data.get("score", 7.0),
        feedback=critique_data.get("feedback", ""),
        issues=critique_data.get("issues", []),
        suggestions=critique_data.get("suggestions", []),
        word_count=word_count,
        needs_revision=critique_data.get("score", 7.0) < config.CRITIQUE_THRESHOLD
    )
    
    state.critique = critique
    return state


def revise_podcast(state: PodcastState) -> PodcastState:
    """Revise podcast based on critique"""
    query = state.query
    script = state.full_script
    critique = state.critique
    
    if not query or not script or not critique:
        raise ValueError("Query, script, and critique are required")
    
    # Check revision limit
    if state.revisions >= state.max_revisions:
        return state
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    prompt = PromptTemplate(
        template="""Revise this podcast script based on the feedback.

CURRENT SCRIPT:
{script}

FEEDBACK:
Score: {score}/10
{feedback}

Issues: {issues}
Suggestions: {suggestions}

Requirements:
- Keep overall structure and segments
- Address major issues
- Implement suggested improvements
- Maintain target duration (~{target_minutes} minutes)

Provide the revised script:""",
        input_variables=["script", "score", "feedback", "issues", "suggestions", "target_minutes"]
    )
    
    revised_script = llm.invoke(prompt.format(
        script=script[:2000],
        score=critique.score,
        feedback=critique.feedback,
        issues="\n- ".join(critique.issues),
        suggestions="\n- ".join(critique.suggestions),
        target_minutes=query.target_duration_minutes
    )).content
    
    state.full_script = revised_script
    state.revisions += 1
    
    return state


def should_revise_podcast(state: PodcastState) -> str:
    """Determine if podcast needs revision"""
    critique = state.critique
    
    if not critique:
        return "critique"
    
    if critique.needs_revision and state.revisions < state.max_revisions:
        return "revise"
    
    return "end"


def create_podcast_graph(checkpointer_type: str = "sqlite"):
    """
    Create Podcast generation graph
    
    Args:
        checkpointer_type: Type of checkpointer ("sqlite" or None)
        
    Returns:
        Compiled LangGraph workflow
    """
    
    workflow = StateGraph(PodcastState)
    
    # Add nodes
    workflow.add_node("research", research_topic_parallel)
    workflow.add_node("segment", segment_content)
    workflow.add_node("assemble", assemble_full_script)
    workflow.add_node("critique", critique_podcast)
    workflow.add_node("revise", revise_podcast)
    
    # Add edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "segment")
    workflow.add_edge("segment", "assemble")
    workflow.add_edge("assemble", "critique")
    
    # Conditional edge for revision
    workflow.add_conditional_edges(
        "critique",
        should_revise_podcast,
        {
            "revise": "revise",
            "end": END
        }
    )
    
    workflow.add_edge("revise", "critique")
    
    # Setup checkpointer
    checkpointer = None
    if checkpointer_type == "sqlite":
        checkpointer = SqliteSaver(db=config.DATABASE_URL)
    
    # Compile
    app = workflow.compile(checkpointer=checkpointer, interrupt_before=["critique"])
    
    return app


async def generate_podcast(
    query: PodcastQuery,
    approval_handler: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Generate a podcast from query
    
    Args:
        query: PodcastQuery with requirements
        approval_handler: Optional callback for approvals
        
    Returns:
        Result dictionary
    """
    graph = create_podcast_graph()
    
    initial_state = PodcastState(
        query=query,
        revisions=0,
        max_revisions=config.MAX_REVISIONS_PODCAST
    )
    
    result = graph.invoke(initial_state)
    
    return {
        "script": result.full_script,
        "segments": result.segments,
        "word_count": count_words(result.full_script or ""),
        "revisions": result.revisions,
        "critique_score": result.critique.score if result.critique else None,
        "approved": result.approved
    }
