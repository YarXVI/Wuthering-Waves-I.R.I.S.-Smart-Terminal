"""
Chinese Thinking Skill

Dual-mode Chinese reasoning support:
- ChineseThinkingSkill: standalone skill for AgentRuntime ReAct loops
- ChineseThinkEncoding: ContentEncoding plugin for LCMEngine protocol layer
Both share core prompt and configuration logic.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from agent_core.v2.infrastructure.content_encoding import (
    ContentEncoding, EncodingType, EncodingContext
)


@dataclass
class ThinkingConfig:
    """中文思考配置"""
    enable_chinese_thinking: bool = True
    thinking_language: str = "zh"  # zh, en, auto
    thinking_depth: str = "deep"  # lite, deep, dialectical
    preserve_thinking_chain: bool = True
    enable_metaphor: bool = True
    enable_dialectical: bool = True
    max_thinking_length: int = 500
    thinking_delimiter: str = "【最终回答】"


class ChineseThinkingSkill:
    """中文思考技能 - V2 原生实现

    职责：
    1. 构建中文思考提示词
    2. 提取和保留思考链
    3. 语言检测和切换
    4. 隐喻和辩证思维增强
    """

    METAPHOR_PROMPT = """## 隐喻增强

在思考过程中，使用中文特有的隐喻和类比来深化理解：
- 用自然现象比喻抽象概念（如"知识如海，学无止境"）
- 用历史典故类比当前问题
- 用生活常识解释技术原理

隐喻不是装饰，而是认知工具。"""

    DIALECTICAL_PROMPT = """## 辩证思维

采用中文辩证思维的三段式：
1. 正题：首先肯定问题的某一方面
2. 反题：然后提出对立面的考量
3. 合题：最后综合双方，提出超越性的见解

如："表面上看...然而深入思考...综合来看...""

    def __init__(self, config: Optional[ThinkingConfig] = None):
        self.config = config or ThinkingConfig()

    def build_thinking_prompt(self, user_query: str) -> str:
        """构建包含中文思考指令的提示词"""
        if not self.config.enable_chinese_thinking:
            return user_query

        parts = [
            "## 思考模式",
            "",
            f"语言: {self.config.thinking_language}",
            f"深度: {self.config.thinking_depth}",
            "",
            "### 核心原则",
            "1. 用中文进行内部推理（thinking chain）",
            "2. 分析完成后，用【最终回答】分隔符输出正式回复",
            "3. 思考过程可以是非结构化的、跳跃的、直觉式的",
            "4. 正式回复必须是结构化的、准确的、可直接使用的",
            "",
        ]

        if self.config.enable_metaphor:
            parts.extend([self.METAPHOR_PROMPT, ""])

        if self.config.enable_dialectical:
            parts.extend([self.DIALECTICAL_PROMPT, ""])

        parts.extend([
            "### 输出格式",
            "<思考过程>（中文，非结构化）",
            f"{self.config.thinking_delimiter}",
            "<正式回复>（结构化，可直接使用）",
            "",
            f"### 用户问题\n{user_query}",
        ])

        return "\n".join(parts)

    def extract_thinking_chain(self, response: str) -> tuple[str, str]:
        """从响应中提取思考链和最终回答"""
        delimiter = self.config.thinking_delimiter

        if delimiter in response:
            parts = response.split(delimiter, 1)
            thinking = parts[0].strip()
            answer = parts[1].strip() if len(parts) > 1 else ""
            return thinking, answer

        return "", response

    def detect_language(self, text: str) -> str:
        """检测文本主要语言"""
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        total_chars = len(text.strip())

        if total_chars == 0:
            return "unknown"

        ratio = chinese_chars / total_chars
        if ratio > 0.5:
            return "zh"
        elif ratio > 0.1:
            return "mixed"
        else:
            return "en"

    def should_switch_language(self, text: str) -> bool:
        """判断是否需要切换语言"""
        if self.config.thinking_language == "auto":
            detected = self.detect_language(text)
            return detected == "zh"
        return self.config.thinking_language == "zh"

    def get_stats(self) -> Dict[str, Any]:
        """获取技能统计"""
        return {
            "enabled": self.config.enable_chinese_thinking,
            "language": self.config.thinking_language,
            "depth": self.config.thinking_depth,
            "metaphor": self.config.enable_metaphor,
            "dialectical": self.config.enable_dialectical,
        }


