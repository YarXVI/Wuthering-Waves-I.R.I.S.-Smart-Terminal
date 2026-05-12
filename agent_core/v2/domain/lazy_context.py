"""
Lazy Context Materialization Protocol

Lightweight shard-based context materialization.
For full LCM features (sentinels, state machine, prefetch), use LCMEngine.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum, auto
import json


class MaterializationSignal(Enum):
    """上下文物化信号类型."""
    IMMEDIATE = auto()
    ON_DEMAND = auto()
    BACKGROUND = auto()
    DEFERRED = auto()
    NEVER = auto()


@dataclass
class ContextShard:
    """上下文碎片 - 最小物化单元."""
    shard_id: str
    content: Any
    signal: MaterializationSignal = MaterializationSignal.ON_DEMAND
    priority: int = 5
    cost_estimate: int = 0
    materialized: bool = False
    metadata: dict = field(default_factory=dict)

    def materialize(self) -> str:
        if isinstance(self.content, str):
            self.materialized = True
            return self.content
        elif isinstance(self.content, dict):
            self.materialized = True
            return json.dumps(self.content, ensure_ascii=False)
        elif isinstance(self.content, list):
            self.materialized = True
            return "\n".join(str(item) for item in self.content)
        else:
            self.materialized = True
            return str(self.content)

    def dematerialize(self) -> None:
        self.materialized = False


@dataclass
class MaterializationPlan:
    """物化计划 - 定义上下文物化策略."""
    max_tokens: int = 4000
    reserve_tokens: int = 500
    strategy: str = "priority_first"
    enable_compression: bool = True
    compression_threshold: int = 1000


class LazyContextProtocol:
    """惰性上下文物化协议核心 —— v2 简化版."""

    def __init__(self, plan: Optional[MaterializationPlan] = None):
        self.plan = plan or MaterializationPlan()
        self._shards: dict[str, ContextShard] = {}
        self._hooks: dict[str, list[Callable]] = {
            "pre_materialize": [],
            "post_materialize": [],
            "on_budget_exceeded": [],
        }
        self._materialized_cache: dict[str, str] = {}
        self._total_cost: int = 0

    def register_shard(self, shard: ContextShard) -> None:
        self._shards[shard.shard_id] = shard
        if shard.signal == MaterializationSignal.IMMEDIATE:
            self._materialize_shard(shard)

    def register_hook(self, event: str, callback: Callable) -> None:
        if event in self._hooks:
            self._hooks[event].append(callback)

    def _trigger_hooks(self, event: str, *args, **kwargs) -> None:
        for hook in self._hooks.get(event, []):
            try:
                hook(*args, **kwargs)
            except Exception:
                pass

    def _materialize_shard(self, shard: ContextShard) -> str:
        self._trigger_hooks("pre_materialize", shard)
        result = shard.materialize()
        self._materialized_cache[shard.shard_id] = result
        cost = shard.cost_estimate or len(result)
        if not hasattr(shard, '_cost_counted'):
            self._total_cost += cost
            shard._cost_counted = True
        self._trigger_hooks("post_materialize", shard, result)
        return result

    def materialize(self, force_all: bool = False) -> str:
        available_budget = self.plan.max_tokens - self.plan.reserve_tokens
        materialized_parts: list[tuple[int, str]] = []

        shards = list(self._shards.values())
        if self.plan.strategy == "priority_first":
            shards.sort(key=lambda s: (-s.priority, s.cost_estimate))
        elif self.plan.strategy == "cost_first":
            shards.sort(key=lambda s: (s.cost_estimate, -s.priority))

        self._total_cost = 0
        for shard in shards:
            shard._cost_counted = False

        for shard in shards:
            if shard.signal == MaterializationSignal.NEVER and not force_all:
                continue

            if shard.shard_id in self._materialized_cache:
                content = self._materialized_cache[shard.shard_id]
            else:
                content = self._materialize_shard(shard)

            cost = shard.cost_estimate or len(content)

            if self._total_cost + cost > available_budget:
                self._trigger_hooks("on_budget_exceeded", shard, self._total_cost, available_budget)
                if self.plan.enable_compression and cost > self.plan.compression_threshold:
                    compressed = self._compress(content)
                    compressed_cost = len(compressed)
                    if self._total_cost + compressed_cost <= available_budget:
                        materialized_parts.append((shard.priority, compressed))
                        self._total_cost += compressed_cost
                continue

            materialized_parts.append((shard.priority, content))
            self._total_cost += cost

        materialized_parts.sort(key=lambda x: -x[0])
        return "\n\n".join(part[1] for part in materialized_parts)

    def _compress(self, content: str) -> str:
        lines = content.split("\n")
        if len(lines) > 10:
            return "\n".join(lines[:5] + ["..."] + lines[-5:])
        return content[:500] + "..." if len(content) > 500 else content

    def get_stats(self) -> dict:
        total = len(self._shards)
        materialized = sum(1 for s in self._shards.values() if s.materialized)
        available_budget = self.plan.max_tokens - self.plan.reserve_tokens
        return {
            "total_shards": total,
            "materialized": materialized,
            "pending": total - materialized,
            "total_cost": self._total_cost,
            "budget": available_budget,
            "budget_usage_pct": round(self._total_cost / available_budget * 100, 2) if available_budget else 0,
        }

    def reset(self) -> None:
        for shard in self._shards.values():
            shard.dematerialize()
        self._materialized_cache.clear()
        self._total_cost = 0
