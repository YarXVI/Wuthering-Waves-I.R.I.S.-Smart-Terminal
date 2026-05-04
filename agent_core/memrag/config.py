"""
MemRAG Configuration
"""

from dataclasses import dataclass, field


@dataclass
class MemRAGConfig:
    """MemRAG module configuration"""

    # Main switch
    enabled: bool = False

    # Retrieval parameters
    top_k: int = 3              # Number of memory entries to retrieve each time
    min_score: float = 0.3      # Minimum similarity threshold

    # Context injection
    max_memory_chars: int = 1500  # Maximum characters to inject

    # Embedding configuration
    embedding_model: str = "text-embedding-ada-002"  # Model name
    embedding_dim: int = 256                            # Vector dimension

    # Statistics
    total_retrievals: int = 0
    total_injections: int = 0


# Global singleton
memrag_config = MemRAGConfig()