class ChineseThinkEncoding(ContentEncoding):
    """中文思考编码 - LCM 内容编码层标准插件

    将 ChineseThinkingSkill 的能力通过 ContentEncoding 接口接入 LCM 核心。
    职责边界：
    - 本类只负责"适配"：将 chinese-think 的能力翻译为 LCM 编码接口
    - 具体的精简规则、文本压缩逻辑由 ChineseThinkingSkill 维护
    - LCM 核心通过 ContentEncodingRegistry 发现和使用本类
    """

    _BASIC_PROMPT = """[CHINESE-THINK 精简模式]

用中文思考，精简表达。规则：
- 删除语气词、程度副词、客套话
- 用文言替换：因...故...、若...则...
- 优先单字、四字格、文言句式
- 代码/路径/术语/安全警告保持原样
"""

    def __init__(self, skill: Optional[ChineseThinkingSkill] = None):
        self._skill = skill or ChineseThinkingSkill()
        self._stats = {"encode_count": 0, "response_count": 0}

    @property
    def encoding_type(self) -> EncodingType:
        return EncodingType.CHINESE_THINK

    @property
    def name(self) -> str:
        return "中文思考精简模式"

    def encode_system_prompt(self, system_prompt: str, context: EncodingContext) -> str:
        """编码系统提示词：注入中文思考指令

        在 LCM 系统提示词后追加中文思考模式的指令，
        引导模型用中文精简表达。
        """
        if not self._skill.config.enable_chinese_thinking:
            return system_prompt

        # 使用 ChineseThinkingSkill 构建思考提示词
        thinking_prompt = self._skill.build_thinking_prompt("")
        # 只取指令部分（去掉用户问题部分）
        if "### 用户问题" in thinking_prompt:
            thinking_prompt = thinking_prompt.split("### 用户问题")[0].strip()

        self._stats["encode_count"] += 1
        return f"{system_prompt}\n\n{thinking_prompt}"

    def encode_response(self, response_text: str, context: EncodingContext) -> str:
        """编码模型响应：提取思考链并保护哨兵标记

        对模型输出进行后处理：
        1. 提取思考链（如果存在）
        2. 保护 LCM 哨兵标记不被破坏
        """
        if not self._skill.config.enable_chinese_thinking:
            return response_text

        # 保护 LCM 哨兵标记
        protected_markers = self._extract_sentinel_markers(response_text)
        working_text = self._mask_markers(response_text, protected_markers)

        # 提取思考链（如果存在）
        thinking, answer = self._skill.extract_thinking_chain(working_text)

        # 恢复哨兵标记
        if thinking:
            result = self._unmask_markers(answer, protected_markers)
        else:
            result = self._unmask_markers(working_text, protected_markers)

        self._stats["response_count"] += 1
        return result

    def decode_for_display(self, encoded_text: str, context: EncodingContext) -> str:
        """解码为展示格式

        中文思考编码通常不需要解码（输出本身就是可读中文），
        但保留接口以支持未来可能的扩展。
        """
        return encoded_text

    def get_stats(self) -> Dict[str, Any]:
        """获取编码统计"""
        return {
            "mode": self._skill.config.thinking_depth,
            "enabled": self._skill.config.enable_chinese_thinking,
            **self._stats,
            **self._skill.get_stats(),
        }

    def reset(self):
        """重置状态"""
        self._stats = {"encode_count": 0, "response_count": 0}

    # --- 内部工具方法 ---

    def _extract_sentinel_markers(self, text: str) -> Dict[str, str]:
        """提取并保护 LCM 哨兵标记"""
        import re
        markers = {}
        pattern = r"\[(NEED_CHUNK|LOAD_CHUNK|FETCH):([A-Za-z0-9_\-]+)\]"
        for match in re.finditer(pattern, text):
            marker_id = f"__SENTINEL_{len(markers)}__"
            markers[marker_id] = match.group()
        return markers

    def _mask_markers(self, text: str, markers: Dict[str, str]) -> str:
        """用占位符替换哨兵标记"""
        import re
        pattern = r"\[(NEED_CHUNK|LOAD_CHUNK|FETCH):([A-Za-z0-9_\-]+)\]"
        counter = [0]

        def replacer(m):
            marker_id = f"__SENTINEL_{counter[0]}__"
            counter[0] += 1
            return marker_id

        return re.sub(pattern, replacer, text)

    def _unmask_markers(self, text: str, markers: Dict[str, str]) -> str:
        """恢复哨兵标记"""
        for marker_id, original in markers.items():
            text = text.replace(marker_id, original)
        return text
