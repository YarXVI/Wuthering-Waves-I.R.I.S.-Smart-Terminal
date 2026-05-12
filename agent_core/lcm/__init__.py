"""
IRIS LCM Integration - 惰性上下文物化协议 v2 集成层

为 IRIS 框架提供统一的 LCM v2 访问接口，兼容旧版调用方式。
"""

from prompt_experiment.lcm_v2 import (
    # 核心类型
    ContextChunk,
    LCMEvent,
    LoadRequest,
    LCMSession,
    LCMState,
    ChunkLoadReason,
    SentinelPattern,
    LCMMetrics,
    # 核心组件
    ChunkStoreV2,
    SentinelDetectorV2,
    LCMOrchestratorV2,
    LCMClientV2,
    build_initial_messages_v2,
    # Token 预算
    TokenBudget,
    # Chunk 依赖图
    ChunkGraph,
    # 混合模式
    HybridChunkManager,
    HybridConfig,
    build_hybrid_messages,
    # Provider 路由
    ProviderRouter,
    ProviderConfig,
    ProviderType,
    RoutingStrategy,
    # KV Cache
    KVCacheManager,
    # 日志
    get_logger,
)

# 保持旧版接口兼容
ChunkStore = ChunkStoreV2
SentinelDetector = SentinelDetectorV2
LCMOrchestrator = LCMOrchestratorV2
LCMClient = LCMClientV2
build_initial_messages = build_initial_messages_v2

# IRIS 适配器
from .adapter import IRISLCMStore, IRISLCMClient, IRISLCMSessionManager

__all__ = [
    # 类型
    "ContextChunk",
    "LCMEvent",
    "LoadRequest",
    "LCMSession",
    "LCMState",
    "ChunkLoadReason",
    "SentinelPattern",
    "LCMMetrics",
    # 组件
    "ChunkStore",
    "ChunkStoreV2",
    "SentinelDetector",
    "SentinelDetectorV2",
    "LCMOrchestrator",
    "LCMOrchestratorV2",
    "LCMClient",
    "LCMClientV2",
    "build_initial_messages",
    "build_initial_messages_v2",
    # 工具
    "TokenBudget",
    "ChunkGraph",
    "HybridChunkManager",
    "HybridConfig",
    "build_hybrid_messages",
    "ProviderRouter",
    "ProviderConfig",
    "ProviderType",
    "RoutingStrategy",
    "KVCacheManager",
    "get_logger",
    # IRIS 适配器
    "IRISLCMStore",
    "IRISLCMClient",
    "IRISLCMSessionManager",
]
