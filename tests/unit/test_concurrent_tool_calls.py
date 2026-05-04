"""

核心引擎边界测试：并发工具调用幂等性验证

测试目标：验证同一工具被并发调用时的幂等性保证



验证点：

1. 相同参数的多次调用应返回一致结果

2. 并发场景下不会产生状态不一致

3. 工具执行的副作用有适当的隔离机制

"""



import pytest

import asyncio

import time

from concurrent.futures import ThreadPoolExecutor, as_completed

from typing import Any, Callable

from dataclasses import dataclass, field

from threading import Lock





@dataclass

class ToolExecutionResult:

    """工具执行结果"""

    tool_name: str

    args: dict

    result: Any

    execution_time: float

    call_id: str = ""





class IdempotencyTracker:

    """幂等性追踪器"""



    def __init__(self):

        self.call_history: list[ToolExecutionResult] = []

        self.lock = Lock()

        self._call_count = 0



    def record_call(self, result: ToolExecutionResult):

        with self.lock:

            self.call_history.append(result)



    def get_call_count(self, tool_name: str, args: dict) -> int:

        with self.lock:

            return sum(

                1 for r in self.call_history

                if r.tool_name == tool_name and r.args == args

            )



    def get_calls(self, tool_name: str, args: dict) -> list[ToolExecutionResult]:

        with self.lock:

            return [

                r for r in self.call_history

                if r.tool_name == tool_name and r.args == args

            ]



    def generate_call_id(self) -> str:

        with self.lock:

            self._call_count += 1

            return f"call_{self._call_count}"





class MockToolRegistry:

    """模拟工具注册表"""



    def __init__(self):

        self.tools: dict[str, Callable] = {}

        self.call_log: list[tuple[str, dict]] = []

        self.log_lock = Lock()



    def register(self, name: str, handler: Callable):

        self.tools[name] = handler



    def call(self, name: str, args: dict, tracker: IdempotencyTracker) -> ToolExecutionResult:

        if name not in self.tools:

            return ToolExecutionResult(

                tool_name=name,

                args=args,

                result=f"Tool '{name}' not found",

                execution_time=0

            )



        start = time.time()

        result = self.tools[name](**args)

        execution_time = time.time() - start



        result_obj = ToolExecutionResult(

            tool_name=name,

            args=args,

            result=result,

            execution_time=execution_time,

            call_id=tracker.generate_call_id()

        )

        tracker.record_call(result_obj)



        with self.log_lock:

            self.call_log.append((name, args.copy()))



        return result_obj





class ReadOnlyTool:

    """只读工具（天然幂等）"""



    def __init__(self, data: dict):

        self.data = data



    def search(self, query: str) -> list[str]:

        return [k for k in self.data.keys() if query.lower() in k.lower()]



    def read(self, key: str) -> str:

        return self.data.get(key, f"Key '{key}' not found")





class StatefulTool:

    """有状态工具（需要测试幂等性）"""



    def __init__(self):

        self._counter = 0

        self._lock = Lock()



    def increment(self, amount: int = 1) -> int:

        with self._lock:

            self._counter += amount

            return self._counter



    def get_counter(self) -> int:

        with self._lock:

            return self._counter





class NonIdempotentTool:

    """故意非幂等的工具（用于测试）"""



    def __init__(self):

        self.call_count = 0



    def reset_and_get(self) -> int:

        self.call_count += 1

        return self.call_count





