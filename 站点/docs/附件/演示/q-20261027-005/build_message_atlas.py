"""Build a Chinese MCP reference from the preserved official 2026-07-28 schema."""

import base64
import copy
import io
import json
import math
import re
import wave
from pathlib import Path


HERE = Path(__file__).resolve().parent
RECORDS = HERE.parents[1]
SOURCE = RECORDS / "来源/mcp-2026-07-28-schema-20261027"
SCHEMA = json.loads((SOURCE / "schema.json").read_text(encoding="utf-8"))
DEFS = SCHEMA["$defs"]
VERSION = "2026-07-28"
BASE = "https://modelcontextprotocol.io/specification/2026-07-28"
RAW = "https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2026-07-28/schema.ts"

FIELD_ZH = {
    "$schema": "此对象采用的 JSON Schema 方言标识。",
    "_meta": "元数据容器；含义取决于所在对象，只有请求元数据要求每次携带版本与客户端能力。",
    "action": "用户处理补充输入的动作：accept 为提交或同意，decline 为拒绝，cancel 为取消；URL 同意不等于站外操作已完成。",
    "additionalProperties": "是否允许未列出的业务属性；也可以指定这些属性必须满足的 Schema。",
    "annotations": "展示、受众、重要性等提示；工具对象使用 ToolAnnotations，内容与资源使用 Annotations。",
    "anyOf": "至少满足一个候选 Schema；在多选表单中列出带标题的选项。",
    "argument": "本次需要补全的一个参数，含名称 name 和已输入前缀 value。",
    "arguments": "调用或模板的业务输入；工具参数是对象，提示模板与补全上下文中的参数值是字符串。",
    "audience": "预期受众列表，可含 user 和 assistant。",
    "blob": "资源二进制内容的 Base64 编码字符串。",
    "cacheScope": "缓存范围：public 可跨授权上下文共享；private 仅限同一授权上下文。",
    "capabilities": "服务器声明支持的能力；与请求中的客户端能力分别解释。",
    "code": "整数错误码；具体值由标准错误或 MCP 专用错误定义。",
    "completion": "参数补全结果，含候选值和是否还有更多候选。",
    "completions": "存在表示服务器支持 completion/complete 参数补全。",
    "const": "该选项或字段必须使用的固定值。",
    "content": "内容；工具结果中为内容块数组，提示消息中为单个内容块，采样中可为单块或数组，表单结果中为业务值对象。",
    "contents": "resources/read 返回的资源正文数组，可含文本或二进制。",
    "context": "补全场景是已知参数上下文；客户端采样能力中的同名字段表示支持 includeContext。",
    "costPriority": "采样选模型时对成本的重视程度，0 至 1；不是价格或概率。",
    "cursor": "服务器先前返回的分页游标；客户端原样回传，不解析其内容。",
    "data": "错误详情或日志数据；图像和音频内容块中则是 Base64 数据。",
    "default": "Schema 声明的默认值；不表示服务器可以跳过数据验证。",
    "description": "供人或模型理解的描述；其具体对象由所在类型确定。",
    "destructiveHint": "工具是否可能破坏性更新；仅在 readOnlyHint=false 时有意义，省略默认 true。",
    "elicitation": "声明客户端可以收集补充输入；form 和 url 分别表示支持的模式。",
    "enum": "允许取值的集合。",
    "enumNames": "旧式单选枚举的显示标题数组；与 enum 对应，保留用于兼容。",
    "error": "协议级错误对象；不能与同一响应的 result 同时使用。",
    "experimental": "实验性、非标准能力的名称到设置对象映射；实际名称由实现定义。",
    "extensions": "扩展标识到设置对象的映射；标识必须带命名空间，具体字段由对应扩展定义。",
    "form": "存在表示客户端支持表单补充输入。",
    "format": "字符串格式提示或约束，例如 email、uri、date、date-time；适用集合由具体 Schema 定义。",
    "hasMore": "是否还有未返回的补全候选。",
    "hints": "有序模型名称提示列表；客户端可按提示选择可用模型。",
    "icons": "图标数组，每项指定来源及可选格式、尺寸和主题。",
    "id": "JSON-RPC 请求编号及响应关联编号；ToolUseContent 内的同名字段则是模型工具调用编号。",
    "idempotentHint": "同参数重复执行是否不再增加环境影响；仅在非只读工具中有意义，省略默认 false。",
    "includeContext": "采样请求附带 MCP 上下文的范围；省略或使用 none，thisServer 与 allServers 已弃用。",
    "input": "采样消息中模型提出的工具调用输入，必须符合该工具 inputSchema。",
    "inputRequests": "服务端需要客户端补充的输入映射；键由服务端分配，值是内嵌输入请求。",
    "inputResponses": "重试原请求时返回的补充输入映射；键与先前 inputRequests 对应。",
    "inputSchema": "工具参数的 JSON Schema，根 type 必须为 object；未写 $schema 时默认 2020-12。",
    "instructions": "服务器提供给宿主或模型的使用指导。",
    "intelligencePriority": "采样选模型时对能力的重视程度，0 至 1。",
    "io.modelcontextprotocol/clientCapabilities": "本次请求声明的客户端能力，必填；空对象表示未声明可选能力。",
    "io.modelcontextprotocol/clientInfo": "客户端软件身份，规范推荐每请求附带；name 和 version 必填，其余展示信息可选。不是认证凭据。",
    "io.modelcontextprotocol/logLevel": "本请求愿意接收的最低日志级别；未指定时不得发送对应日志通知。Logging 已弃用。",
    "io.modelcontextprotocol/protocolVersion": "本次请求采用的 MCP 规范版本，必填；HTTP 时须与 MCP-Protocol-Version 头一致。",
    "io.modelcontextprotocol/serverInfo": "服务器软件身份，规范推荐每结果附带；不是经过验证的认证身份。",
    "io.modelcontextprotocol/subscriptionId": "关联订阅的编号，等于打开该订阅的 subscriptions/listen 请求 id。",
    "isError": "工具执行是否失败；省略默认 false。true 仍可出现在正常 JSON-RPC result 内。",
    "items": "数组元素的 Schema。",
    "jsonrpc": "JSON-RPC 版本标记，固定为 2.0；与 MCP 日期版本不同。",
    "lastModified": "资源最后修改时间，ISO 8601 字符串。",
    "level": "该日志消息的严重级别。",
    "listChanged": "服务器是否支持相应列表变化通知；客户端仍须显式订阅。",
    "logger": "日志来源名称，可选。",
    "logging": "服务器支持协议日志；该能力在本版中已弃用。",
    "maxItems": "表单多选最多选择的项数，单位为项。",
    "maxLength": "字符串最大长度，按 JSON Schema 字符计数。",
    "maxTokens": "采样生成的 token 数上限；客户端可以生成更少。",
    "maximum": "数值允许的最大值，含边界。",
    "message": "展示给用户的提示、进度文字或错误摘要；由所在类型确定。",
    "messages": "消息数组；提示结果用 PromptMessage，采样输入用 SamplingMessage。",
    "metadata": "传给模型提供商的自定义信息，格式由提供商约定；不同于 MCP 的 _meta。",
    "method": "操作或通知的方法名；客户端顶层请求与 MRTR 内嵌输入请求的信封不同。",
    "mimeType": "媒体类型，例如 text/plain、image/png、audio/wav。",
    "minItems": "表单多选至少选择的项数，单位为项。",
    "minLength": "字符串最小长度，按 JSON Schema 字符计数。",
    "minimum": "数值允许的最小值，含边界。",
    "mode": "elicitation 中为 form 或 url；ToolChoice 中为 auto、required 或 none。",
    "model": "实际用于生成采样结果的模型名称。",
    "modelPreferences": "服务端对采样模型的选择偏好，客户端可以忽略。",
    "name": "对象名称；在软件身份、工具、资源、参数、模型提示等对象中各有独立命名范围。",
    "nextCursor": "获取下一页的游标；没有此字段通常表示本列表已到末页。",
    "notifications": "订阅过滤器；确认通知内则为服务器实际接受的过滤器子集。",
    "oneOf": "恰好满足一个候选 Schema；在单选表单中列出值与显示标题。",
    "openWorldHint": "工具是否可能与开放的外部实体交互；省略默认 true。",
    "outputSchema": "工具 structuredContent 必须满足的输出 Schema；本版允许任意 JSON 值类型。",
    "params": "该方法或通知的参数对象。",
    "priority": "内容或资源的重要性提示，0 至 1；1 最重要，0 最不重要。",
    "progress": "已完成工作量，应递增；单位由该操作确定。",
    "progressToken": "请求中申请进度通知的标识；通知内原样回传，用于关联该请求。",
    "prompts": "提示模板列表，或服务器支持提示模板的能力对象。",
    "promptsListChanged": "是否订阅提示模板列表变化。",
    "properties": "对象业务字段名到 Schema 的映射；这些业务字段名称由该工具或表单定义。",
    "readOnlyHint": "工具是否不修改环境；省略默认 false。提示不构成安全保证。",
    "reason": "取消请求的可选人类可读原因。",
    "ref": "要补全的提示模板或资源模板引用。",
    "requestId": "要取消的 JSON-RPC 请求 id；不是 progressToken。",
    "requestState": "服务端返回的不透明字符串；客户端重试时原样回传，不解析或修改。",
    "requested": "客户端请求但服务器未支持的 MCP 协议版本。",
    "requestedSchema": "表单输入的受限 JSON Schema，仅允许顶层的基础字段和受支持枚举，不支持任意嵌套。",
    "required": "Schema 中为必填属性名列表；PromptArgument 中为该模板参数是否必填的布尔值。",
    "requiredCapabilities": "服务端处理本请求所需但客户端尚未声明的能力。",
    "resource": "嵌入的资源正文对象，可含 text 或 blob。",
    "resourceSubscriptions": "订阅更新的资源 URI 列表。",
    "resourceTemplates": "可参数化资源模板的列表。",
    "resources": "资源列表，或服务器资源能力对象；由所在类型确定。",
    "resourcesListChanged": "是否订阅资源列表变化。",
    "result": "响应结果对象；与 error 是不同分支。",
    "resultType": "结果分支：complete 为最终结果，input_required 为需要补充输入；扩展可另行定义。",
    "role": "消息角色，user 或 assistant。",
    "roots": "根目录列表；客户端能力中同名对象表示支持列根目录。Roots 已弃用。",
    "sampling": "客户端支持通过模型生成内容的能力；Sampling 已弃用。",
    "size": "资源正文大小，单位为字节。",
    "sizes": "图标尺寸列表，采用宽x高的像素形式，或 any 表示可缩放。",
    "speedPriority": "采样选模型时对低延迟的重视程度，0 至 1。",
    "src": "图标来源 URI；示例使用 HTTPS。",
    "stopReason": "采样停止原因，例如 endTurn、stopSequence、maxTokens、toolUse；允许提供商扩展。",
    "stopSequences": "遇到后应停止生成的字符串序列列表。",
    "structuredContent": "结构化工具结果；本版可为对象、数组、字符串、数值、布尔值或 null。",
    "subscribe": "服务器是否支持针对资源 URI 的更新通知。",
    "supported": "服务器支持的 MCP 协议版本列表，用于版本错误响应。",
    "supportedVersions": "服务器发现结果中支持的 MCP 协议版本列表。",
    "systemPrompt": "服务端建议的采样系统提示，客户端可修改或省略。",
    "temperature": "采样温度；可接受范围由模型提供商确定，MCP 不在此统一规定。",
    "text": "明文文本正文。",
    "theme": "图标适用背景主题：light 或 dark；省略表示不限定。",
    "title": "面向用户的显示标题；不同于用于调用的 name。",
    "toolChoice": "控制采样中的模型工具选择策略。",
    "toolUseId": "对应先前 ToolUseContent.id 的工具调用编号。",
    "tools": "工具定义列表、服务器工具能力或客户端采样工具能力；由所在类型确定。",
    "toolsListChanged": "是否订阅工具列表变化。",
    "total": "进度通知中为总工作量；补全结果中为全部候选数量，含未返回部分。",
    "ttlMs": "缓存保鲜时间提示，单位为毫秒；0 表示立即过期，不是请求执行超时。",
    "type": "内容块或引用的类型判别符；Schema 对象内则表示其数据类型。",
    "uri": "资源、根目录或资源模板引用的统一资源标识符。",
    "uriTemplate": "带变量占位符的资源 URI 模板。",
    "url": "URL 模式的站外交互地址；客户端能力对象中表示支持该模式。",
    "value": "用户已输入、用于匹配补全候选的字符串前缀。",
    "values": "本次返回的补全候选字符串数组，最多 100 项。",
    "version": "客户端或服务器软件版本；与日期形式的 MCP 协议版本不同。",
    "websiteUrl": "实现的官方网站地址，可选。",
}

