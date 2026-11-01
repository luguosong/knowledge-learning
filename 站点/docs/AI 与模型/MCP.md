# MCP

模型上下文协议（Model Context Protocol，MCP）用 JSON-RPC 2.0 消息把工具、资源与提示模板接入模型。主线：架构接入、核心能力、消息与传输、交互、宿主、授权安全、部署与兼容；基线为 2026-07-28 规范。

## 学习路线：从接入到扩展

学习按「会接入 → 会写服务器 → 理解协议 → 会写客户端和宿主 → 安全上线 → 扩展与兼容」推进。

```text
会接入 > 会写服务器 > 理解协议 > 会写客户端和宿主 > 安全上线 > 扩展与兼容
```

完整知识清单分 12 块：

1. **前置基础**：任选一门有官方 SDK 的语言；包管理、类型、异步、异常、测试、进程、标准流、环境变量；JSON、JSON Schema 2020-12、JSON-RPC 2.0、HTTP、SSE；模型工具调用与上下文限制。
2. **架构**：宿主（Host）、客户端（Client）、服务器（Server）的职责；数据层与传输层；发现、调用、上下文装配和模型执行的关系；与普通 API、函数调用、检索增强生成、Agent Skills 的分工。
3. **接入**：command、args、env、工作目录、路径、配置作用域；本地标准输入／输出（Standard Input/Output，stdio）、本地 HTTP、远程 HTTP；供应链、版本固定和凭据管理；Inspector 查看原始消息与排障。
4. **服务器能力**：tools/list、tools/call；输入输出 Schema、structuredContent、isError、工具提示注解；resources/list、resources/read、resources/templates/list；URI、模板、文本与二进制；prompts/list、prompts/get、参数和消息；文字、图像、音频、资源链接及嵌入资源；title、description、icons、annotations、_meta。
5. **基础协议**：请求、结果、错误和通知；请求 ID、并发关联、乱序返回；每请求版本、身份和能力；server/discover；resultType；JSON-RPC 错误与工具执行错误的区分；Schema 的 $ref、组合和验证资源限制。
6. **传输**：stdio 的换行分帧、UTF-8、stdout 纯协议、stderr 日志、子进程生命周期；HTTP 单端点 POST、JSON 或请求级 SSE、内容协商；MCP-Protocol-Version、Mcp-Method、适用请求的 Mcp-Name；x-mcp-header、头体一致性和安全编码；断线、超时、取消；本地 Origin 校验和回环绑定。
7. **交互与通用机制**：MRTR 的 input_required、inputRequests、inputResponses、requestState 与重试新 ID；Elicitation 的 form/url、accept/decline/cancel 和敏感信息边界；subscriptions/listen 的过滤、确认、关联和重建；progressToken；cursor 分页；ttlMs、cacheScope 和缓存失效；completion/complete；幂等、并发与业务状态句柄。
8. **客户端与宿主**：多服务器生命周期、名字冲突、能力降级；协议工具与模型工具定义转换；工具调用循环、上下文预算、审批、最大轮数；资源与提示模板的使用；渐进式工具发现、程序化工具调用、缓存和沙箱。
9. **授权**：HTTP 下的 OAuth 角色、授权码和 PKCE、Bearer、scope、resource/audience；受保护资源和授权服务器元数据发现；CIMD、预注册、DCR 兼容；令牌存取刷新、step-up、issuer 和重定向校验；区分客户端到 MCP 与 MCP 到下游 API 的凭据；stdio 的进程环境凭据。
10. **安全**：最小权限、服务端逐请求鉴权、多租户隔离、句柄归属；提示注入、工具描述投毒、内容和注解不可信；供应链和本地进程隔离；SSRF、DNS rebinding、confused deputy、token passthrough、凭据泄露和审计。
11. **工程化**：契约与集成测试、多宿主互操作、失败注入和模型选择工具的评测；连接与执行并发、限流、排队、背压、重试退避、幂等去重；网关、TLS、反向代理 SSE 缓冲与超时、水平扩展；OpenTelemetry、日志脱敏、延迟与错误指标；版本发布、Registry 元数据、文档和迁移策略。
12. **扩展、兼容与源码**：扩展标识和能力协商；Tasks 的 task 结果类型与 tasks/get、tasks/update、tasks/cancel、持久化和中途输入；MCP Apps 的界面资源、宿主通信和界面安全；Skills over MCP 的资源式发现与读取；OAuth Client Credentials 与 Enterprise-Managed Authorization；旧 initialize、session、GET 流、resources/subscribe、ping、tasks/result/list 和断线续传；Roots、Sampling、Logging、DCR 的弃用迁移；schema.ts、SDK 分层、协议实现与规范增强提案 SEP。

项目验收建议：同一服务器分别经 stdio 与 HTTP 调用并用 Inspector 解释报文；个人知识库服务器覆盖分页、Schema 和错误；自建宿主连接至少两个服务器并处理同名工具、超时和用户拒绝；授权远程服务完成 OAuth、两用户数据隔离、权限不足和令牌过期测试；长任务可轮询、取消、中途补充输入并在客户端重启后继续；对比旧版客户端验证迁移，确认重试不重复写入。注意：路线与项目验收是学习建议，不是规范要求所有应用实现全部可选能力。

