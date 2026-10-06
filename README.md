# AgentForge Harness

基于 [mwm-harness](https://github.com/Matswm86/mwm-harness) 扩展的 Python Agent Harness 项目，用于代码仓库分析和多步骤工具任务，提供终端与 FastAPI Web 入口。

## 核心能力

- **上下文管理**：大工具结果落盘、按需回读，达到 Token 预算后压缩历史。
- **子任务隔离**：子 Agent 使用独立上下文和工具范围，仅向主任务返回最终结果。
- **会话恢复**：JSONL 日志、压缩摘要恢复、中断工具调用结果修补。
- **执行安全**：工具权限、人工确认、生命周期 Hook，以及 Linux bubblewrap 文件系统隔离。
- **工具接入**：文件、Shell、MCP、Skill 和 OpenAI 兼容模型接口。

## 运行

Python 3.12+。完整 Shell、Hook 与隔离功能建议在 Linux / WSL 中运行。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

在 `models.toml` 配置模型的 `base_url`、`key_env` 和上下文预算，并通过环境变量设置对应 API Key。命令和 Python 包名暂时沿用上游，方便兼容已有配置。

```bash
mwm --model <模型ID>
mwm --model <模型ID> --web
mwm --model <模型ID> --resume last
python -m pytest -q
```

## 本地改动

- 恢复时跳过非对象 JSON 记录和错误消息结构，避免异常记录阻断后续有效历史。
- 缺失工具结果标记为“执行结果未知”，提示核对副作用后再重试。
- 逐行读取会话日志，避免一次性读入并拆分整份日志。

当前恢复能力不包含持久化检查点和幂等执行；子任务不包含 Fork 上下文模式；bubblewrap 配置未提供网络隔离。验证记录见 [MIGRATION.md](MIGRATION.md)。

## 来源

基于 MWM AI 的 MIT 开源项目，保留原始 [LICENSE](LICENSE)。上游版本及本地修改范围见 [UPSTREAM.md](UPSTREAM.md)。
