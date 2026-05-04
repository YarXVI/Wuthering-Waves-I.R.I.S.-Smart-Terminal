"""

核心引擎边界测试：消息角色交替验证

测试目标：在重构 AIAgent 类之前，建立测试基准确保重构过程无回归



验证点：

1. 合法的 role 序列：System → User → Assistant → User → Assistant...

2. 禁止连续两个相同 role（除 tool 外）

3. 禁止 role 顺序错误

"""



import pytest

from typing import Any





VALID_ROLE_SEQUENCE = ["system", "user", "assistant", "user", "assistant"]



ALLOWED_TRANSITIONS = {

    "system": ["user"],

    "user": ["assistant"],

    "assistant": ["user", "tool"],

    "tool": ["assistant", "tool"],

}



FORBIDDEN_TRANSITIONS = {

    "system": ["system", "assistant", "tool"],

    "user": ["system", "user", "tool"],

    "assistant": ["assistant", "system"],

    "tool": ["system", "user"],

}





class MessageRoleValidator:

    """消息角色交替验证器"""



    def __init__(self):

        self.history: list[str] = []



    def add_message(self, role: str) -> None:

        """添加消息到历史"""

        self.history.append(role)



    def reset(self) -> None:

        """重置历史"""

        self.history = []



    def validate_transition(self, prev_role: str, next_role: str) -> tuple[bool, str]:

        """

        验证角色转换是否合法

        Returns: (is_valid, error_message)

        """

        if prev_role not in ALLOWED_TRANSITIONS:

            return False, f"Unknown prev_role: {prev_role}"

        if next_role not in ALLOWED_TRANSITIONS:

            return False, f"Unknown next_role: {next_role}"



        if next_role in FORBIDDEN_TRANSITIONS.get(prev_role, []):

            return False, f"Forbidden transition: {prev_role} → {next_role}"



        return True, ""



    def validate_history(self) -> tuple[bool, list[str]]:

        """

        验证整个消息历史是否合法

        Returns: (is_valid, list_of_errors)

        """

        errors = []



        if not self.history:

            return True, []



        # 检查所有角色是否有效

        for i, role in enumerate(self.history):

            if role not in ALLOWED_TRANSITIONS:

                errors.append(f"Position {i}: Invalid role '{role}'")



        # 检查角色转换

        for i in range(len(self.history) - 1):

            prev_role = self.history[i]

            next_role = self.history[i + 1]

            is_valid, error_msg = self.validate_transition(prev_role, next_role)

            if not is_valid:

                errors.append(f"Position {i}→{i+1}: {error_msg}")



        return len(errors) == 0, errors



    def get_consecutive_violations(self) -> list[tuple[int, str]]:

        """检测连续相同角色的违规"""

        violations = []

        for i in range(len(self.history) - 1):

            if self.history[i] == self.history[i + 1]:

                violations.append((i, self.history[i]))

        return violations