信源（均一手）：[现行规范](https://modelcontextprotocol.io/specification/2026-07-28)、[架构](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)、[基础消息](https://modelcontextprotocol.io/specification/2026-07-28/basic)、[工具](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)、[资源](https://modelcontextprotocol.io/specification/2026-07-28/server/resources)、[提示模板](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts.md)、[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)、[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)、[MRTR](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr)、[订阅](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions.md)、[Elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)、[授权](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)、[安全最佳实践](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)、[扩展总览](https://modelcontextprotocol.io/extensions/overview)。

## 数据层无状态：每请求自带版本与能力

结论：MCP 数据层无状态。2026-07-28 规范中，每次请求在 `params._meta` 中必须包含 `io.modelcontextprotocol/protocolVersion` 与 `io.modelcontextprotocol/clientCapabilities`；客户端应附带 `clientInfo`；无可选客户端能力时，能力字段仍传 `{}`。因此，服务器处理请求时不依赖前一次请求建立的协议会话。

**无状态的准确边界**：

- 服务器必须实现 `server/discover`；客户端可以跳过发现，直接调用已知方法。发现请求不建立协议会话。
- 2025-11-25 及更早版本的 `initialize` 握手属于旧版兼容机制，不能混入新版演示。
- 「无状态」不表示客户端和服务器进程不能保存任何数据：客户端可以保存上下文，再把所需结果明确写入下一请求。MCP 不规定宿主如何管理模型上下文。
- `_meta` 是 MCP 约定的元数据（Metadata）容器，可出现在请求参数，也可出现在响应结果等规范允许的位置；`arguments` 承载工具业务输入。元数据是附带信息，但必需字段（版本、能力）不可删除。

**重启实验**：经 stdio 传输，父进程充当客户端，启动子进程充当服务器；每条 JSON-RPC 2.0 消息占一行，以换行符分帧；服务器收到输入结束后退出。流程：发现 → 列工具 → 调用加法得 5，随后关闭原服务器，启动全新进程，直接传入上一结果和新参数，仍得正确结果。

```text
客户端                      原服务器进程               新服务器进程
  |
  +--- id=1 server/discover --->   |
  |<--- 支持版本与 tools 能力 ---   |
  +--- id=2 tools/list ----------> |
  |<--- add 工具与参数定义 -----   |
  +--- id=3 tools/call a=2 b=3 --> |
  |<--- sum=5 ------------------   |
  |        客户端保存 5，关闭原服务器
  +-------------- id=4 tools/call a=5 b=10 -------------> |
  |<-------------------------- sum=15 -------------------- +
```

新服务器进程收到的第一条请求（它未收到任何历史请求，也未收到 `initialize`）：

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {"a": 5, "b": 10},
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {"name": "learning-client", "version": "1.0.0"},
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

响应 `id` 为 4，`resultType` 为 `complete`，`content` 含文本 `15`，`structuredContent` 为 `{"sum":15}`，`isError` 为 `false`。`id` 用于配对请求和响应，不是会话编号。

**修正记录**：初版捕获的发现与工具列表响应遗漏必填的 `ttlMs` 与 `cacheScope`，不能作为完整规范响应的范例——官方 `DiscoverResult`、`ListToolsResult` 都继承 `CacheableResult`。补齐后重跑仍得 5 和 15，八条捕获报文均通过所保存官方 Schema 的结构关键词校验。2026-10-29 复跑结果一致；本次未重新执行 Schema 校验，不扩展此前校验结论。

**实验限制**：运行结果来自本地教学实现，不代表完整实现了 MCP，也没有调用真实模型或外部服务。实验验证的是「协议字段和业务参数齐备时，全新服务器进程可以处理调用」；它没有验证所有工具都无需持久化业务数据，也没有验证失败重试的幂等性。

**完整报文参考**：MCP 各种消息结构不同，不能合成一条同时包含所有字段的有效报文。据此建立的参考册与逐字段附录（存于提问记录）覆盖官方核心 Schema 的 155 个类型定义、21 个固定方法名、517 项声明属性位置、56 个带具体数据的独立示例；517 含继承后在多个类型中重复出现的属性，不代表互异字段名。要点：

- 顶层客户端请求 10 种方法（发现、工具、资源、提示模板、参数补全、订阅等）。
- 内嵌补充输入 3 种方法；elicitation 分 form 与 url 示例；roots 与 sampling 在本版已弃用，不能按旧版作为独立服务器请求发送。
- 通知 8 个方法名，实际可用方向、所属请求和传输限制各异。
- 任意业务字段、供应商能力及独立扩展是开放集合，不能声称穷尽。
- `x-description-zh` 等是参考册注解，不是线上字段；JSON 键 `io.modelcontextprotocol/protocolVersion` 是一个完整名称，斜杠不产生对象嵌套。
- 工具执行失败通常用 `result.isError=true`；协议级失败用 `error`。缓存结果的 `ttlMs`（单位毫秒）与 `cacheScope` 是必填项。
- 本版顶层交互由客户端发起：服务器需要补充输入时，在 `resultType=input_required` 的结果内返回 `inputRequests`；客户端以新请求 id 重试并提交 `inputResponses`，原样回传 `requestState`。只有 `tools/call`、`resources/read`、`prompts/get` 支持这一中间结果。
- 订阅的确认是 `notifications/subscriptions/acknowledged`；最终 result 只在正常结束时返回。

信源（均一手）：[基础消息与每请求元数据](https://modelcontextprotocol.io/specification/2026-07-28/basic)、[版本与兼容](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)、[服务器发现](https://modelcontextprotocol.io/specification/2026-07-28/server/discover)、[工具](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)、[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)、[架构与宿主职责](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)、[类型源码](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2026-07-28/schema.ts)、[版本变更](https://modelcontextprotocol.io/specification/2026-07-28/changelog)。

## MCP 与 HTTP：消息层本体与传输绑定

结论：MCP 本质上不是 HTTP。本体是 JSON-RPC 2.0 消息层：请求、响应（结果或错误）、通知三类核心消息与消息模式（请求响应、MRTR、订阅通知）、每请求元数据都属于核心协议，所有实现必须支持，这一层不依赖任何网络协议。

传输是绑定（Binding）：只规定消息如何分帧、如何投递、取消与终止如何表达，不规定消息含义。规范明确「协议语义在每种传输上相同」，协议与传输无关（transport-agnostic），可在任何支持双向消息交换的通道上实现。

```text
+----------------------------------------------------+
| MCP 协议本体：JSON-RPC 2.0 消息                      |
| 请求 + 响应 + 通知 + 消息模式 + 每请求元数据           |
+--------------------------+-------------------------+
                           |
         +-----------------+------------------+
         |                 |                  |
   +-----+------+   +------+------+   +-------+------+
   | stdio 绑定 |   | Streamable  |   | 自定义绑定    |
   | 子进程标准流 |   | HTTP 绑定    |   | 任意双向通道  |
   | 换行分帧    |   | 单端点 POST  |   | 保留消息格式  |
   | 不含 HTTP   |   | JSON 或 SSE |   | 与元数据模型  |
   +------------+   +-------------+   +--------------+
```

- **stdio**：客户端启动子进程，消息走标准输入与标准输出，按换行分帧，全程不出现 HTTP。
- **Streamable HTTP**：每条消息是对单个 MCP 端点的 HTTP POST，响应为 JSON 对象或请求级服务器发送事件（Server-Sent Events，SSE）流。HTTP 只在这一绑定进入协议栈。
- **自定义传输**：必须保留 JSON-RPC 消息格式、消息模式与每请求元数据模型；运行在可靠双向字节流上的自定义传输应复用 stdio 分帧。

**为什么容易被当成 HTTP**：远程部署普遍使用 Streamable HTTP；授权框架（OAuth 2.x）只面向 HTTP 传输——HTTP 传输应遵循该框架，stdio 传输应从进程环境取凭据、不使用该框架；再加 SSE 流式响应，远程 MCP 看起来像「又一个 HTTP API」。但这些内容都位于传输绑定层，不在消息层本体。补充（领域综述）：HTTP 传输可以运行在本机；stdio 不强制串行；npx 只是启动命令，不是协议概念。

**JSON-RPC 2.0 是什么**：JSON-RPC 2.0 是无状态、轻量级的远程过程调用（Remote Procedure Call，RPC）协议，用 JSON 编码「调用远程方法」的消息；规范本身不规定传输层，同一进程、套接字、HTTP 均可承载。三类消息：

- **请求**：`method` 为方法名（`rpc.` 前缀保留）；`params` 可省略，可为按位置的数组或按名称的对象；`id` 由客户端建立，用于配对响应。
- **响应**：带与请求相同的 `id`；`result` 与 `error` 二选一，不得并存；检测不到请求 id 时（如解析错误），响应 `id` 为 null。
- **通知**：省略 `id` 的请求，服务器不得回复；1.0 用 `id: null` 表示通知，2.0 弃用该写法。

最小调用：

```json
{"jsonrpc": "2.0", "method": "add", "params": [2, 3], "id": 1}
{"jsonrpc": "2.0", "result": 5, "id": 1}
```

错误对象为 `{code, message, data?}`；-32700 至 -32603 为预定义错误（解析错误、无效请求、方法不存在、参数无效、内部错误）；-32000 至 -32099 保留给实现定义的服务器错误，MCP 在此范围内划出 -32020 至 -32099 为规范专用码。批处理：客户端可一次发送请求数组，服务器返回响应数组；响应顺序任意，靠 `id` 配对。版本信息：2.0 定稿于 2010-03-26，由 JSON-RPC Working Group 维护，是社区规范，不是 IETF RFC。MCP 选择它的原因：传输无关、结构极简、无状态，与「每请求自带元数据、不依赖会话」的模型一致；MCP 在其上加了自身规则——`id` 不得为 null，`result` 必须含 `resultType`。

信源（均一手）：[基础消息](https://modelcontextprotocol.io/specification/2026-07-28/basic)、[传输](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)、[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)、[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)、[JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)。