TYPE_ZH = {
    "Discover": "服务器发现", "ListTools": "工具列表", "CallTool": "工具调用",
    "ListResources": "资源列表", "ReadResource": "读取资源",
    "ListResourceTemplates": "资源模板列表", "ListPrompts": "提示模板列表",
    "GetPrompt": "获取提示模板", "Complete": "参数补全",
    "SubscriptionsListen": "监听订阅", "CreateMessage": "模型采样（已弃用）",
    "Elicit": "补充用户输入", "ListRoots": "列出根目录（已弃用）",
    "RequestMetaObject": "请求元数据", "ResultMetaObject": "结果元数据",
    "NotificationMetaObject": "通知元数据", "ClientCapabilities": "客户端能力",
    "ServerCapabilities": "服务器能力", "Implementation": "客户端或服务器软件信息",
    "Tool": "工具定义", "Resource": "资源定义", "ResourceTemplate": "资源模板定义",
    "Prompt": "提示模板定义", "Annotations": "内容与资源的提示注解",
    "ToolAnnotations": "工具行为提示注解", "SubscriptionFilter": "订阅过滤器",
    "InputRequiredResult": "需要补充输入的中间结果", "Icon": "显示图标",
    "TextContent": "文本内容块", "ImageContent": "图像内容块", "AudioContent": "音频内容块",
    "ResourceLink": "资源链接内容块", "EmbeddedResource": "内嵌资源内容块",
    "ToolUseContent": "采样中的模型工具调用（已弃用）",
    "ToolResultContent": "采样中的工具返回（已弃用）",
    "StringSchema": "表单字符串字段规则", "NumberSchema": "表单数值字段规则",
    "BooleanSchema": "表单布尔字段规则", "LegacyTitledEnumSchema": "旧式带显示标题的单选字段规则",
    "TitledSingleSelectEnumSchema": "带显示标题的单选字段规则",
    "TitledMultiSelectEnumSchema": "带显示标题的多选字段规则",
    "UntitledSingleSelectEnumSchema": "无独立显示标题的单选字段规则",
    "UntitledMultiSelectEnumSchema": "无独立显示标题的多选字段规则",
    "JSONObject": "任意 JSON 对象", "JSONArray": "任意 JSON 数组", "JSONValue": "任意 JSON 值",
    "MetaObject": "开放的元数据键值映射", "InputRequests": "服务端要求补充的输入映射",
    "InputResponses": "客户端提交的补充输入映射", "RequestId": "字符串或整数请求编号",
    "ProgressToken": "字符串或整数进度关联标识", "Cursor": "不透明分页游标字符串",
    "Error": "协议错误详情", "Result": "通用结果", "EmptyResult": "仅表示完成的结果",
    "Role": "用户或助手角色", "ResultType": "结果分支标识", "LoggingLevel": "日志级别枚举（已弃用）",
    "BaseMetadata": "对象的程序名称与显示标题", "Icons": "图标集合",
    "ResourceContents": "资源正文的公共标识与媒体类型", "TextResourceContents": "文本资源正文",
    "BlobResourceContents": "Base64 编码的二进制资源正文", "PromptArgument": "提示模板参数定义",
    "PromptMessage": "提示模板返回的单条消息", "PromptReference": "参数补全所引用的提示模板",
    "ResourceTemplateReference": "参数补全所引用的资源模板", "Root": "根目录 URI 与名称（已弃用）",
    "SamplingMessage": "模型采样的输入或输出消息（已弃用）", "SamplingMessageContentBlock": "采样消息可使用的内容块联合类型（已弃用）",
    "ModelHint": "模型名称选择提示（已弃用）", "ModelPreferences": "模型选择偏好（已弃用）",
    "ToolChoice": "采样中的模型工具选择策略（已弃用）", "ContentBlock": "工具与提示可使用的五类内容块联合类型",
    "Request": "尚未添加 JSON-RPC 信封的通用请求结构", "RequestParams": "顶层客户端请求的公共元数据参数",
    "Notification": "尚未添加 JSON-RPC 版本的通用通知结构", "NotificationParams": "通知公共参数",
    "JSONRPCRequest": "客户端顶层请求信封，含版本、id、方法和参数",
    "JSONRPCNotification": "无 id 且不要求响应的通知信封",
    "JSONRPCResultResponse": "成功结果响应信封，与 error 分支互斥",
    "JSONRPCErrorResponse": "协议错误响应信封，与 result 分支互斥",
    "JSONRPCResponse": "结果响应或错误响应的联合类型", "JSONRPCMessage": "顶层请求、通知与响应的联合类型",
    "ClientRequest": "十种客户端顶层请求的联合类型", "ClientNotification": "客户端可发送的取消通知类型",
    "ClientResult": "通用空结果别名；不代表新版允许客户端独立发送 JSON-RPC 响应",
    "ServerResult": "服务器可返回的结果类型集合", "ServerNotification": "服务器通知类型联合；实际方向还须遵守消息模式与传输规范",
    "InputRequest": "三类内嵌补充输入请求的联合类型", "InputResponse": "三类补充输入答复的联合类型",
    "InputResponseRequestParams": "支持多轮补充输入的请求公共参数",
    "PaginatedRequest": "支持分页的请求信封", "PaginatedRequestParams": "分页请求的公共参数",
    "PaginatedResult": "包含可选下一页游标的公共结果", "CacheableResult": "带必填缓存时间与缓存范围的结果",
    "ResourceRequestParams": "按 URI 指定资源的公共请求参数",
    "SubscriptionsListenResultMetaObject": "订阅关闭结果的元数据，含必填订阅编号",
    "ElicitRequestParams": "表单模式与 URL 模式参数的联合类型",
    "ElicitRequestFormParams": "表单模式补充输入的参数", "ElicitRequestURLParams": "URL 模式站外交互参数",
    "PrimitiveSchemaDefinition": "表单允许的基础字段与枚举规则联合类型",
    "EnumSchema": "表单枚举规则联合类型", "SingleSelectEnumSchema": "表单单选规则联合类型",
    "MultiSelectEnumSchema": "表单多选规则联合类型", "ParseError": "JSON 解析错误，代码 -32700",
    "InvalidRequestError": "无效请求错误，代码 -32600", "MethodNotFoundError": "未知方法错误，代码 -32601",
    "InvalidParamsError": "无效参数错误，代码 -32602", "InternalError": "内部错误，代码 -32603",
    "HeaderMismatchError": "HTTP 头缺失、无效或头体不一致的错误响应，代码 -32020",
    "MissingRequiredClientCapabilityError": "缺少所需客户端能力的错误响应，代码 -32021",
    "UnsupportedProtocolVersionError": "协议版本不支持的错误响应，代码 -32022",
}

