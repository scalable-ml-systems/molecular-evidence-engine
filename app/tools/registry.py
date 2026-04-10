import time

from app.observability.logging import log_event


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {}

    def register(self, tool):
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        # wrap tool with logging
        self._tools[tool.name] = self._wrap_tool(tool)

    def _wrap_tool(self, tool):
        class LoggedTool:
            name = tool.name

            def execute(self_inner, request):
                start = time.time()

                log_event(
                    "tool_call_start",
                    tool_name=tool.name,
                    request=request.model_dump(),
                )

                response = tool.execute(request)

                latency = int((time.time() - start) * 1000)

                log_event(
                    "tool_call_end",
                    tool_name=tool.name,
                    status=response.status,
                    result_count=len(response.results),
                    latency_ms=latency,
                )

                return response

        return LoggedTool()

    def get(self, name: str):
        return self._tools[name]

    def list_tools(self):
        return sorted(self._tools.keys())