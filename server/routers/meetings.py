"""
Router: Smart Meeting Room
Topic matching, multi-round discussion, consensus judgment, background meeting
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from server.ws_manager import manager as ws_manager
import asyncio
from agent_core.project_room.meeting import (
    create_meeting,
    delete_meeting,
    execute_round,
    judge_consensus,
    save_meeting,
    load_meeting,
    list_meetings,
    terminate_meeting,
    auto_discuss,
    summarize_meeting,
    search_meetings,
    list_templates,
    export_meeting_markdown,
    update_template,
    delete_template,
    get_meeting_stats,
)
from agent_core.project_room.meeting_models import MeetingSession
from agent_core.project_room.meeting_discussion import _get_agent_name, _write_to_whiteboard
from agent_core.project_room.meeting_templates import create_template, create_from_template
from agent_core.core.agent_manager import manager

router = APIRouter()


class SuggestRequest(BaseModel):
    topic: str


class StartMeetingRequest(BaseModel):
    topic: str
    agents: list[str] = []


class CreateTemplateRequest(BaseModel):
    name: str
    description: str
    suggested_agents: list[str]
    default_rounds: int = 6


class UpdateTemplateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    suggested_agents: list[str] | None = None
    default_rounds: int | None = None


@router.post("/meetings/suggest-agents")
def suggest_agents(req: SuggestRequest):
    """Suggest appropriate Agent list for meeting topic (excluding iris)"""
    topic = req.topic.strip()
    if not topic:
        return {"suggested": [], "reasoning": "Topic is empty"}
    candidates = []
    for aid, profile in manager.profiles.items():
        if aid == "iris":
            continue
        specialty = profile.specialty if hasattr(profile, 'specialty') else ""
        candidates.append(f"- {profile.name}({aid}): {specialty}")
    if not candidates:
        return {"suggested": [], "reasoning": "No colleagues available"}
    candidates_text = "\n".join(candidates)
    prompt = (
        f"You are a project coordinator, select the most suitable colleagues for the meeting.\n\n"
        f"## Topic\n{topic}\n\n"
        f"## Available colleagues and specialties\n{candidates_text}\n\n"
        f"Please select 1-3 most relevant colleagues based on topic and specialty relevance.\n"
        f"Note: You (iris) automatically attend all meetings.\n\n"
        f"Respond in JSON format only:\n"
        f'{{"suggested": ["agent_id1", "agent_id2"], "reasoning": "selection reason"}}'
    )
    from agent_core.project_room.meeting_discussion import _call_agent_llm
    content, _ = _call_agent_llm("iris", prompt, temperature=0.1)
    import json, re
    try:
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(content)
    except (json.JSONDecodeError, Exception):
        result = {"suggested": [], "reasoning": "System analysis failed, please select manually"}
    result["suggested"] = [a for a in result.get("suggested", []) if manager.get_profile(a)]
    return result


@router.post("/meetings/start")
async def start_meeting(req: StartMeetingRequest):
    """Create new meeting with specified topic and agents"""
    topic = req.topic.strip() or "(No topic)"
    agents = req.agents or []
    agents = list(dict.fromkeys(agents))
    meeting = create_meeting(topic, agents)
    await ws_manager.broadcast(meeting.room_id, {
        "type": "meeting_created",
        "room_id": meeting.room_id,
        "topic": meeting.topic,
        "status": meeting.status,
    })
    return {
        "room_id": meeting.room_id,
        "topic": meeting.topic,
        "agents": ["iris"] + meeting.agents,
        "status": meeting.status,
    }


@router.get("/meetings")
def list_all_meetings():
    """List all meetings"""
    return {"meetings": list_meetings()}


@router.get("/meetings/templates")
def list_meeting_templates():
    """List all meeting templates"""
    return {"templates": list_templates()}


@router.post("/meetings/templates")
def create_meeting_template(req: CreateTemplateRequest):
    """Create new template"""
    tpl = create_template(req.name, req.description, req.suggested_agents, req.default_rounds)
    return {"template": tpl}


@router.patch("/meetings/templates/{template_id}")
def update_meeting_template(template_id: str, req: UpdateTemplateRequest):
    """Update template"""
    tpl = update_template(template_id, req.name, req.description, req.suggested_agents, req.default_rounds)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"template": tpl}


@router.delete("/meetings/templates/{template_id}")
def delete_meeting_template(template_id: str):
    """Delete template"""
    success = delete_template(template_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete default template or template not found")
    return {"success": True}


class TemplateMeetingRequest(BaseModel):
    template_id: str
    topic: str
    agents: list[str] = []


@router.post("/meetings/from-template")
def start_from_template(req: TemplateMeetingRequest):
    """Create meeting from template"""
    try:
        meeting = create_from_template(req.template_id, req.topic, req.agents or None)
        return {
            "room_id": meeting.room_id,
            "topic": meeting.topic,
            "agents": ["iris"] + meeting.agents,
            "status": meeting.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/meetings/search")
def search_all_meetings(q: str = ""):
    """Search meetings by topic and discussion content"""
    return {"meetings": search_meetings(q)}


class AdvancedSearchRequest(BaseModel):
    q: str = ""
    status: str = ""
    consensus: bool | None = None
    date_from: str = ""
    date_to: str = ""
    agent: str = ""


@router.post("/meetings/advanced-search")
def advanced_search_meetings(req: AdvancedSearchRequest):
    """Advanced search with multi-dimensional filtering"""
    from datetime import datetime
    meetings = list_meetings()
    results = []
    for m in meetings:
        if req.q:
            topic = m.get("topic", "").lower()
            if req.q.lower() not in topic:
                continue
        if req.status and m.get("status") != req.status:
            continue
        if req.consensus is not None and m.get("consensus") != req.consensus:
            continue
        if req.date_from:
            try:
                dt = datetime.fromisoformat(m.get("created_at", ""))
                if dt < datetime.fromisoformat(req.date_from):
                    continue
            except:
                pass
        if req.date_to:
            try:
                dt = datetime.fromisoformat(m.get("created_at", ""))
                if dt > datetime.fromisoformat(req.date_to):
                    continue
            except:
                pass
        if req.agent:
            if req.agent not in m.get("agents", []):
                continue
        results.append(m)
    return {"meetings": results, "total": len(results)}


@router.get("/meetings/stats")
def meeting_stats():
    """Global meeting statistics"""
    return get_meeting_stats()


@router.get("/meetings/{room_id}")
def get_meeting(room_id: str):
    """Get meeting details"""
    meeting = load_meeting(room_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting.to_dict()


@router.delete("/meetings/{room_id}")
def remove_meeting(room_id: str):
    """Delete meeting record and associated whiteboard"""
    if not load_meeting(room_id):
        raise HTTPException(status_code=404, detail="Meeting not found")
    ok = delete_meeting(room_id)
    return {"status": "deleted" if ok else "partial"}


@router.post("/meetings/{room_id}/round")
async def run_round(room_id: str):
    """Execute one round of discussion"""
    round_entry = execute_round(room_id)
    if not round_entry:
        meeting = load_meeting(room_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return {"error": f"Meeting is in '{meeting.status}' status, not 'discussing'"}
    await ws_manager.broadcast(room_id, {
        "type": "round_added",
        "round": round_entry.to_dict(),
        "current_round": round_entry.round_number,
    })
    return {
        "round": round_entry.to_dict(),
        "current_round": round_entry.round_number,
    }


@router.post("/meetings/{room_id}/auto-discuss")
async def run_auto_discuss(room_id: str, max_rounds: int = 20):
    """Start auto-discuss mode where Agents decide whether to continue"""
    result = await auto_discuss(room_id, max_rounds=max_rounds)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    await ws_manager.broadcast(room_id, {
        "type": "auto_discuss_complete",
        **result,
    })
    return result


@router.post("/meetings/{room_id}/terminate")
def terminate_meeting_endpoint(room_id: str):
    """User actively terminates discussion"""
    result = terminate_meeting(room_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/meetings/{room_id}/judge")
async def run_judge(room_id: str):
    """Let iris judge if consensus has been reached"""
    result = judge_consensus(room_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    await ws_manager.broadcast(room_id, {
        "type": "judge_result",
        **result,
    })
    return result


@router.post("/meetings/{room_id}/summarize")
async def summarize_meeting_endpoint(room_id: str):
    """Generate meeting summary and end discussion"""
    result = summarize_meeting(room_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    await ws_manager.broadcast(room_id, {
        "type": "summary_generated",
        **result,
    })
    return result


@router.post("/meetings/{room_id}/sub-meeting")
def create_sub_meeting(room_id: str, initiator: str = "", issue: str = ""):
    """Create a sub-meeting from main meeting"""
    from datetime import datetime
    parent = load_meeting(room_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent meeting not found")
    if parent.parent_room:
        parent_2 = load_meeting(parent.parent_room)
        if parent_2 and parent_2.parent_room:
            raise HTTPException(status_code=400, detail="Sub-meeting nesting depth exceeded (max 2 levels)")
    now = datetime.now()
    sub_room_id = f"{room_id}_sub_{now.strftime('%H%M%S')}"
    sub = MeetingSession(
        room_id=sub_room_id,
        topic=f"[Sub-meeting] {issue or 'Discussion issue'}",
        agents=parent.agents,
        parent_room=room_id,
    )
    save_meeting(sub)
    _write_to_whiteboard(sub_room_id, "system", "note",
        f"Sub-meeting started by {_get_agent_name(initiator) if initiator else 'Someone'}\nIssue: {issue}")
    return {
        "room_id": sub_room_id,
        "parent_room": room_id,
        "topic": sub.topic,
        "status": sub.status,
    }


@router.get("/meetings/{room_id}/export")
def export_meeting(room_id: str):
    """Export meeting summary (Markdown)"""
    md = export_meeting_markdown(room_id)
    if not md:
        raise HTTPException(status_code=404, detail="Meeting not found")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=meeting-{room_id}.md"},
    )