FIELD_OVERRIDES = {
    ("CallToolRequestParams", "arguments"): "传给目标工具的业务参数对象；字段及必填性由该工具 inputSchema 定义。",
    ("GetPromptRequestParams", "arguments"): "提示模板参数名到字符串值的映射；与工具参数的任意 JSON 值不同。",
    ("CallToolResult", "content"): "工具非结构化结果的内容块数组，元素引用 ContentBlock。",
    ("ElicitResult", "content"): "用户提交的表单字段值；仅 action=accept 且为 form 模式时出现。",
    ("PromptMessage", "content"): "单个 ContentBlock 对象；本类型的 content 不是数组。",
    ("SamplingMessage", "content"): "单个采样内容块或采样内容块数组；可含 tool_use 和 tool_result。",
    ("CreateMessageResult", "content"): "生成的单个采样内容块或数组；不是 JSON-RPC result 信封。",
    ("ImageContent", "data"): "图像字节的 Base64 编码字符串；实际图像格式与 mimeType 一致。",
    ("AudioContent", "data"): "音频字节的 Base64 编码字符串；实际音频格式与 mimeType 一致。",
    ("Error", "data"): "可选的附加错误详情，允许任意 JSON 值；部分 MCP 专用错误规定具体形状。",
    ("ProgressNotificationParams", "total"): "预期总工作量，单位与 progress 相同；不是固定的百分比。",
    ("Implementation", "name"): "客户端或服务器软件的程序名称，例如 learning-client。",
    ("Tool", "name"): "服务器内用于 tools/call 的工具标识名称。",
    ("Prompt", "name"): "服务器内用于 prompts/get 的提示模板名称。",
    ("PromptArgument", "required"): "该提示模板参数是否必填；此处是布尔值，不是 JSON Schema 的 required 数组。",
    ("ClientCapabilities", "tools"): "采样能力内的此字段表示客户端支持模型工具调用；不是服务器 tools 能力。",
}


def field_description(owner, key):
    return FIELD_OVERRIDES.get((owner, key), FIELD_ZH[key])


def type_description(name):
    if name in TYPE_ZH:
        return TYPE_ZH[name]
    for suffix, label in [
        ("RequestParams", "请求参数"), ("ResultResponse", "JSON-RPC 成功响应"),
        ("Request", "请求结构"), ("Result", "结果结构"),
    ]:
        if name.endswith(suffix):
            stem = name[:-len(suffix)]
            return TYPE_ZH.get(stem, stem) + "：" + label
    if name.endswith("NotificationParams"):
        return name[:-len("NotificationParams")] + " 通知参数"
    if name.endswith("Notification"):
        return name[:-len("Notification")] + " 通知结构"
    return "协议类型 " + name + "；字段定义与引用见本节。"


