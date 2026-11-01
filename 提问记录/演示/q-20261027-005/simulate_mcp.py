"""A minimal MCP 2026-07-28 stdio demonstration, using only Python stdlib.

Run without arguments to send real messages to a child process and capture them.
This implements only discovery, listing one integer-addition tool, and calling it.
It is a teaching example, not a complete MCP implementation.
"""

import copy
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


VERSION = "2026-07-28"
SERVER_INFO = {"name": "addition-demo", "version": "1.0.0"}
CLIENT_META = {
    "io.modelcontextprotocol/protocolVersion": VERSION,
    "io.modelcontextprotocol/clientInfo": {
        "name": "learning-client", "version": "1.0.0"
    },
    "io.modelcontextprotocol/clientCapabilities": {},
}
TOOL = {
    "name": "add",
    "description": "Return the sum of two integers.",
    "inputSchema": {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
        "additionalProperties": False,
    },
    "outputSchema": {
        "type": "object",
        "properties": {"sum": {"type": "integer"}},
        "required": ["sum"],
    },
}


def result(request_id, **fields):
    return {
        "jsonrpc": "2.0", "id": request_id,
        "result": {
            "resultType": "complete", **fields,
            "_meta": {"io.modelcontextprotocol/serverInfo": SERVER_INFO},
        },
    }


def error(request_id, code, message, **fields):
    return {"jsonrpc": "2.0", "id": request_id,
            "error": {"code": code, "message": message, **fields}}


def handle(message):
    """No per-client or previous-request state is read or written here."""
    request_id = message.get("id")
    params = message.get("params", {})
    meta = params.get("_meta", {})
    if ("io.modelcontextprotocol/protocolVersion" not in meta
            or "io.modelcontextprotocol/clientCapabilities" not in meta):
        return error(request_id, -32602, "Required request metadata is missing")
    if meta["io.modelcontextprotocol/protocolVersion"] != VERSION:
        return error(request_id, -32022, "Unsupported protocol version",
                     data={"supported": [VERSION],
                           "requested": meta["io.modelcontextprotocol/protocolVersion"]})
    method = message.get("method")
    if method == "server/discover":
        return result(request_id, supportedVersions=[VERSION], capabilities={"tools": {}},
                      ttlMs=300000, cacheScope="public")
    if method == "tools/list":
        return result(request_id, tools=[TOOL], ttlMs=300000, cacheScope="public")
    if method == "tools/call":
        arguments = params.get("arguments", {})
        if (params.get("name") != "add" or set(arguments) != {"a", "b"}
                or any(type(arguments[k]) is not int for k in ("a", "b"))):
            return error(request_id, -32602, "Expected add with integer a and b")
        total = arguments["a"] + arguments["b"]
        return result(request_id, content=[{"type": "text", "text": str(total)}],
                      structuredContent={"sum": total}, isError=False)
    return error(request_id, -32601, "Method not found")


def serve():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    for line in sys.stdin:
        response = handle(json.loads(line))
        sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()


def launch():
    return subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", bufsize=1,
    )


def stop(process):
    process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise RuntimeError("Server failed to exit after stdin was closed")
    diagnostics = process.stderr.read()
    process.stdout.close()
    process.stderr.close()
    if process.returncode:
        raise RuntimeError(diagnostics)


def run_demo():
    steps = []
    process = launch()
    first_pid = process.pid

    def exchange(number, method, title, note, generation, **parameters):
        request = {"jsonrpc": "2.0", "id": number, "method": method,
                   "params": {**parameters, "_meta": copy.deepcopy(CLIENT_META)}}
        # These exact compact lines are sent through the child's standard streams.
        wire = json.dumps(request, ensure_ascii=False, separators=(",", ":"))
        steps.append({"kind": "request", "title": title, "note": note,
                      "generation": generation, "pid": process.pid, "wire": wire})
        process.stdin.write(wire + "\n")
        process.stdin.flush()
        reply_line = process.stdout.readline()
        if not reply_line:
            raise RuntimeError("The server closed stdout before sending its response")
        reply = json.loads(reply_line)
        assert reply["id"] == number and "result" in reply
        steps.append({"kind": "response", "title": title + "：返回",
                      "note": {
                          1: "服务器返回所支持的版本与工具能力；发现操作没有建立协议会话。",
                          2: "inputSchema 定义 a、b 必填；add 是本演示定义的业务工具。",
                          3: "id=3 对应刚才的调用；宿主可以保存 sum=5，供后续请求使用。",
                          4: "新进程直接返回 15；它没有收到先前的发现、列表和计算请求。",
                      }[number],
                      "generation": generation, "pid": process.pid,
                      "wire": reply_line.rstrip("\r\n")})
        return reply["result"]

    try:
        exchange(1, "server/discover", "发现服务器",
                 "每次请求都携带 protocolVersion 和 clientCapabilities；空对象表示未声明可选客户端能力。", 1)
        exchange(2, "tools/list", "读取工具定义",
                 "此请求再次携带 _meta；服务器不需要读取上一条请求中的协议版本和能力。", 1)
        first = exchange(3, "tools/call", "计算 2 + 3",
                         "name 选择 add；arguments 带齐本次计算的两个输入。", 1,
                         name="add", arguments={"a": 2, "b": 3})
    finally:
        stop(process)
    steps.append({"kind": "restart", "title": "关闭旧进程，启动新进程",
                  "note": "客户端在内存中保留 5；服务器进程内存已释放。", "generation": 2,
                  "wire": ""})
    process = launch()
    second_pid = process.pid
    try:
        second = exchange(4, "tools/call", "直接调用：用上一结果再加 10",
                          "宿主把上一结果明确填入 a=5；新服务器只需读取本条请求。", 2,
                          name="add", arguments={"a": first["structuredContent"]["sum"], "b": 10})
    finally:
        stop(process)
    assert first["structuredContent"] == {"sum": 5}
    assert second["structuredContent"] == {"sum": 15}
    assert len(steps) == 9
    trace = {"capturedAtUtc": datetime.now(timezone.utc).isoformat(),
             "protocolVersion": VERSION, "transport": "stdio",
             "scope": "Real local subprocess IO; synthetic addition server; no model or external API call.",
             "steps": steps}
    folder = Path(__file__).resolve().parent
    (folder / "trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path = folder / "mcp-stateless-flow.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")
        payload = json.dumps(trace, ensure_ascii=False).replace("<", "\\u003c")
        html, count = re.subn(
            r'(<script type="application/json" id="mcp-trace-data">)[\s\S]*?(</script>)',
            lambda match: match[1] + payload + match[2], html, count=1,
        )
        assert count == 1
        html_path.write_text(html, encoding="utf-8")
    print(json.dumps({"requests": 4, "responses": 4, "serverProcesses": [first_pid, second_pid],
                      "firstSum": 5, "secondSum": 15, "freshProcessFirstMethod": "tools/call",
                      "trace": str(folder / "trace.json")}, ensure_ascii=False))


if __name__ == "__main__":
    serve() if "--server" in sys.argv else run_demo()
