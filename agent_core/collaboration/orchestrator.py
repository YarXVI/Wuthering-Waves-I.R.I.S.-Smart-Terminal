"""
Orchestrator �?自动任务编排
将复杂任务拆解为子任务，分派给合适的 Agent，汇聚结果�?
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DelegationResult:
    """一次任务委派的结果"""
    agent_id: str
    agent_name: str
    task: str
    result: str
    success: bool = True


class Orchestrator:
    """
    任务编排�?�?自动将复合任务拆解、分派、汇总�?

    使用方式�?
        1. 分析用户请求，识别任务类�?
        2. 拆分为子任务，按能力分派给不�?Agent
        3. 收集结果，汇总给用户
    """

    def __init__(self):
        self._manager = None

    @property
    def manager(self):
        if self._manager is None:
            from agent_core.core.agent_manager import manager as m
            self._manager = m
        return self._manager

    def list_available_agents(self) -> list[dict]:
        """列出所有可用于协作�?Agent"""
        agents = self.manager.list_agents()
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "title": a["title"],
                "status": a["status"],
            }
            for a in agents
        ]

    def delegate(self, agent_id: str, task: str) -> DelegationResult:
        """
        将任务委派给指定 Agent�?

        参数:
            agent_id: 目标 Agent
            task: 要执行的任务描述

        返回:
            DelegationResult
        """
        profile = self.manager.get_profile(agent_id)
        if not profile:
            return DelegationResult(
                agent_id=agent_id,
                agent_name=agent_id,
                task=task,
                result=f"[错误] 同事 '{agent_id}' 不存�?,
                success=False,
            )

        try:
            reply = self.manager.chat(agent_id, task)
            return DelegationResult(
                agent_id=agent_id,
                agent_name=profile.name,
                task=task,
                result=reply,
                success=True,
            )
        except Exception as e:
            return DelegationResult(
                agent_id=agent_id,
                agent_name=profile.name,
                task=task,
                result=f"[错误] {str(e)[:200]}",
                success=False,
            )

    def sequential_delegate(self, delegations: list[tuple[str, str]]) -> list[DelegationResult]:
        """
        顺序委派多个任务。前一个结果可通过 {prev_result} 在后�?task 中引用�?

        参数:
            delegations: [(agent_id, task), ...]

        返回:
            [DelegationResult, ...]
        """
        results = []
        prev_result = None

        for agent_id, task in delegations:
            # 支持引用前一个结�?
            if prev_result is not None:
                task = task.replace("{prev_result}", prev_result.result[:1000])
                task = task.replace("{prev_agent}", prev_result.agent_name)

            result = self.delegate(agent_id, task)
            results.append(result)
            prev_result = result

        return results

    def compile_results(self, delegations: list[DelegationResult]) -> str:
        """
        将多个委派结果汇总为一份综合报告�?

        参数:
            delegations: 委派结果列表

        返回:
            汇总后的报告文�?
        """
        lines = ["## 协作结果汇总\n"]

        for i, d in enumerate(delegations, 1):
            status = "成功" if d.success else "失败"
            lines.append(f"### {i}. {d.agent_name}（{d.agent_id}）�?{status}")
            lines.append(f"**任务**: {d.task[:100]}{'...' if len(d.task) > 100 else ''}")
            lines.append("")
            if d.success:
                lines.append(d.result.strip())
            else:
                lines.append(f"�?出错: {d.result}")
            lines.append("")

        total_success = sum(1 for d in delegations if d.success)
        total = len(delegations)
        lines.append(f"---")
        lines.append(f"**总计**: {total_success}/{total} 个子任务完成")

        return "\n".join(lines)


# 全局单例
orchestrator = Orchestrator()