def type_expr(node):
    if "$ref" in node:
        return node["$ref"].split("/")[-1]
    if "const" in node:
        return json.dumps(node["const"], ensure_ascii=False)
    if "enum" in node:
        return " | ".join(json.dumps(v, ensure_ascii=False) for v in node["enum"])
    for union in ("anyOf", "oneOf", "allOf"):
        if union in node:
            return (" & " if union == "allOf" else " | ").join(type_expr(v) for v in node[union])
    if node.get("type") == "array":
        return "array<" + type_expr(node.get("items", {})) + ">"
    return str(node.get("type", "任意 JSON 值"))


def check(value, definition, path="$"):
    """Validate the structural keywords used by the preserved official schema.

    Formats remain annotations, as allowed by JSON Schema 2020-12. Protocol
    sequencing and business rules receive separate assertions below.
    """
    if definition is True:
        return
    if definition is False:
        raise ValueError(path + ": forbidden value")
    if "$ref" in definition:
        ref = definition["$ref"]
        assert ref.startswith("#/$defs/"), ref
        check(value, DEFS[ref.split("/")[-1]], path)
    if "anyOf" in definition or "oneOf" in definition:
        keyword = "anyOf" if "anyOf" in definition else "oneOf"
        passed = 0
        for branch in definition[keyword]:
            try:
                check(value, branch, path)
                passed += 1
            except ValueError:
                pass
        if passed == 0 or (keyword == "oneOf" and passed != 1):
            raise ValueError(path + ": no matching " + keyword + " branch")
    for branch in definition.get("allOf", []):
        check(value, branch, path)
    kind = definition.get("type")
    kinds = kind if isinstance(kind, list) else [kind] if kind else []
    valid = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str), "integer": type(value) is int,
             "number": type(value) in (int, float) and math.isfinite(value),
             "boolean": type(value) is bool, "null": value is None}
    if kinds and not any(valid[k] for k in kinds):
        raise ValueError(path + ": expected " + str(kind))
    if "const" in definition and value != definition["const"]:
        raise ValueError(path + ": wrong constant")
    if "enum" in definition and value not in definition["enum"]:
        raise ValueError(path + ": wrong enum")
    if isinstance(value, dict):
        for key in definition.get("required", []):
            if key not in value:
                raise ValueError(path + ": missing " + key)
        properties = definition.get("properties", {})
        for key, val in value.items():
            if key in properties:
                check(val, properties[key], path + "." + key)
            elif "additionalProperties" in definition:
                check(val, definition["additionalProperties"], path + "." + key)
    if isinstance(value, list):
        for index, item in enumerate(value):
            check(item, definition.get("items", {}), path + f"[{index}]")
        if len(value) < definition.get("minItems", 0) or len(value) > definition.get("maxItems", math.inf):
            raise ValueError(path + ": array length")
    if isinstance(value, str):
        if len(value) < definition.get("minLength", 0) or len(value) > definition.get("maxLength", math.inf):
            raise ValueError(path + ": string length")
    if type(value) in (int, float):
        if value < definition.get("minimum", -math.inf) or value > definition.get("maximum", math.inf):
            raise ValueError(path + ": numeric range")


EXAMPLES = []


def example(label, type_name, value, note=""):
    check(value, DEFS[type_name], label)
    EXAMPLES.append({"名称": label, "官方类型": type_name, "说明": note, "data": value})
    return value


def request(number, method, **params):
    return {"jsonrpc": "2.0", "id": number, "method": method,
            "params": {**params, "_meta": copy.deepcopy(REQUEST_META)}}


def response(number, **result):
    return {"jsonrpc": "2.0", "id": number,
            "result": {"resultType": "complete", **result,
                       "_meta": copy.deepcopy(RESULT_META)}}


def notification(method, **params):
    return {"jsonrpc": "2.0", "method": method, "params": params}


ICON = {"src": "https://example.com/mcp/icon.png", "mimeType": "image/png",
        "sizes": ["48x48", "96x96"], "theme": "light"}
CLIENT_INFO = {"name": "learning-client", "title": "学习客户端", "version": "1.0.0",
               "description": "用于说明字段的虚构客户端", "websiteUrl": "https://example.com/client",
               "icons": [ICON]}
SERVER_INFO = {**CLIENT_INFO, "name": "learning-server", "title": "学习服务器",
               "description": "用于说明字段的虚构服务器", "websiteUrl": "https://example.com/server"}
CLIENT_CAPS = {"experimental": {}, "extensions": {}, "elicitation": {"form": {}, "url": {}},
               "roots": {}, "sampling": {"context": {}, "tools": {}}}
SERVER_CAPS = {"experimental": {}, "extensions": {}, "tools": {"listChanged": True},
               "resources": {"listChanged": True, "subscribe": True},
               "prompts": {"listChanged": True}, "completions": {}, "logging": {}}
REQUEST_META = {"io.modelcontextprotocol/protocolVersion": VERSION,
                "io.modelcontextprotocol/clientInfo": CLIENT_INFO,
                "io.modelcontextprotocol/clientCapabilities": CLIENT_CAPS,
                "progressToken": "progress-demo",
                "io.modelcontextprotocol/logLevel": "info",
                "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
                "tracestate": "demo=example", "baggage": "demo=learning",
                "com.example/demoTag": "教学自定义字段"}
RESULT_META = {"io.modelcontextprotocol/serverInfo": SERVER_INFO,
               "com.example/demoTag": "教学自定义字段"}
ANNOTATIONS = {"audience": ["user", "assistant"], "priority": 0.8,
               "lastModified": "2026-10-27T08:00:00Z"}
TOOL = {"name": "add", "title": "整数加法", "description": "返回两个整数的和。", "icons": [ICON],
        "inputSchema": {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                        "properties": {"a": {"type": "integer", "x-mcp-header": "A"},
                                       "b": {"type": "integer"}},
                        "required": ["a", "b"], "additionalProperties": False},
        "outputSchema": {"type": "object", "properties": {"sum": {"type": "integer"}}, "required": ["sum"]},
        "annotations": {"title": "加法", "readOnlyHint": True, "destructiveHint": False,
                        "idempotentHint": True, "openWorldHint": False},
        "_meta": {"com.example/category": "math"}}
RESOURCE = {"uri": "file:///project/readme.txt", "name": "readme.txt", "title": "项目说明",
            "description": "虚构资源", "mimeType": "text/plain", "size": 12,
            "icons": [ICON], "annotations": ANNOTATIONS, "_meta": {"com.example/tag": "demo"}}
TEMPLATE = {key: val for key, val in RESOURCE.items() if key not in ("uri", "size")}
TEMPLATE.update(name="project_file", uriTemplate="file:///project/{path}")
PROMPT = {"name": "summarize", "title": "摘要", "description": "总结所给主题", "icons": [ICON],
          "arguments": [{"name": "topic", "title": "主题", "description": "需要总结的主题", "required": True}],
          "_meta": {"com.example/tag": "demo"}}
TEXT = {"type": "text", "text": "5", "annotations": ANNOTATIONS, "_meta": {"com.example/tag": "demo"}}
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aD1kAAAAASUVORK5CYII="
audio = io.BytesIO()
with wave.open(audio, "wb") as wav:
    wav.setparams((1, 1, 8000, 0, "NONE", "not compressed"))
    wav.writeframes(bytes([128]) * 80)
AUDIO = base64.b64encode(audio.getvalue()).decode("ascii")


