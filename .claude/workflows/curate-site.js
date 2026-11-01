export const meta = {
  name: "curate-site",
  description: "整理发布：维护唯一正文的结构与链接，做拆分/合并/裂变/塌缩判断，校验后提交并推送 GitHub",
  phases: [
    { title: "准备", detail: "确认任务文件范围与暂存状态" },
    { title: "结构", detail: "触及+邻居+标题扫描的拆分/合并/裂变/塌缩判断" },
    { title: "重构", detail: "应用结构操作并就地验证" },
    { title: "校验", detail: "结构检查与严格构建通过才发布" },
    { title: "发布", detail: "只提交本次文件，推送失败留待下次" },
  ],
}

const ROOT = "/home/luguosong/code-wsl/personal/知识学习"
const OPS = ["merge", "split", "fission", "collapse"]

const OPS_SCHEMA = {
  type: "object",
  properties: {
    ops: {
      type: "array",
      items: {
        type: "object",
        properties: {
          op: { type: "string", enum: OPS },
          sources: { type: "array", items: { type: "string" } },
          target: { type: "string" },
          reason: { type: "string" },
        },
        required: ["op", "sources", "target", "reason"],
      },
    },
    notes: { type: "string" },
  },
  required: ["ops"],
}

const APPLY_SCHEMA = {
  type: "object",
  properties: {
    done: { type: "boolean" },
    detail: { type: "string" },
    targets: { type: "array", items: { type: "string" } },
    movedTitles: { type: "array", items: { type: "string" } },
    touchedFiles: { type: "array", items: { type: "string" } },
  },
  required: ["done", "detail", "targets", "movedTitles", "touchedFiles"],
}

const DONE_SCHEMA = {
  type: "object",
  properties: { ok: { type: "boolean" }, detail: { type: "string" } },
  required: ["ok", "detail"],
}

const PUSH_SCHEMA = {
  type: "object",
  properties: { pushed: { type: "boolean" }, detail: { type: "string" } },
  required: ["pushed", "detail"],
}

const structPrompt = [
  "你是人类站点的结构编辑，仓库根 " + ROOT + "。本次触及领域：" + JSON.stringify(args.domains),
  "1. 前台已经更新唯一正文，不从其他记录生成答案。用 站点/管理/索引.json 定位触及领域，再按需读取相关章节与邻居文章。分类目录即顶部导航（八类固定），层级由专题目录承载；结构操作的产物留在目标文章所在目录。",
  "2. 用 grep -rE \"^# \" 站点/docs/ 做全站标题扫描；对与触及文章疑似同主题或名字相邻的其它文章读标题乃至全文确认。",
  "3. 只提出有充分理由的操作：",
  "- merge：两篇主讲同一知识维度（主题重合过半），或一篇不足约 300 字且可自然并入母篇；产物留在目标文章所在目录。",
  "- split：一篇超过约 2000 字且含至少两个可独立成篇的子主题；拆出文章与原文同目录。",
  "- fission：split 条件成立且文章名即主题锚点（位于分类根或专题根、无同名目录）时裂变：新建同名小写英文目录，概览/路线内容改写为 index.md 导读（一句话介绍 + 指向全部成员文章的链接，不承载具体知识解释），其余小节各自成篇放入，配 .nav.yml（首条「导读: index.md」，成员按学习顺序）。",
  "- collapse：专题目录经合并后只剩一篇文章时，收回为上级目录的同名单文件，删除空目录及其 .nav.yml。",
  "4. 不确定则不动；操作之间不得共享源文件。每个操作必须保留原问题 ID、原问、日期、来源、核实范围及历史修正。领域范围只能登记一次。",
  "返回 ops：op（" + OPS.join("/") + "）、sources、target、reason（split/fission 时含新文件或目录名清单）。",
].join("\n")

function applyPrompt(op) {
  return [
    "在 " + ROOT + " 应用一个站点结构操作，只动站点/docs/ 下的文件：",
    "站点规范：修改前读取并执行 站点/维护规范.md。",
    JSON.stringify(op),
    op.op === "merge"
      ? "把 sources 每篇的全部小节并入 target（重写涵盖合并范围的导语）；先写好 target 再删除 sources 文件。"
      : op.op === "split"
      ? "把 target 按子主题拆成多篇文章（文件名取 reason 清单或自拟中文名，每篇配导语，与 target 同目录）；先写好全部新文件再删除 target。"
      : op.op === "fission"
      ? "把 sources 文章裂变为专题目录 target/（小写英文名）：概览与路线内容改写为 target/index.md 导读（一句话介绍 + 指向全部成员的相对链接，不承载具体知识解释），其余小节各自成篇放入 target/，并写 target/.nav.yml（首条「导读: index.md」，成员按学习顺序）；先写好全部新文件再删除原文。"
      : "把 sources（某专题目录仅剩的文章）的全部小节并入 target 单文件（重写导语）；先写好 target 再删除 sources 文件、其空目录与该目录的 .nav.yml。",
    "铁律：任何实质内容、来源和日期不得丢失；提问记录随其正文迁移，原 ID 全局唯一；同步更新所有受影响的导读、导航、正文入口与站内链接。只有与本操作有关的文件可以改动。",
    "返回：done、detail、targets（最终产物文件名列表）、movedTitles（移动的标题）、touchedFiles（本操作修改、新建和删除的全部实际文件，包括既有入链页及导航；只列文件，不列目录）。",
  ].join("\n")
}

