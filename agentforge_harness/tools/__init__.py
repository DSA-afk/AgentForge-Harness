"""Built-in tools. Names match Claude Code's so existing hook matchers keep working."""

from agentforge_harness.tools.base import Tool, ToolContext, ToolResult
from agentforge_harness.tools.files import Edit, Glob, Grep, Read, Write
from agentforge_harness.tools.judge import Judge
from agentforge_harness.tools.plan import ExitPlanMode
from agentforge_harness.tools.shell import Bash
from agentforge_harness.tools.todo import TodoWrite
from agentforge_harness.tools.web import WebFetch, WebSearch


def default_tools(web_allow_private: bool = False) -> dict[str, Tool]:
    tools = [
        Bash(),
        Read(),
        Write(),
        Edit(),
        Glob(),
        Grep(),
        TodoWrite(),
        ExitPlanMode(),
        WebFetch(web_allow_private),
        WebSearch(),
        Judge(),
    ]
    return {tool.name: tool for tool in tools}


__all__ = ["Tool", "ToolContext", "ToolResult", "default_tools"]
