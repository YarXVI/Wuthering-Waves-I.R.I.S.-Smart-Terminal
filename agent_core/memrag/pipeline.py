"""
MemRAG Pipeline - Memory Enhanced RAG Pipeline
"""
import uuid

from agent_core.memrag.config import memrag_config
from agent_core.memrag.retriever import retrieve
from agent_core.memrag.memory_indexer import indexer


def is_embedding_available() -> bool:
    """Check if embedding is available"""
    return False


class MemRAGPipeline:
    """Lightweight MemRAG pipeline"""

    def __init__(self):
        self._embedding_available: bool | None = None

    @property
    def embedding_available(self) -> bool:
        if self._embedding_available is None:
            self._embedding_available = is_embedding_available()
        return self._embedding_available

    def enrich_prompt(self, agent_id: str, user_message: str, 
                      base_system_prompt: str) -> str:
        """
        Enrich system prompt with retrieved memories
        
        Args:
            agent_id: Current Agent ID
            user_message: User's current input
            base_system_prompt: Original system prompt
            
        Returns:
            Enriched system prompt (with memory context)
        """
        if not memrag_config.enabled:
            return base_system_prompt

        result = retrieve(agent_id, user_message)
        memrag_config.total_retrievals += 1

        if result["total"] == 0 and not result["recent_context"]:
            return base_system_prompt

        context_parts = []
        
        if result["memories"]:
            context_parts.append("## Relevant Memories")
            for i, m in enumerate(result["memories"], 1):
                context_parts.append(f"{i}. [{m['type']}] {m['content']}")
        
        if result["recent_context"]:
            context_parts.append("## Recent Conversation")
            context_parts.append(result["recent_context"])

        memory_context = "\n".join(context_parts)
        memrag_config.total_injections += 1

        enriched = f"""{base_system_prompt}

## Memory Context

Below are historical memories and recent conversations related to you, please answer questions accordingly:

{memory_context}"""
        return enriched

    def index_interaction(self, agent_id: str, user_msg: str, 
                          assistant_reply: str, session_id: str = "") -> None:
        """
        Index a complete interaction for future retrieval
        """
        if not memrag_config.enabled:
            return

        interaction_id = session_id or str(uuid.uuid4())[:8]

        user_memory_id = f"{agent_id}_user_{interaction_id}"
        indexer.add(user_memory_id, agent_id, user_msg, "interaction")

        reply_preview = assistant_reply[:500]
        reply_memory_id = f"{agent_id}_reply_{interaction_id}"
        indexer.add(reply_memory_id, agent_id, reply_preview, "response")


# Global singleton
pipeline = MemRAGPipeline()