function verifyPrompt(op, res) {
  return [
    "在 " + ROOT + " 校验一个结构操作的结果：",
    "站点校验：按 站点/维护规范.md 的「验证」逐项检查 targets 中本次触及的内容。",
    JSON.stringify({ op: op.op, sources: op.sources, target: op.target }),
    "应用代理报告：detail=" + res.detail + "，targets=" + JSON.stringify(res.targets) + "，movedTitles=" + JSON.stringify(res.movedTitles),
    "逐项检查：1) 每个 movedTitles 标题（或其等义改写）在 targets 某文件中存在；2) targets 每个文件恰有一个一级标题；3) 文中没有 [[ 形式的 wiki 链接；4) fission 时 target/index.md 存在且链接全部成员、成员都在 target/ 内，collapse 时原目录与 .nav.yml 已删除；5) 站内相对链接的目标文件存在。",
    "核对 touchedFiles 与实际文件差异；不得漏掉修改的既有入链页或删除文件。触及清单：" + JSON.stringify(res.touchedFiles),
    "返回 ok 与 detail（列出每一个失败项）。",
  ].join("\n")
}

if (!Array.isArray(args.files) || args.files.length === 0) {
  return { pushed: false, pushDetail: "未提供本次变更文件清单，保留本地改动" }
}
phase("准备")
const preflight = await agent([
  "在 " + ROOT + " 检查 git -c core.quotepath=false status --short 与暂存区，不修改文件。",
  "本次文件：" + JSON.stringify(args.files),
  "只允许本次文件和 站点/管理/索引.json 有未暂存改动。若存在任何其他任务的修改、新文件或暂存改动，返回 ok=false；不得先同步全局索引。",
  "检查通过才返回 ok=true，detail 写实际结果。",
].join("\n"), { schema: DONE_SCHEMA, phase: "准备", label: "任务范围检查" })
if (!preflight || !preflight.ok) return { pushed: false, pushDetail: preflight ? preflight.detail : "准备检查失败" }

phase("结构")
const plan = await agent(structPrompt, { schema: OPS_SCHEMA, phase: "结构", label: "结构判断" })
if (!plan || !Array.isArray(plan.ops)) return { pushed: false, pushDetail: "结构判断失败，保留本地改动" }

phase("重构")
const verifyResults = []
// 结构操作逐个执行，避免多个操作同时修改同一入链页。
for (const op of plan.ops) {
  const res = await agent(applyPrompt(op), { schema: APPLY_SCHEMA, phase: "重构", label: "改:" + op.target })
  if (!res || !res.done || !Array.isArray(res.touchedFiles)) {
    return { ops: plan.ops, verifyResults, pushed: false, pushDetail: "结构操作失败或缺少完整文件清单" }
  }
  const verified = await agent(verifyPrompt(op, res), { schema: DONE_SCHEMA, phase: "重构", label: "验:" + op.target })
  verifyResults.push({ target: op.target, ok: Boolean(verified && verified.ok),
    verify: verified ? verified.detail : "校验代理失败", targets: res.targets, touchedFiles: res.touchedFiles })
  if (!verified || !verified.ok) {
    return { ops: plan.ops, verifyResults, pushed: false, pushDetail: "结构校验失败，保留本地改动" }
  }
}
const files = [...new Set([
  ...args.files,
  "站点/管理/索引.json",
  ...verifyResults.flatMap(v => v.touchedFiles),
])]

phase("校验")
const validation = await agent([
  "在 " + ROOT + " 先检查 git status 与暂存区，再顺序运行命令。存在清单之外的改动或任何暂存改动时返回 ok=false，不同步索引；命令任一非零退出即停止。",
  "本次完整文件清单：" + JSON.stringify(files),
  "python 站点/工具/records.py sync",
  "python 站点/工具/records.py check",
  "python 站点/工具/build.py",
  "只返回实际执行结果；构建仅生成临时副本与忽略的 site 目录，不改写源文章。",
  "返回 ok 与 detail。",
].join("\n"), { schema: DONE_SCHEMA, phase: "校验", label: "校验与构建" })
if (!validation || !validation.ok) {
  return { ops: plan.ops, verifyResults, pushed: false, pushDetail: validation ? validation.detail : "校验失败" }
}

phase("发布")
const pushPrompt = [
  "在 " + ROOT + " 发布本次问答，触及领域：" + JSON.stringify(args.domains || []),
  "候选文件：" + JSON.stringify(files),
  "1. 重新检查 git status 和暂存区。存在任何候选清单之外的改动、新文件或暂存改动时返回 pushed=false；不要混入其他任务。",
  "2. 只逐文件暂存候选清单中的实际变更，包括删除文件。所有入链页、成员文章和导航已包含在 touchedFiles，不得另加清单之外的文件。禁止 git add 整个目录。",
  "3. 若暂存为空，返回 pushed=true、detail=无变更；否则提交，消息说明触及领域与本次摘要。",
  "本次摘要：" + String(args.summary || ""),
  "4. git pull --rebase origin main 成功后执行 git push。冲突时 git rebase --abort；推送失败不重试；绝不强推。",
  "返回 pushed 与 detail，保留失败摘要。",
].join("\n")
const push = (await agent(pushPrompt, { schema: PUSH_SCHEMA, phase: "发布", label: "commit+push" })) || { pushed: false, detail: "发布代理失败" }

return {
  ops: plan.ops,
  verifyResults,
  pushed: push.pushed,
  pushDetail: push.detail,
}
