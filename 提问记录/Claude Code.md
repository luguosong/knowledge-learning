# Claude Code

## 综述

学习 Claude Code 的总框架是**四层地图**：把 Claude Code 当作 Anthropic agent 理论的参考实现——①理论底座（增强型 LLM；workflow vs agent；agent 本质＝LLM 用工具并根据环境反馈循环；链式/路由/并行/编排者-工人/评估者-优化者五模式；ACI；简单优先）→ ②核心机制（agentic loop 探索→计划→实施→提交、上下文管理 /clear、/compact、CLAUDE.md 记忆、工具与权限三态、subagent/hooks/skills、MCP）→ ③驾驶技术（plan 模式、验证闭环"给 Claude 可运行的检查"、CLAUDE.md 逐行"删掉会犯错吗"检验、白名单+沙箱）→ ④规模化（headless claude -p、CI 代码审查、worktree/批量并行、Agent SDK 自建）。贯穿方法论：上下文是稀缺资源 + 简单优先。已深挖 subagent（属第②层，orchestrator-workers 模式实例）：独立上下文窗口隔离污染，description 驱动自动委派，冷启动不继承历史，默认 3 层嵌套 20 并发，agent ID + SendMessage 续聊。待解：hooks/memory/isolation: worktree 实操验证；五种编排模式的实例推演。

## 2026-09-21 · Claude Code subagent 的使用、配置与执行原理
- **问**：详细讲解 Claude Code 中 subagent 的使用方法、配置方式、执行过程以及原理。
- **答**：subagent 是由主对话派生、拥有独立上下文窗口的专职 agent，核心动机是隔离上下文污染（挤占预算、稀释注意力、推高成本）。执行：主 agent 依据各代理 description 决定委派 → Agent tool 派生 → 子代理冷启动（自身 system prompt + 任务消息 + CLAUDE.md + git 快照，不继承对话历史）→ 工具循环（两道工具过滤器 + 独立权限，提示上浮主会话）→ 输出扫描防提示注入 → 回传摘要 + agent ID（可用 SendMessage 带全历史续聊，保留热 prompt cache）。默认 3 层嵌套、20 并发；fork（/subtask）是唯一继承父历史的例外。配置：.claude/agents/（项目）与 ~/.claude/agents/（用户）下的 Markdown + frontmatter，仅 name、description 必填，description 驱动自动委派，model 解析顺序为 调用参数 → frontmatter → CLAUDE_CODE_SUBAGENT_MODEL → 主对话模型；缺 name/description 的文件被静默跳过。使用：自动委派（最常用）、@-mention（保证触发）、claude --agent <name>（整机替换）；内置 Explore（只读探索）/Plan（计划调研）/general-purpose。
- **信源**：[一手] https://code.claude.com/docs/en/sub-agents

## 2026-09-21 · 系统学习 Claude Code 与 Agent 原理的学习地图
- **问**：从宏观角度系统深入学习 Claude Code 的使用与原理，顺带学 agent 智能体工作原理，需要学哪些模块与知识点？
- **答**：四层递进——理论底座（增强型 LLM、workflow vs agent、"LLM 用工具并根据环境反馈循环"、五编排模式、ACI、简单优先）→ 核心机制（agentic loop 探索→计划→实施→提交、上下文管理、CLAUDE.md、工具与权限、subagent/hooks/skills、MCP）→ 驾驶技术（plan 模式分离研究与执行、验证闭环＝给 Claude 可运行的检查、CLAUDE.md 逐行检验、白名单+沙箱）→ 规模化（headless `claude -p`、GitHub Actions 代码审查、worktree 与 /batch fan-out 并行、Agent SDK 自建）。贯穿两条方法论：上下文是稀缺资源、简单优先。coding 是 agent 最佳落地场景，因其可验证（测试/构建即环境反馈）。
- **信源**：[一手] https://www.anthropic.com/engineering/building-effective-agents · [一手] https://code.claude.com/docs/en/overview · [一手] https://code.claude.com/docs/en/best-practices
- **关联**：深化本文件 2026-09-21 subagent 条目——subagent 属核心机制层，是 orchestrator-workers 模式的实例