def build_examples():
    example("发现服务器请求", "DiscoverRequest", request(1, "server/discover"))
    example("发现服务器响应", "DiscoverResultResponse", response(1, supportedVersions=[VERSION],
            capabilities=SERVER_CAPS, instructions="按工具定义传入参数。", ttlMs=300000, cacheScope="public"))
    example("工具列表请求", "ListToolsRequest", request(2, "tools/list", cursor="opaque-page-2"),
            "cursor 只在读取后续页时提供；这里假定客户端已持有前页游标。")
    example("工具列表响应", "ListToolsResultResponse", response(2, tools=[TOOL], nextCursor="opaque-page-3", ttlMs=300000, cacheScope="public"))
    example("工具调用请求", "CallToolRequest", request(3, "tools/call", name="add", arguments={"a": 2, "b": 3}))
    example("工具调用成功响应", "CallToolResultResponse", response(3, content=[TEXT], structuredContent={"sum": 5}, isError=False))
    example("工具执行失败结果", "CallToolResultResponse", response(30, content=[{"type": "text", "text": "下游服务暂不可用。"}], isError=True),
            "与协议级 error 分支不同；完整示例用于一般工具失败，非上面纯加法的实测结果。")
    example("资源列表请求", "ListResourcesRequest", request(4, "resources/list", cursor="opaque-page-2"))
    example("资源列表响应", "ListResourcesResultResponse", response(4, resources=[RESOURCE], nextCursor="opaque-page-3", ttlMs=60000, cacheScope="private"))
    example("资源模板列表请求", "ListResourceTemplatesRequest", request(5, "resources/templates/list", cursor="opaque-page-2"))
    example("资源模板列表响应", "ListResourceTemplatesResultResponse", response(5, resourceTemplates=[TEMPLATE], nextCursor="opaque-page-3", ttlMs=300000, cacheScope="public"))
    example("读取资源请求", "ReadResourceRequest", request(6, "resources/read", uri=RESOURCE["uri"]))
    example("读取资源响应", "ReadResourceResultResponse", response(6, contents=[
        {"uri": RESOURCE["uri"], "mimeType": "text/plain", "text": "Hello world!", "_meta": {"com.example/tag": "demo"}},
        {"uri": "file:///project/pixel.png", "mimeType": "image/png", "blob": PNG, "_meta": {"com.example/tag": "demo"}}
    ], ttlMs=60000, cacheScope="private"))
    example("提示模板列表请求", "ListPromptsRequest", request(7, "prompts/list", cursor="opaque-page-2"))
    example("提示模板列表响应", "ListPromptsResultResponse", response(7, prompts=[PROMPT], nextCursor="opaque-page-3", ttlMs=300000, cacheScope="public"))
    example("获取提示模板请求", "GetPromptRequest", request(8, "prompts/get", name="summarize", arguments={"topic": "MCP"}))
    example("获取提示模板响应", "GetPromptResultResponse", response(8, description="已填入主题的摘要提示", messages=[{"role": "user", "content": {"type": "text", "text": "请总结 MCP。"}}]))
    example("提示参数补全请求", "CompleteRequest", request(9, "completion/complete", ref={"type": "ref/prompt", "name": "summarize", "title": "摘要"}, argument={"name": "topic", "value": "MC"}, context={"arguments": {"language": "zh"}}))
    example("资源模板参数补全请求", "CompleteRequest", request(19, "completion/complete", ref={"type": "ref/resource", "uri": TEMPLATE["uriTemplate"]}, argument={"name": "path", "value": "rea"}, context={"arguments": {}}))
    example("参数补全响应", "CompleteResultResponse", response(9, completion={"values": ["MCP"], "total": 1, "hasMore": False}))
    filters = {"toolsListChanged": True, "promptsListChanged": True, "resourcesListChanged": True, "resourceSubscriptions": [RESOURCE["uri"]]}
    example("订阅请求", "SubscriptionsListenRequest", request(10, "subscriptions/listen", notifications=filters))
    subscription_meta = {"io.modelcontextprotocol/subscriptionId": 10}
    example("订阅确认通知", "SubscriptionsAcknowledgedNotification", notification("notifications/subscriptions/acknowledged", notifications=filters, _meta=subscription_meta), "这是订阅建立后的首条关联通知。")
    for label, type_name, method in [
        ("工具列表变化通知", "ToolListChangedNotification", "notifications/tools/list_changed"),
        ("资源列表变化通知", "ResourceListChangedNotification", "notifications/resources/list_changed"),
        ("提示模板列表变化通知", "PromptListChangedNotification", "notifications/prompts/list_changed"),
    ]:
        example(label, type_name, notification(method, _meta=subscription_meta))
    example("资源更新通知", "ResourceUpdatedNotification", notification("notifications/resources/updated", uri=RESOURCE["uri"], _meta=subscription_meta))
    closed = response(10)
    closed["result"]["_meta"].update(subscription_meta)
    example("订阅正常结束响应", "SubscriptionsListenResultResponse", closed, "只在订阅正常关闭时发送；确认通知不是最终响应。")
    example("进度通知", "ProgressNotification", notification("notifications/progress", progressToken="progress-demo", progress=50, total=100, message="已处理 50 项，共 100 项。", _meta={}), "单位为项；进度通知不需要订阅编号。")
    example("日志通知（已弃用）", "LoggingMessageNotification", notification("notifications/message", level="info", logger="demo", data={"stage": "running"}, _meta={}), "本例请求设置了 logLevel；未设置时不能收到对应日志。")
    example("取消通知（stdio）", "CancelledNotification", notification("notifications/cancelled", requestId=20, reason="用户取消", _meta={}), "示例假定 id=20 尚在执行；HTTP 使用关闭响应流取消。")

    form_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "properties": {
        "label": {"type": "string", "title": "名称", "description": "结果名称", "minLength": 1, "maxLength": 40, "default": "sum"},
        "count": {"type": "integer", "title": "份数", "description": "需要的份数", "minimum": 1, "maximum": 10, "default": 1},
        "confirm": {"type": "boolean", "title": "确认", "description": "是否继续", "default": True},
        "plain": {"type": "string", "title": "语言", "description": "选择语言", "enum": ["zh", "en"], "default": "zh"},
        "labeled": {"type": "string", "title": "模式", "description": "选择模式", "oneOf": [{"const": "fast", "title": "快速"}, {"const": "full", "title": "完整"}], "default": "fast"},
        "legacy": {"type": "string", "title": "旧式模式", "description": "仅演示兼容", "enum": ["a", "b"], "enumNames": ["甲", "乙"], "default": "a"},
        "tags": {"type": "array", "title": "标签", "description": "可多选", "items": {"type": "string", "enum": ["math", "demo"]}, "minItems": 1, "maxItems": 2, "default": ["math"]},
        "namedTags": {"type": "array", "title": "带标题标签", "description": "可多选", "items": {"anyOf": [{"const": "math", "title": "数学"}, {"const": "demo", "title": "演示"}]}, "minItems": 1, "maxItems": 2, "default": ["math"]},
        "email": {"type": "string", "title": "联系邮箱", "description": "用于本次联系", "format": "email", "default": "learner@example.com"}
    }, "required": ["confirm"]}
    form_input = {"method": "elicitation/create", "params": {"mode": "form", "message": "请选择本次演示参数。", "requestedSchema": form_schema}}
    url_input = {"method": "elicitation/create", "params": {"mode": "url", "message": "请在站外完成配置。", "url": "https://example.com/setup"}}
    roots_input = {"method": "roots/list", "params": {}}
    sampling_input = {"method": "sampling/createMessage", "params": {
        "messages": [{"role": "user", "content": {"type": "text", "text": "请概括 MCP。"}, "_meta": {}}],
        "modelPreferences": {"hints": [{"name": "example-model"}], "costPriority": 0.2, "speedPriority": 0.5, "intelligencePriority": 0.8},
        "systemPrompt": "请简洁回答。", "includeContext": "none", "temperature": 0.2, "maxTokens": 128,
        "stopSequences": ["END"], "metadata": {}, "tools": [TOOL], "toolChoice": {"mode": "auto"}
    }}
    for label, kind, value in [("表单补充输入", "ElicitRequest", form_input), ("URL 补充输入", "ElicitRequest", url_input), ("根目录输入（已弃用）", "ListRootsRequest", roots_input), ("模型采样输入（已弃用）", "CreateMessageRequest", sampling_input)]:
        example(label, kind, value, "这是 result.inputRequests 内的对象，不是独立的 JSON-RPC 顶层报文。")
    original = request(40, "tools/call", name="add", arguments={"a": 2, "b": 3})
    example("MRTR 原始请求", "CallToolRequest", original)
    interim = response(40, inputRequests={"form": form_input, "url": url_input, "roots": roots_input, "sample": sampling_input}, requestState="opaque-state-from-server")
    interim["result"]["resultType"] = "input_required"
    example("MRTR 中间响应", "CallToolResultResponse", interim, "为覆盖字段，合并多个可选输入；真实应用只请求所需输入。")
    retry = request(41, "tools/call", name="add", arguments={"a": 2, "b": 3}, requestState="opaque-state-from-server", inputResponses={
        "form": {"action": "accept", "content": {"confirm": True}}, "url": {"action": "accept"},
        "roots": {"roots": [{"uri": "file:///project", "name": "项目", "_meta": {}}]},
        "sample": {"role": "assistant", "content": {"type": "text", "text": "MCP 统一上下文交换。"}, "model": "example-model", "stopReason": "endTurn", "_meta": {}}
    })
    example("MRTR 重试请求", "CallToolRequest", retry, "使用新 id=41；requestState 原样回传。")
    example("MRTR 最终响应", "CallToolResultResponse", response(41, content=[TEXT], structuredContent={"sum": 5}, isError=False))
    for action in ["decline", "cancel"]:
        example("补充输入结果：" + action, "ElicitResult", {"action": action})

    content_examples = [
        ("文本内容", "TextContent", TEXT),
        ("图像内容", "ImageContent", {"type": "image", "data": PNG, "mimeType": "image/png", "annotations": ANNOTATIONS, "_meta": {}}),
        ("音频内容", "AudioContent", {"type": "audio", "data": AUDIO, "mimeType": "audio/wav", "annotations": ANNOTATIONS, "_meta": {}}),
        ("资源链接内容", "ResourceLink", {**RESOURCE, "type": "resource_link"}),
        ("内嵌文本资源", "EmbeddedResource", {"type": "resource", "resource": {"uri": RESOURCE["uri"], "mimeType": "text/plain", "text": "Hello world!", "_meta": {}}, "annotations": ANNOTATIONS, "_meta": {}}),
        ("内嵌二进制资源", "EmbeddedResource", {"type": "resource", "resource": {"uri": "file:///project/pixel.png", "mimeType": "image/png", "blob": PNG, "_meta": {}}, "annotations": ANNOTATIONS, "_meta": {}}),
        ("采样工具调用内容（已弃用）", "ToolUseContent", {"type": "tool_use", "id": "use-1", "name": "add", "input": {"a": 2, "b": 3}, "_meta": {}}),
        ("采样工具结果内容（已弃用）", "ToolResultContent", {"type": "tool_result", "toolUseId": "use-1", "content": [TEXT], "structuredContent": {"sum": 5}, "isError": False, "_meta": {}}),
    ]
    for label, kind, value in content_examples:
        example(label, kind, value, "嵌套内容对象；不可把它当作独立 MCP 顶层报文。")

    errors = [("ParseError", -32700, "Parse error"), ("InvalidRequestError", -32600, "Invalid Request"),
              ("MethodNotFoundError", -32601, "Method not found"), ("InvalidParamsError", -32602, "Invalid params"),
              ("InternalError", -32603, "Internal error")]
    for kind, code, message in errors:
        err = {"jsonrpc": "2.0", "error": {"code": code, "message": message, "data": {"detail": "虚构错误详情"}}}
        if code != -32700:
            err["id"] = 50
        example(message + " 协议错误响应", "JSONRPCErrorResponse", err,
                "解析失败无法识别请求编号时省略 id；不使用 null。")
    for label, kind, code, data in [
        ("HTTP 头体不一致错误", "HeaderMismatchError", -32020, {"header": "MCP-Protocol-Version"}),
        ("缺少客户端能力错误", "MissingRequiredClientCapabilityError", -32021, {"requiredCapabilities": {"elicitation": {"form": {}}}}),
        ("协议版本不支持错误", "UnsupportedProtocolVersionError", -32022, {"supported": [VERSION], "requested": "1900-01-01"}),
    ]:
        example(label, kind, {"jsonrpc": "2.0", "id": 50, "error": {"code": code, "message": label, "data": data}})
    assert retry["id"] != original["id"]
    assert retry["params"]["requestState"] == interim["result"]["requestState"]
    assert set(retry["params"]["inputResponses"]) == set(interim["result"]["inputRequests"])