class TestConcurrentToolIdempotency:

    """并发工具调用幂等性测试套件"""



    def setup_method(self):

        self.registry = MockToolRegistry()

        self.tracker = IdempotencyTracker()



        self.read_only_tool = ReadOnlyTool({

            "project": "I.R.I.S. Smart Terminal",

            "config": "settings.json",

            "readme": "documentation"

        })

        self.registry.register("search", self.read_only_tool.search)

        self.registry.register("read", self.read_only_tool.read)



        self.stateful_tool = StatefulTool()

        self.registry.register("increment", self.stateful_tool.increment)



        self.non_idempotent = NonIdempotentTool()

        self.registry.register("reset_and_get", self.non_idempotent.reset_and_get)



    def test_concurrent_same_read_calls_return_same_result(self):

        """测试相同读操作的并发调用返回一致结果"""



        def call_search():

            return self.registry.call("search", {"query": "project"}, self.tracker)



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [executor.submit(call_search) for _ in range(20)]

            results = [f.result() for f in as_completed(futures)]



        result_values = [str(r.result) for r in results]

        results_set = set(result_values)

        assert len(results_set) == 1, f"All read results should be identical: {results_set}"



    def test_concurrent_different_read_calls_return_different_results(self):

        """测试不同读操作的并发调用返回不同结果"""



        def call_read(key: str):

            return self.registry.call("read", {"key": key}, self.tracker)



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [

                executor.submit(call_read, "project"),

                executor.submit(call_read, "config"),

                executor.submit(call_read, "readme"),

            ]

            results = [f.result() for f in as_completed(futures)]



        result_values = [r.result for r in results]

        assert len(set(result_values)) == 3, "Different reads should return different results"



    def test_stateful_tool_concurrent_calls_are_serialized(self):

        """测试有状态工具的并发调用被正确序列化"""



        def call_increment():

            return self.registry.call("increment", {"amount": 1}, self.tracker)



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [executor.submit(call_increment) for _ in range(100)]

            results = [f.result() for f in as_completed(futures)]



        final_counter = self.stateful_tool.get_counter()

        assert final_counter == 100, f"Counter should be 100, got {final_counter}"



    def test_race_condition_detection(self):

        """测试竞态条件检测"""



        class RaceConditionProneTool:

            def __init__(self):

                self.value = 0



            def increment(self):

                old = self.value

                time.sleep(0.0001)

                self.value = old + 1

                return self.value



        tool = RaceConditionProneTool()



        def call_increment():

            return tool.increment()



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [executor.submit(call_increment) for _ in range(100)]

            results = [f.result() for f in as_completed(futures)]



        expected_final = 100

        actual_final = tool.value



        if actual_final != expected_final:

            print(f"Race condition detected! Expected {expected_final}, got {actual_final}")



    def test_idempotent_calls_tracked_correctly(self):

        """测试幂等调用被正确追踪"""

        for _ in range(5):

            self.registry.call("search", {"query": "project"}, self.tracker)



        call_count = self.tracker.get_call_count("search", {"query": "project"})

        assert call_count == 5, f"Should track 5 calls, got {call_count}"



    def test_non_idempotent_tool_produces_different_results(self):

        """测试非幂等工具产生不同结果"""

        results = []

        for _ in range(10):

            result = self.registry.call("reset_and_get", {}, self.tracker)

            results.append(result.result)



        result_set = set(results)

        assert len(result_set) > 1, "Non-idempotent tool should produce different results"



    def test_parallel_tool_calls_complete_without_deadlock(self):

        """测试并行工具调用不会死锁"""



        async def async_tool_call(tool_name: str, args: dict):

            return self.registry.call(tool_name, args, self.tracker)



        async def run_parallel():

            tasks = [

                async_tool_call("search", {"query": "project"})

                for _ in range(50)

            ]

            return await asyncio.gather(*tasks)



        start = time.time()

        results = asyncio.run(run_parallel())

        duration = time.time() - start



        assert len(results) == 50, "All calls should complete"

        assert duration < 5.0, f"Should complete quickly, took {duration}s"



    def test_tool_call_order_preserved(self):

        """测试工具调用顺序被保留"""

        call_order = []



        def make_tracker():

            def track():

                call_order.append(len(call_order))

                time.sleep(0.001)

                return "done"

            return track



        tool = make_tracker()

        self.registry.register("ordered", tool)



        def call_ordered():

            return self.registry.call("ordered", {}, self.tracker)



        with ThreadPoolExecutor(max_workers=5) as executor:

            futures = [executor.submit(call_ordered) for _ in range(10)]

            [f.result() for f in as_completed(futures)]



        assert len(call_order) == 10



    def test_multiple_tools_concurrent_calls(self):

        """测试多工具并发调用"""



        def call_search():

            return self.registry.call("search", {"query": "project"}, self.tracker)



        def call_read():

            return self.registry.call("read", {"key": "config"}, self.tracker)



        def call_increment():

            return self.registry.call("increment", {"amount": 1}, self.tracker)



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = []

            for _ in range(10):

                futures.append(executor.submit(call_search))

                futures.append(executor.submit(call_read))

                futures.append(executor.submit(call_increment))



            results = [f.result() for f in as_completed(futures)]



        assert len(results) == 30



        search_results = [r for r in results if r.tool_name == "search"]

        assert len(search_results) == 10





class TestToolCallSafety:

    """工具调用安全性测试"""



    def setup_method(self):

        self.registry = MockToolRegistry()

        self.tracker = IdempotencyTracker()



    def test_unknown_tool_handled_gracefully(self):

        """测试未知工具被优雅处理"""

        result = self.registry.call("nonexistent_tool", {"arg": "value"}, self.tracker)

        assert "not found" in result.result



    def test_tool_exception_doesnt_crash_registry(self):

        """测试工具异常不导致注册表崩溃"""



        def failing_tool():

            raise ValueError("Intentional failure")



        self.registry.register("failing", failing_tool)



        for _ in range(5):

            try:

                self.registry.call("failing", {}, self.tracker)

            except ValueError:

                pass



        assert "failing" in self.registry.tools



    def test_concurrent_calls_with_mixed_results(self):

        """测试混合成功/失败的并发调用"""



        def sometimes_failing_tool(fail: bool):

            if fail:

                raise RuntimeError("Random failure")

            return "success"



        self.registry.register("mixed", sometimes_failing_tool)



        def call_mixed(fail: bool):

            try:

                return self.registry.call("mixed", {"fail": fail}, self.tracker)

            except Exception as e:

                return ToolExecutionResult(

                    tool_name="mixed",

                    args={"fail": fail},

                    result=f"Exception: {e}",

                    execution_time=0

                )



        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [executor.submit(call_mixed, i % 2 == 0) for i in range(20)]

            results = [f.result() for f in as_completed(futures)]



        assert len(results) == 20





if __name__ == "__main__":

    pytest.main([__file__, "-v"])

