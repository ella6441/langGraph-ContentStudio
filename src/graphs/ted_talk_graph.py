"""TED Talk generation graph with LangGraph"""
from typing import Optional, Callable, Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import json

from src.schemas.models import TalkBrief, CritiqueResult, TalkState
from src.utils.word_counter import count_words, enforce_word_limit
from configs.config import config


# Define node functions
def plan_talk(state: TalkState) -> TalkState:
    """Create initial plan for the talk"""
    brief = state.brief
    if not brief:
        raise ValueError("Brief is required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    prompt = PromptTemplate(
        template="""Create a detailed outline for a {duration} minute TED talk on: {topic}

Target audience: {audience}
Key points to cover: {key_points}

Provide:
1. Hook/Opening (30-60 seconds)
2. Introduction of the problem (2-3 minutes)
3. Key insights or solutions (10-12 minutes)
4. Real-world examples (3-5 minutes)
5. Call to action/Conclusion (1-2 minutes)

Be specific and actionable. Target word count: ~{max_words} words.""",
        input_variables=["duration", "topic", "audience", "key_points", "max_words"]
    )
    
    plan_text = llm.invoke(prompt.format(
        duration=brief.duration_minutes,
        topic=brief.topic,
        audience=brief.target_audience,
        key_points="\n- ".join(brief.key_points),
        max_words=brief.max_words
    )).content
    
    state.context = plan_text
    return state


def gather_context(state: TalkState) -> TalkState:
    """Gather research and context information"""
    brief = state.brief
    if not brief:
        raise ValueError("Brief is required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    prompt = PromptTemplate(
        template="""Research and provide context for a talk on: {topic}

Provide:
1. Current state of the field/topic
2. Key statistics and data points
3. Recent developments or breakthroughs
4. Common misconceptions
5. Expert perspectives
6. Practical implications for the audience

Keep this concise but informative.""",
        input_variables=["topic"]
    )
    
    context = llm.invoke(prompt.format(
        topic=brief.topic
    )).content
    
    # Append to existing context
    state.context = (state.context or "") + "\n\n" + context
    return state


def write_talk(state: TalkState) -> TalkState:
    """Write the complete TED talk script"""
    brief = state.brief
    context = state.context
    
    if not brief or not context:
        raise ValueError("Brief and context are required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    prompt = PromptTemplate(
        template="""Using the following outline and context, write a complete TED talk script.

OUTLINE:
{outline}

CONTEXT:
{context}

Requirements:
- Target word count: {max_words} words (enforce this strictly)
- Conversational, engaging tone
- Include storytelling elements
- Clear transitions between sections
- Include pause markers [PAUSE] for emphasis
- Make it memorable and impactful

Write the complete talk now:""",
        input_variables=["outline", "context", "max_words"]
    )
    
    talk_text = llm.invoke(prompt.format(
        outline=state.context[:2000],  # Use first part as outline
        context=state.context,
        max_words=brief.max_words
    )).content
    
    # Enforce word limit
    talk_text = enforce_word_limit(talk_text, brief.max_words, mode="truncate")
    
    state.initial_talk = talk_text
    return state


def critique_script(state: TalkState) -> TalkState:
    """Critique the talk script"""
    brief = state.brief
    talk = state.initial_talk
    
    if not brief or not talk:
        raise ValueError("Brief and talk are required")
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.5
    )
    
    prompt = PromptTemplate(
        template="""Critique this TED talk script on: {topic}

SCRIPT:
{script}

Provide:
1. Overall quality score (0-10)
2. Specific strengths
3. Areas for improvement
4. Any factual or logical issues
5. Suggestions for making it more engaging
6. Pacing and flow assessment

Respond in JSON format with: {{"score": 0-10, "feedback": "...", "issues": [...], "suggestions": [...]}}""",
        input_variables=["topic", "script"]
    )
    
    response = llm.invoke(prompt.format(
        topic=brief.topic,
        script=talk
    )).content
    
    # Parse JSON response
    try:
        critique_data = json.loads(response)
    except json.JSONDecodeError:
        # Fallback if model doesn't return valid JSON
        critique_data = {
            "score": 7.0,
            "feedback": response,
            "issues": [],
            "suggestions": []
        }
    
    word_count = count_words(talk)
    
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