class TestRoleAlternation:

    """角色交替测试套件"""



    def setup_method(self):

        self.validator = MessageRoleValidator()



    def test_valid_sequence_system_user_assistant(self):

        """测试标准合法序列"""

        for role in VALID_ROLE_SEQUENCE:

            self.validator.add_message(role)



        is_valid, errors = self.validator.validate_history()

        assert is_valid, f"Valid sequence should pass: {errors}"



    def test_valid_sequence_with_tools(self):

        """测试包含工具调用的合法序列"""

        sequence = [

            "system", "user", "assistant",

            "tool", "tool",

            "assistant", "user", "assistant"

        ]

        for role in sequence:

            self.validator.add_message(role)



        is_valid, errors = self.validator.validate_history()

        assert is_valid, f"Valid sequence with tools should pass: {errors}"



    def test_consecutive_user_forbidden(self):

        """测试禁止连续两个 user"""

        self.validator.add_message("system")

        self.validator.add_message("user")

        self.validator.add_message("user")  # 非法！



        violations = self.validator.get_consecutive_violations()

        assert len(violations) > 0, "Should detect consecutive users"

        assert violations[0][1] == "user"



    def test_consecutive_assistant_forbidden(self):

        """测试禁止连续两个 assistant"""

        self.validator.add_message("system")

        self.validator.add_message("user")

        self.validator.add_message("assistant")

        self.validator.add_message("assistant")  # 非法！



        violations = self.validator.get_consecutive_violations()

        assert len(violations) > 0, "Should detect consecutive assistants"

        assert violations[0][1] == "assistant"



    def test_system_to_tool_forbidden(self):

        """测试 system 不能直接到 tool"""

        self.validator.add_message("system")

        self.validator.add_message("tool")  # 非法！



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "system → tool should be forbidden"

        assert any("Forbidden transition" in e for e in errors)



    def test_user_to_tool_forbidden(self):

        """测试 user 不能直接到 tool"""

        self.validator.add_message("system")

        self.validator.add_message("user")

        self.validator.add_message("tool")  # 非法！



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "user → tool should be forbidden"



    def test_assistant_to_system_forbidden(self):

        """测试 assistant 不能直接到 system"""

        self.validator.add_message("system")

        self.validator.add_message("user")

        self.validator.add_message("assistant")

        self.validator.add_message("system")  # 非法！



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "assistant → system should be forbidden"



    def test_tool_to_user_forbidden(self):

        """测试 tool 不能直接到 user"""

        self.validator.add_message("system")

        self.validator.add_message("user")

        self.validator.add_message("assistant")

        self.validator.add_message("tool")

        self.validator.add_message("user")  # 非法！



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "tool → user should be forbidden"



    def test_consecutive_tools_allowed(self):

        """测试连续多个 tool 是允许的"""

        sequence = [

            "system", "user", "assistant",

            "tool", "tool", "tool",

            "assistant"

        ]

        for role in sequence:

            self.validator.add_message(role)



        is_valid, errors = self.validator.validate_history()

        assert is_valid, f"Consecutive tools should be allowed: {errors}"



    def test_empty_history(self):

        """测试空历史"""

        is_valid, errors = self.validator.validate_history()

        assert is_valid, "Empty history should be valid"



    def test_single_message(self):

        """测试单条消息"""

        self.validator.add_message("system")

        is_valid, errors = self.validator.validate_history()

        assert is_valid, "Single system message should be valid"



    def test_complex_valid_sequence(self):

        """测试复杂合法序列"""

        sequence = [

            "system",

            "user", "assistant",

            "user", "assistant", "tool", "tool", "assistant",

            "user", "assistant",

        ]

        for role in sequence:

            self.validator.add_message(role)



        is_valid, errors = self.validator.validate_history()

        assert is_valid, f"Complex valid sequence should pass: {errors}"



    def test_complex_invalid_sequence(self):

        """测试复杂非法序列"""

        sequence = [

            "system",

            "user", "assistant",

            "user", "assistant", "tool",

            "assistant",  # tool → assistant 合法

            "assistant",  # 非法！连续 assistant

            "user",

        ]

        for role in sequence:

            self.validator.add_message(role)



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "Should detect violation"



    def test_multiple_violations(self):

        """测试检测多个违规"""

        sequence = [

            "system",

            "user",

            "user",  # 非法1: 连续 user

            "assistant",

            "assistant",  # 非法2: 连续 assistant

            "user",

        ]

        for role in sequence:

            self.validator.add_message(role)



        violations = self.validator.get_consecutive_violations()

        assert len(violations) >= 2, "Should detect multiple violations"



    def test_reset_functionality(self):

        """测试重置功能"""

        self.validator.add_message("system")

        self.validator.add_message("user")

        self.validator.add_message("user")  # 非法



        assert len(self.validator.get_consecutive_violations()) > 0



        self.validator.reset()

        assert len(self.validator.history) == 0

        assert len(self.validator.get_consecutive_violations()) == 0



        is_valid, errors = self.validator.validate_history()

        assert is_valid, "After reset, history should be valid"





class TestRoleValidationEdgeCases:

    """边界情况测试"""



    def setup_method(self):

        self.validator = MessageRoleValidator()



    def test_unknown_role(self):

        """测试未知角色"""

        self.validator.add_message("system")

        self.validator.add_message("unknown_role")



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "Unknown role should fail"



    def test_case_sensitivity(self):

        """测试大小写敏感性"""

        self.validator.add_message("System")  # 大写 S

        self.validator.add_message("user")



        is_valid, errors = self.validator.validate_history()

        assert not is_valid, "Role names should be case-sensitive"





if __name__ == "__main__":

    pytest.main([__file__, "-v"])

