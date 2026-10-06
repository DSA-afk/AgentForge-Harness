# AgentForge Harness

采用 Harness 架构的 Python Agent 工程项目，面向代码仓库分析和多步骤任务，提供终端与 Web 两种交互方式。

## 功能

- 上下文管理：大工具结果落盘回读、Token 预算监控与历史摘要压缩。
- 子任务执行：独立上下文、工具范围限制与结果回传。
- 会话恢复：JSONL 日志持久化、压缩摘要恢复与中断状态处理。
- 安全控制：工具权限、人工确认、生命周期 Hook 与 Linux 文件系统隔离。
- 工具扩展：文件操作、Shell、MCP、Skill 与 OpenAI 兼容模型接口。

## 快速开始

需要 Python 3.12+，完整 Shell / Hook 功能建议在 Linux 或 WSL 中使用。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[web]"
```

在 `models.toml` 中配置模型地址、模型 ID 和 `key_env`，再设置该字段对应的 API Key 环境变量。

```bash
agentforge --model <模型ID>
agentforge --model <模型ID> --web
agentforge --model <模型ID> --resume last
```

默认配置目录为 `~/.config/agentforge-harness`，可通过 `AGENTFORGE_HARNESS_CONFIG` 指定其他目录。

## 开发

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

核心代码位于 `agentforge_harness/`，测试位于 `tests/`。

许可证与第三方声明：[LICENSE](LICENSE) 。