def revise_talk(state: TalkState) -> TalkState:
    """Revise the talk based on feedback"""
    brief = state.brief
    talk = state.initial_talk
    critique = state.critique
    
    if not brief or not talk or not critique:
        raise ValueError("Brief, talk, and critique are required")
    
    # Check revision limit
    if state.revisions >= state.max_revisions:
        state.final_talk = talk
        return state
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.7
    )
    
    prompt = PromptTemplate(
        template="""Revise this TED talk script based on the feedback provided.

CURRENT SCRIPT:
{script}

FEEDBACK:
Score: {score}/10
{feedback}

Issues:
{issues}

Suggestions:
{suggestions}

Requirements:
- Keep word count around {max_words} words
- Address all major issues mentioned
- Maintain the original structure and key points
- Make the suggested improvements
- Keep the conversational tone

Provide the revised script:""",
        input_variables=["script", "score", "feedback", "issues", "suggestions", "max_words"]
    )
    
    revised_talk = llm.invoke(prompt.format(
        script=talk,
        score=critique.score,
        feedback=critique.feedback,
        issues="\n- ".join(critique.issues),
        suggestions="\n- ".join(critique.suggestions),
        max_words=brief.max_words
    )).content
    
    # Enforce word limit
    revised_talk = enforce_word_limit(revised_talk, brief.max_words, mode="truncate")
    
    state.initial_talk = revised_talk
    state.revisions += 1
    
    return state


def should_revise(state: TalkState) -> str:
    """Determine if talk needs revision"""
    critique = state.critique
    
    if not critique:
        return "critique"
    
    # If score is below threshold and we haven't exceeded revision limit
    if critique.needs_revision and state.revisions < state.max_revisions:
        return "revise"
    
    # If score is acceptable, move to approval
    state.final_talk = state.initial_talk
    return "end"


def create_ted_talk_graph(
    approval_handler: Optional[Callable] = None
):
    """
    Create TED Talk generation graph
    
    Args:
        approval_handler: Optional callback for human approval
        
    Returns:
        Compiled LangGraph workflow
    """
    
    # Create state graph
    workflow = StateGraph(TalkState)
    
    # Add nodes
    workflow.add_node("plan", plan_talk)
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("write", write_talk)
    workflow.add_node("critique", critique_script)
    workflow.add_node("revise", revise_talk)
    
    # Add edges (linear flow with loop back)
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "gather_context")
    workflow.add_edge("gather_context", "write")
    workflow.add_edge("write", "critique")
    
    # Conditional edge for revision loop
    workflow.add_conditional_edges(
        "critique",
        should_revise,
        {
            "revise": "revise",
            "end": END
        }
    )
    
    # Revise loops back to critique
    workflow.add_edge("revise", "critique")
    
    # Compile graph without persistent checkpointing
    # Checkpointing can be added with langgraph.checkpoint once stable version confirmed
    app = workflow.compile(interrupt_before=["critique"])
    
    return app


# Convenience function to run the graph
async def generate_ted_talk(
    brief: TalkBrief,
    approval_handler: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Generate a TED talk from brief
    
    Args:
        brief: TalkBrief with requirements
        approval_handler: Optional callback for approvals
        
    Returns:
        Result dictionary with generated talk
    """
    graph = create_ted_talk_graph()
    
    initial_state = TalkState(
        brief=brief,
        revisions=0,
        max_revisions=config.MAX_REVISIONS_TED
    )
    
    result = graph.invoke(initial_state)
    
    return {
        "talk": result.final_talk,
        "word_count": count_words(result.final_talk or ""),
        "revisions": result.revisions,
        "critique_score": result.critique.score if result.critique else None,
        "approved": result.approved
    }