def annotate(node, path, fields, owner):
    if not isinstance(node, dict):
        return
    required = node.get("required", [])
    for key, field in node.get("properties", {}).items():
        if key not in FIELD_ZH:
            raise KeyError("No Chinese explanation for " + key)
        description = field_description(owner, key)
        field["x-description-zh"] = description
        field["x-required-in-parent"] = key in required
        field_path = path + "." + key
        constraints = {k: v for k, v in field.items() if k in ("minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems", "const", "enum", "default")}
        fields.append({"path": field_path, "type": type_expr(field), "required": key in required,
                       "说明": description, "constraints": constraints})
        annotate(field, field_path, fields, owner)
    if isinstance(node.get("items"), dict):
        annotate(node["items"], path + "[]", fields, owner)
    if isinstance(node.get("additionalProperties"), dict):
        annotate(node["additionalProperties"], path + "[任意键]", fields, owner)
    for keyword in ("anyOf", "oneOf", "allOf"):
        for index, branch in enumerate(node.get(keyword, [])):
            annotate(branch, path + f"〈{keyword}分支{index + 1}〉", fields, owner)


def main():
    build_examples()
    negative_checks = []
    for label, kind, value in [
        ("缓存结果缺少 ttlMs", "ListToolsResultResponse", response(2, tools=[TOOL], cacheScope="public")),
        ("缓存结果缺少 cacheScope", "DiscoverResultResponse", response(1, capabilities=SERVER_CAPS, supportedVersions=[VERSION], ttlMs=300000)),
    ]:
        try:
            check(value, DEFS[kind], label)
        except ValueError:
            negative_checks.append(label)
        else:
            raise AssertionError(label + " was not rejected")
    missing_meta = request(99, "tools/list")
    del missing_meta["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"]
    try:
        check(missing_meta, DEFS["ListToolsRequest"])
    except ValueError:
        negative_checks.append("请求缺少客户端能力")
    else:
        raise AssertionError("Missing request capability was not rejected")
    # Ensure complete coverage of every literal method in the official core schema.
    expected = {v.get("properties", {}).get("method", {}).get("const") for v in DEFS.values()}
    expected.discard(None)
    actual = {ex["data"]["method"] for ex in EXAMPLES if "method" in ex["data"]}
    assert expected == actual, (expected - actual, actual - expected)
    annotated = copy.deepcopy(DEFS)
    type_source = (SOURCE / "schema.ts").read_text(encoding="utf-8")
    deprecated = set()
    for declaration in re.finditer(r"export (?:interface|type) (\w+)", type_source):
        before = type_source[:declaration.start()].rstrip()
        if before.endswith("*/"):
            comment = before[before.rfind("/**"):]
            if "@deprecated" in comment:
                deprecated.add(declaration[1])
    field_guide = {}
    for name, node in annotated.items():
        node["x-description-zh"] = type_description(name)
        node["x-status"] = "已弃用" if name in deprecated else "保留；适用条件见所在类型"
        fields = []
        annotate(node, "$", fields, name)
        field_guide[name] = fields
    def strip_annotations(node):
        if isinstance(node, dict):
            return {key: strip_annotations(value) for key, value in node.items()
                    if key not in ("x-description-zh", "x-required-in-parent", "x-status")}
        if isinstance(node, list):
            return [strip_annotations(value) for value in node]
        return node
    assert strip_annotations(annotated) == DEFS, "Official constraints changed"
    atlas = {
        "说明": "这是 MCP 数据层参考册，不是可整体发送的一条 MCP 报文。examples 每项的 data 是独立示例，不是依次执行的一段会话；MRTR 的四个示例另有明确的顺序。内嵌输入与内容块需置于相应外层。$defs 保留官方约束并增加中文注解。",
        "protocolVersion": VERSION, "verifiedOn": "2026-10-27",
        "scope": "覆盖本次采集的 2026-07-28 官方核心 schema 全部 155 个定义、全部固定方法名与全部已声明属性；包含仍保留的 Deprecated 类型。开放业务参数、JSON Schema 完整词汇、扩展及 OAuth 外部协议不能由一个核心 Schema 穷尽。",
        "readingOrder": ["methods：先看方法与通信方向", "examples：看带具体值的 JSON", "$defs：按类型名查字段的中文解释与完整约束", "fieldGuide：用 path 查每项声明属性"],
        "sources": json.loads((SOURCE / "采集说明.json").read_text(encoding="utf-8")),
        "notation": {"x-description-zh": "教学中文概括；原 description 与类型约束保留，用于核对完整适用条件。", "x-required-in-parent": "是否列在直接父对象的 required 中；不代表可选父对象本身必须出现。", "$ref": "引用 $defs 中的类型；例如 #/$defs/RequestMetaObject。", "sampleValues": "示例中的名称、业务数据、URI、状态字符串和实验字段均为虚构；没有连接真实服务。"},
        "methods": [{"method": method, "position": "顶层客户端请求" if not method.startswith("notifications/") and method not in ("elicitation/create", "roots/list", "sampling/createMessage") else "MRTR 的 inputRequests 内嵌对象" if method in ("elicitation/create", "roots/list", "sampling/createMessage") else "JSON-RPC 通知", "deprecated": method in ("roots/list", "sampling/createMessage", "notifications/message"), "direction": "客户端→服务器（stdio）" if method == "notifications/cancelled" else "服务器→客户端" if method.startswith("notifications/") else "服务器要求客户端补充输入，嵌入结果后由客户端重试" if method in ("elicitation/create", "roots/list", "sampling/createMessage") else "客户端→服务器"} for method in sorted(expected)],
        "examples": EXAMPLES,
        "extraMetadata": {
            "traceparent": "OpenTelemetry 的 W3C Trace Context 跟踪父上下文，不是请求 id。",
            "tracestate": "跟踪系统的厂商状态。",
            "baggage": "跨服务传播的应用上下文键值。",
            "com.example/demoTag": "教学自定义元数据；不是 MCP 标准字段，不具有认证意义。",
            "x-mcp-header": "工具 inputSchema 属性上的 HTTP 头映射注解；示例 a=2 对应 Mcp-Param-A: 2。不是直接写在 arguments 外的顶层字段。"
        },
        "exampleBusinessFields": {
            "a": "演示加法的第一个整数，非 MCP 内置参数。", "b": "演示加法的第二个整数，非 MCP 内置参数。",
            "sum": "演示加法结果，非 MCP 内置结果字段。", "topic": "示例提示模板要求的主题字符串。",
            "language": "补全上下文中已知的语言值。", "path": "资源模板 URI 中的路径变量。",
            "label": "表单示例的名称字符串。", "count": "表单示例的份数整数。", "confirm": "表单示例的确认布尔值。",
            "plain": "无独立显示标题的单选示例。", "labeled": "带显示标题的单选示例。", "legacy": "旧式枚举显示名示例。",
            "tags": "无独立显示标题的多选示例。", "namedTags": "带显示标题的多选示例。", "email": "表单示例的邮箱字段。",
            "stage": "日志 data 内的自定义阶段字段，不是 MCP 标准字段。", "detail": "error.data 内的自定义错误详情。",
            "header": "示例 HeaderMismatchError 的 error.data 自定义字段，不是该错误要求的固定字段。",
            "form / url / roots / sample": "本例服务端给 inputRequests 分配的关联键；对应 inputResponses 必须使用相同键名。",
            "com.example/category / com.example/tag": "演示使用的厂商命名空间元数据；category=math 与 tag=demo 不具有标准含义。"
        },
        "transportNotes": {
            "stdio": "UTF-8；每条顶层 JSON-RPC 消息占一行，以换行符分帧；stdout 只传协议消息，日志用 stderr。",
            "http": "每条客户端消息独立 POST；响应为 application/json 或本请求的 SSE 流。头字段不属于数据层 JSON。",
            "httpRequestHeaders": {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": VERSION, "Mcp-Method": "tools/call", "Mcp-Name": "add", "Mcp-Param-A": "2"},
            "httpHeaderMeanings": {"Content-Type": "请求体媒体类型。", "Accept": "客户端必须支持普通 JSON 与 SSE 两种响应。", "MCP-Protocol-Version": "必须与请求 _meta 中版本相同。", "Mcp-Method": "必须与 method 相同。", "Mcp-Name": "tools/call、prompts/get 使用 name，resources/read 使用 uri。", "Mcp-Param-A": "由示例工具属性的 x-mcp-header=A 声明产生。"},
            "authorization": "受保护 HTTP 服务的 Authorization: Bearer … 位于 HTTP 头；本参考册不放入凭据，也不把 OAuth 元数据当成 MCP JSON-RPC 消息。"
        },
        "removedFromThisVersion": ["initialize", "notifications/initialized", "ping", "logging/setLevel", "resources/subscribe", "resources/unsubscribe", "notifications/roots/list_changed", "notifications/elicitation/complete"],
        "extensionBoundary": {"tasks": "io.modelcontextprotocol/tasks 是独立官方扩展，不在本核心 Schema 中；字段以扩展规范为准。", "appsAndOthers": "MCP Apps 与其他扩展同样另行声明能力及字段。", "source": "https://modelcontextprotocol.io/extensions/overview"},
        "$defs": annotated, "fieldGuide": field_guide,
    }
    atlas["coverage"] = {"definitions": len(DEFS), "literalMethods": len(expected), "examples": len(EXAMPLES), "declaredPropertyOccurrences": sum(map(len, field_guide.values())), "clientRequestMethods": 10, "embeddedInputMethods": 3, "notificationMethods": 8}
    (HERE / "mcp-message-atlas.json").write_text(json.dumps(atlas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# MCP 2026-07-28 消息与字段参考", "", "归属：[MCP 数据层无状态的完整报文与重启实验](../AI%20与模型/MCP.md#q-20261027-005)。", "", "- **核实**：2026-10-27；基于本次保存的官方 schema.ts 与 schema.json；不替代具体实现的行为验证。", "- **覆盖**：155 个核心类型定义、21 个固定方法名、全部声明属性；保留已弃用类型。开放映射中的业务键、供应商字段及独立扩展无法穷尽。", "- **完整 JSON**：[消息参考册](../附件/演示/q-20261027-005/mcp-message-atlas.json)。", "- **原始资料**：[官方 JSON Schema 原件](../附件/来源/mcp-2026-07-28-schema-20261027/schema.json)、[官方类型源码原件](../附件/来源/mcp-2026-07-28-schema-20261027/schema.ts)、[采集说明及哈希](../附件/来源/mcp-2026-07-28-schema-20261027/采集说明.json)。", "", "## 阅读规则", "", "examples 的 data 才是示例对象；参考册整体不能发送给 MCP 服务器。内嵌输入请求只有 method 与 params，不加独立 JSON-RPC 信封。所有新增 x-description-zh、x-required-in-parent 与 fieldGuide 都是参考册注解，不是线上报文字段。", "", "JSON Schema 中 required 表示直接父对象出现时的必填性；可选父对象未出现时，其内部必填字段无需单独出现。表格字段如果引用其他类型，沿类型标题继续查阅。保留官方英文 description 和完整 Schema 约束，以免简短中文概括丢失条件。", "", "## 重要边界", "", "本版顶层交互由客户端发起。服务器需要用户输入、根目录或模型采样时，在 resultType=input_required 的结果内返回 inputRequests；客户端以新请求 id 重试，提交 inputResponses，并原样回传 requestState。只有 tools/call、resources/read、prompts/get 支持这一中间结果。", "", "订阅的确认是 notifications/subscriptions/acknowledged；最终 result 只在正常结束时返回。订阅通知携带 subscriptionId，进度和日志通知不属于订阅流。日志、根目录、采样在本版仍保留但已弃用。", "", "工具执行失败通常使用 result.isError=true；协议级失败使用 error。缓存结果的 ttlMs 与 cacheScope 是必填项，ttlMs 的单位是毫秒。", "", f"一手来源：[基础规范]({BASE}/basic)、[消息模式]({BASE}/basic/patterns)、[MRTR]({BASE}/basic/patterns/mrtr)、[版本变更]({BASE}/changelog)、[类型源码]({RAW})。", "", "## 方法目录", "", "| 方法 | 所在位置 | 方向 | 状态 |", "| --- | --- | --- | --- |"]
    for row in atlas["methods"]:
        md.append(f"| `{row['method']}` | {row['position']} | {row['direction']} | {'已弃用' if row['deprecated'] else '保留'} |")
    md += ["", "## 具体 JSON 示例", "", "以下是独立示例，不是一段依次执行的会话；MRTR 四个示例明确构成一个多轮流程。示例包含可选字段以便查阅。真实请求仅声明实际支持且本次需要的能力；演示场景中的 URL、游标和状态字符串不是可用于真实服务的凭据。", "", "`io.modelcontextprotocol/protocolVersion` 是一个完整 JSON 键名。斜杠不产生嵌套对象；实际访问形如 `_meta[\"io.modelcontextprotocol/protocolVersion\"]`。", "", "### 示例业务字段", "", "| 字段 | 含义 |", "| --- | --- |"]
    for key, desc in atlas["exampleBusinessFields"].items():
        md.append(f"| `{key}` | {desc} |")
    for ex in EXAMPLES:
        md += ["", "### " + ex["名称"], "", "官方类型：`" + ex["官方类型"] + "`。" + ex["说明"], "", "```json", json.dumps(ex["data"], ensure_ascii=False, indent=2), "```"]
    md += ["", "## 额外元数据与 HTTP 字段", "", "| 字段 | 说明 |", "| --- | --- |"]
    for key, desc in {**atlas["extraMetadata"], **atlas["transportNotes"]["httpHeaderMeanings"]}.items():
        md.append(f"| `{key}` | {desc} |")
    md += ["", f"一手来源：[基础规范元数据]({BASE}/basic)、[HTTP 传输]({BASE}/basic/transports/streamable-http)。", "", "## 全部类型与声明字段", ""]
    for name, node in annotated.items():
        md += ["### " + name, "", type_description(name), ""]
        if name in deprecated:
            md += ["状态：已弃用。", ""]
        fields = field_guide[name]
        if not fields:
            md += ["该类型无固定声明属性，可能为基础值、开放映射或联合类型。结构：`" + type_expr(node).replace("|", "或") + "`。", ""]
            continue
        md += ["| 字段路径 | 类型或引用 | 直接父对象内必填 | 说明 |", "| --- | --- | --- | --- |"]
        for field in fields:
            constraints = "；约束：" + json.dumps(field["constraints"], ensure_ascii=False) if field["constraints"] else ""
            md.append("| `" + field["path"] + "` | `" + field["type"].replace("|", "或") + "` | " + ("是" if field["required"] else "否") + " | " + (field["说明"] + constraints).replace("|", "或").replace("\n", " ") + " |")
        md.append("")
    md += ["## 适用范围与首要资料", "", "该参考册没有复刻旧版已移除的握手、会话、独立服务器请求及旧任务 API；没有把 Tasks、Apps 或第三方扩展混入核心消息。嵌入工具 Schema 的 JSON Schema 词汇是独立标准，官方允许完整 2020-12 词汇；示例只用到其中部分关键词。", "", f"首要资料：[一手：MCP 类型源码]({RAW})、[一手：基础规范]({BASE}/basic)、[一手：工具]({BASE}/server/tools)、[一手：资源]({BASE}/server/resources)、[一手：补充输入]({BASE}/client/elicitation)、[一手：版本变更]({BASE}/changelog)。", ""]
    appendix = RECORDS.parent / "附录/q-20261027-005.md"
    appendix.parent.mkdir(parents=True, exist_ok=True)
    appendix.write_text("\n".join(md), encoding="utf-8")
    # Validate the actual local demonstration separately from synthetic examples.
    trace_path = HERE / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    request_types = {"server/discover": "DiscoverRequest", "tools/list": "ListToolsRequest", "tools/call": "CallToolRequest"}
    response_types = {"server/discover": "DiscoverResultResponse", "tools/list": "ListToolsResultResponse", "tools/call": "CallToolResultResponse"}
    pending = {}
    for step in trace["steps"]:
        if step["kind"] == "restart":
            continue
        message = json.loads(step["wire"])
        if step["kind"] == "request":
            pending[message["id"]] = message["method"]
            check(message, DEFS[request_types[message["method"]]], "trace.request")
        else:
            method = pending.pop(message["id"])
            check(message, DEFS[response_types[method]], "trace.response")
    assert not pending
    verification = {"verifiedOn": "2026-10-27", "scope": "使用自带校验器检查本次官方 Schema 所用的结构关键词；不把 format 注解、业务语义或任意通信时序当成已验证。",
                    "syntheticExamplesValidated": len(EXAMPLES), "capturedMessagesValidated": 8,
                    "coverage": atlas["coverage"], "negativeChecksRejected": negative_checks,
                    "officialConstraintsUnchangedAfterRemovingTeachingAnnotations": True,
                    "mrtrCorrelationChecked": True}
    (HERE / "atlas-verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(atlas["coverage"], ensure_ascii=False))


if __name__ == "__main__":
    main()
