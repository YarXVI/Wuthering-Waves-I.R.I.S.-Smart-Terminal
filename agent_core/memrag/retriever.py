"""
Retriever - Hybrid retrieval: semantic vectors + keywords + recent context
"""

from agent_core.memrag.config import memrag_config
from agent_core.memrag.memory_indexer import indexer
from agent_core.memory.session_store import load_session
from agent_core.memory.memory_store import search_memories


def retrieve(agent_id: str, query: str) -> dict:
    """
    Execute hybrid retrieval for specified Agent

    Returns:
        {
            "memories": [...],       # Semantic/keyword retrieved memory entries
            "recent_context": "...",  # Last N rounds of dialogue summary
            "total": int,
        }
    """
    top_k = memrag_config.top_k
    memories = []

    # 1. Vector/keyword search in memory store
    vec_results = indexer.search(query, agent_id, top_k=top_k)
    for r in vec_results:
        memories.append({
            "source": "memrag_index",
            "type": r["type"],
            "content": r["text"],
            "score": "vector",
        })

    # 2. Keyword search in memory_store (supplementary)
    kw_results = search_memories(query, limit=top_k)
    seen_texts = {m["content"] for m in memories}
    for r in kw_results:
        if r.get("content") not in seen_texts and len(memories) < top_k:
            memories.append({
                "source": "memory_store",
                "type": r.get("type", "note"),
                "content": r["content"],
                "score": "keyword",
            })
            seen_texts.add(r["content"])

    # 3. Recent dialogue context (extracted from session)
    recent_context = ""
    session = load_session(agent_id)
    if session and session.get("messages"):
        # Get last 3 exchanges
        msgs = session["messages"]
        recent = msgs[-6:] if len(msgs) > 6 else msgs
        lines = []
        for m in recent:
            role = "User" if m["role"] == "user" else "Assistant"
            text = m["content"][:200]
            lines.append(f"{role}: {text}")
        recent_context = "\n".join(lines)

    # Truncate total character count
    total_chars = sum(len(m["content"]) for m in memories)
    if total_chars > memrag_config.max_memory_chars:
        # Truncate from end
        truncated = []
        chars = 0
        for m in memories:
            if chars + len(m["content"]) <= memrag_config.max_memory_chars:
                truncated.append(m)
                chars += len(m["content"])
            else:
                break
        memories = truncated

    return {
        "memories": memories,
        "recent_context": recent_context,
        "total": len(memories),
    }
