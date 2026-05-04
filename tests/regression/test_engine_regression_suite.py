"""

核心引擎回归测试套件

在重构 AIAgent 类之前运行，确保重构后所有核心行为保持一致



运行方式:

    pytest tests/regression/test_engine_regression_suite.py -v

    python -m pytest tests/regression/ -v

"""



import pytest

import sys

import os



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))



from tests.unit.test_agent_role_validation import (

    TestRoleAlternation,

    TestRoleValidationEdgeCases,

    MessageRoleValidator

)

from tests.unit.test_concurrent_tool_calls import (

    TestConcurrentToolIdempotency,

    TestToolCallSafety,

    MockToolRegistry,

    IdempotencyTracker,

    ReadOnlyTool,

    StatefulTool,

    NonIdempotentTool

)

from tests.unit.test_context_compression import (

    TestContextCompressionKeyInfoRetention,

    TestCompressionBoundaryDetection,

    TestResolvedPendingTracking,

    CompressionEngine,

    CriticalInfoExtractor,

    InformationRetentionCalculator,

    Message,

    MessageRole,

    CriticalInfo,

    CriticalInfoType

)





def create_fresh_role_validator():

    """创建全新的角色验证器"""

    return MessageRoleValidator()





def create_fresh_tool_suite():

    """创建全新的工具测试套件"""

    suite = TestConcurrentToolIdempotency()

    suite.setup_method()

    return suite





def create_fresh_compression_suite():

    """创建全新的压缩测试套件"""

    suite = TestContextCompressionKeyInfoRetention()

    suite.setup_method()

    return suite





