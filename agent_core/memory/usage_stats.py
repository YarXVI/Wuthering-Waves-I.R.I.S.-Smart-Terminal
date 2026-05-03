"""
API 用量统计 — 追踪 Token 使用量和 API 调用
"""

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "memory" / "usage"
BASE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class UsageRecord:
    agent_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    latency_ms: int
    timestamp: str

def _today_file() -> Path:
    return BASE_DIR / f"{date.today().isoformat()}.json"

def _ensure_dir():
    BASE_DIR.mkdir(parents=True, exist_ok=True)

def record_usage(
    agent_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    cost: float = 0.0
) -> bool:
    """记录一次 API 调用"""
    _ensure_dir()
    record = UsageRecord(
        agent_id=agent_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        cost=cost,
        latency_ms=latency_ms,
        timestamp=datetime.now().isoformat(),
    )
    path = _today_file()
    try:
        data = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, Exception):
                data = []
        data.append(asdict(record))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except (OSError, Exception):
        return False

def get_daily_usage(day: Optional[date] = None) -> dict:
    """获取指定日期的用量统计"""
    if day is None:
        day = date.today()
    path = BASE_DIR / f"{day.isoformat()}.json"
    if not path.exists():
        return {
            "date": day.isoformat(),
            "total_requests": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency_ms": 0,
            "by_agent": {},
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        total_prompt = sum(r["prompt_tokens"] for r in data)
        total_completion = sum(r["completion_tokens"] for r in data)
        total_cost = sum(r["cost"] for r in data)
        total_latency = sum(r["latency_ms"] for r in data)

        by_agent: dict[str, dict] = {}
        for r in data:
            aid = r["agent_id"]
            if aid not in by_agent:
                by_agent[aid] = {
                    "requests": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                }
            by_agent[aid]["requests"] += 1
            by_agent[aid]["prompt_tokens"] += r["prompt_tokens"]
            by_agent[aid]["completion_tokens"] += r["completion_tokens"]
            by_agent[aid]["total_tokens"] += r["total_tokens"]
            by_agent[aid]["cost"] += r["cost"]

        return {
            "date": day.isoformat(),
            "total_requests": len(data),
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
            "total_cost": round(total_cost, 6),
            "avg_latency_ms": int(total_latency / len(data)) if data else 0,
            "by_agent": by_agent,
        }
    except (json.JSONDecodeError, Exception):
        return {
            "date": day.isoformat(),
            "total_requests": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency_ms": 0,
            "by_agent": {},
        }

def get_recent_days(days: int = 7) -> list[dict]:
    """获取最近 N 天的用量统计"""
    result = []
    today = date.today()
    for i in range(days):
        day = today - timedelta(days=i)
        stat = get_daily_usage(day)
        result.append(stat)
    return result