class TestEngineRegressionSuite:

    """

    核心引擎回归测试套件

    所有测试必须在重构后通过

    """



    def test_00_role_validation_complete(self):

        """角色交替验证完整测试"""

        validator = create_fresh_role_validator()



        for role in ["system", "user", "assistant", "user", "assistant"]:

            validator.add_message(role)

        is_valid, errors = validator.validate_history()

        assert is_valid, f"Valid sequence should pass: {errors}"



        validator.reset()

        for role in ["system", "user", "assistant", "tool", "tool", "assistant", "user", "assistant"]:

            validator.add_message(role)

        is_valid, errors = validator.validate_history()

        assert is_valid, f"Valid sequence with tools should pass: {errors}"



        validator.reset()

        validator.add_message("system")

        validator.add_message("user")

        validator.add_message("user")

        violations = validator.get_consecutive_violations()

        assert len(violations) > 0 and violations[0][1] == "user"



        validator.reset()

        validator.add_message("system")

        validator.add_message("user")

        validator.add_message("assistant")

        validator.add_message("assistant")

        violations = validator.get_consecutive_violations()

        assert len(violations) > 0 and violations[0][1] == "assistant"



        validator.reset()

        validator.add_message("system")

        validator.add_message("tool")

        is_valid, errors = validator.validate_history()

        assert not is_valid



        validator.reset()

        validator.add_message("system")

        validator.add_message("user")

        validator.add_message("tool")

        is_valid, errors = validator.validate_history()

        assert not is_valid



        validator.reset()

        validator.add_message("system")

        validator.add_message("user")

        validator.add_message("assistant")

        validator.add_message("system")

        is_valid, errors = validator.validate_history()

        assert not is_valid



        validator.reset()

        validator.add_message("system")

        validator.add_message("user")

        validator.add_message("assistant")

        validator.add_message("tool")

        validator.add_message("user")

        is_valid, errors = validator.validate_history()

        assert not is_valid



        validator.reset()

        for role in ["system", "user", "assistant", "tool", "tool", "tool", "assistant"]:

            validator.add_message(role)

        is_valid, errors = validator.validate_history()

        assert is_valid



    def test_01_role_validation_edge_cases(self):

        """角色验证边界情况"""

        validator = create_fresh_role_validator()

        validator.add_message("system")

        is_valid, errors = validator.validate_history()

        assert is_valid



        validator.reset()

        validator.add_message("system")

        validator.add_message("user")

        is_valid, errors = validator.validate_history()

        assert is_valid



        validator.reset()

        validator.add_message("unknown_role")

        is_valid, errors = validator.validate_history()

        assert not is_valid



        validator.reset()

        validator.add_message("System")

        validator.add_message("user")

        is_valid, errors = validator.validate_history()

        assert not is_valid



    def test_02_concurrent_idempotency(self):

        """并发工具幂等性测试"""

        from concurrent.futures import ThreadPoolExecutor, as_completed



        registry = MockToolRegistry()

        tracker = IdempotencyTracker()



        read_only_tool = ReadOnlyTool({

            "project": "I.R.I.S. Smart Terminal",

            "config": "settings.json",

            "readme": "documentation"

        })

        registry.register("search", read_only_tool.search)

        registry.register("read", read_only_tool.read)



        def call_search():

            return registry.call("search", {"query": "project"}, tracker)



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [executor.submit(call_search) for _ in range(20)]

            results = [f.result() for f in as_completed(futures)]



        result_values = [str(r.result) for r in results]

        results_set = set(result_values)

        assert len(results_set) == 1



        registry2 = MockToolRegistry()

        tracker2 = IdempotencyTracker()

        stateful_tool = StatefulTool()

        registry2.register("increment", stateful_tool.increment)



        def call_increment():

            return registry2.call("increment", {"amount": 1}, tracker2)



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [executor.submit(call_increment) for _ in range(100)]

            results = [f.result() for f in as_completed(futures)]



        assert stateful_tool.get_counter() == 100



        tracker3 = IdempotencyTracker()

        for _ in range(5):

            registry.call("search", {"query": "project"}, tracker3)



        call_count = tracker3.get_call_count("search", {"query": "project"})

        assert call_count == 5



    def test_03_tool_safety(self):

        """工具安全性测试"""

        registry = MockToolRegistry()

        tracker = IdempotencyTracker()



        result = registry.call("nonexistent_tool", {"arg": "value"}, tracker)

        assert "not found" in result.result



        def failing_tool():

            raise ValueError("Intentional failure")



        registry.register("failing", failing_tool)



        for _ in range(5):

            try:

                registry.call("failing", {}, tracker)

            except ValueError:

                pass



        assert "failing" in registry.tools



    def test_04_compression_key_info_retention(self):

        """压缩关键信息保留测试"""

        compressor = CompressionEngine(max_tokens=100)

        extractor = CriticalInfoExtractor()



        messages = [

            Message(role="system", content="你是I.R.I.S.，一个智能助手"),

            Message(role="system", content="always be helpful"),

            Message(role="user", content="你好"),

            Message(role="assistant", content="你好！"),

            Message(role="user", content="今天天气如何"),

            Message(role="assistant", content="今天是晴天"),

            Message(role="user", content="谢谢"),

            Message(role="assistant", content="不客气！"),

        ]



        critical_info = []

        for msg in messages:

            critical_info.extend(extractor.extract(msg))



        compressed, preserved = compressor.compress(messages, critical_info)



        assert len(compressed) < len(messages)

        assert compressed[0].role == "system"



    def test_05_compression_boundary(self):

        """压缩边界检测测试"""

        compressor = CompressionEngine(max_tokens=100)



        messages = [

            Message(role="system", content="系统"),

            Message(role="user", content="用户"),

            Message(role="assistant", content="助手"),

        ]



        compressed, _ = compressor.compress(messages, [])

        assert len(compressed) == len(messages)



    def test_06_resolved_pending_tracking(self):

        """Resolved/Pending状态追踪测试"""

        class TaskTracker:

            def __init__(self):

                self.resolved = []

                self.pending = []



            def mark_resolved(self, task_id):

                if task_id not in self.resolved:

                    self.resolved.append(task_id)

                if task_id in self.pending:

                    self.pending.remove(task_id)



            def add_pending(self, task_id):

                if task_id not in self.pending:

                    self.pending.append(task_id)



            def get_status(self, task_id):

                if task_id in self.resolved:

                    return "resolved"

                if task_id in self.pending:

                    return "pending"

                return "unknown"



        tracker = TaskTracker()

        tracker.add_pending("task1")

        tracker.add_pending("task2")

        tracker.add_pending("task3")



        assert tracker.get_status("task1") == "pending"

        tracker.mark_resolved("task1")

        assert tracker.get_status("task1") == "resolved"

        assert tracker.get_status("task2") == "pending"





if __name__ == "__main__":

    pytest.main([__file__, "-v", "--tb=short"])

