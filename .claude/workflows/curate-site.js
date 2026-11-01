export const meta = {
  name: "curate-site",
  description: "整理发布：把本次问答的记录增量更新进人类站点，做拆分/合并判断，校验后提交并推送 GitHub",
  phases: [
    { title: "更新", detail: "每个触及领域更新对应文章" },
    { title: "结构", detail: "触及+邻居+标题扫描的拆分/合并判断" },
    { title: "重构", detail: "应用结构操作并就地验证" },
    { title: "发布", detail: "commit 并 push，失败留待下次" },
  ],
}

const ROOT = "/home/luguosong/code-wsl/personal/知识学习"

const UPDATE_SCHEMA = {
  type: "object",
  properties: {
    domain: { type: "string" },
    updated: { type: "integer" },
    notes: { type: "string" },
  },
  required: ["domain", "updated"],
}

const OPS_SCHEMA = {
  type: "object",
  properties: {
    ops: {
      type: "array",
      items: {
        type: "object",
        properties: {
          op: { type: "string", enum: ["merge", "split"] },
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
  },
  required: ["done", "detail", "targets", "movedTitles"],
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

function updatePrompt(d) {
  return [
    "你在更新个人知识库人类站点的一篇文章，仓库根 " + ROOT + "。触及领域：" + d + "。本次问答概述：" + args.summary,
    "文章：站点/docs/" + d + ".md（可能不存在）。只动这一个文件，不运行 git。",
    "",
    "步骤：",
    "1. 读 提问记录/" + d + ".md（综述与问题目录）。",
    "2. 文章已存在时：先 grep 它的小节标题（^## ），与目录的问题清单对比；只为缺失或主题已变的问题读 提问记录/条目/ 对应文件；综述有变则重写导语（至多 120 字）。",
    "3. 文章不存在时：按目录读全部问题，新建文章（以 \"# " + d + "\" 开头，不用 frontmatter，含导语）。",
    "",
    "写作规范：每问题一节（主题化标题，不用日期），讲结论、原因与取舍，保留条件、单位、限制与例外；关键信源为 Markdown 链接并保留一手/二手标注；复杂结构用 text 代码块 ASCII 图；短句、一词一义；术语首次出现写「中文名（English Name，缩写）」。",
    "铁律：不引入记录中没有的结论；矛盾并列并注明；禁止把 [[...]] wiki 链接原样写入；内容性改写仅限本文。",
    "",
    "返回 JSON：domain、updated（新增或改写的小节数）、notes（结构异常说明，如文章过长含多个子主题，可空）。",
  ].join("\n")
}

const structPrompt = [
  "你是人类站点的结构编辑，仓库根 " + ROOT + "。本次触及领域：" + JSON.stringify(args.domains),
  "1. 通读触及领域的文章全文（站点/docs/<领域>.md）。",
  "2. 用 grep -E \"^# \" 站点/docs/*.md 做全站标题扫描；对与触及文章疑似同主题或名字相邻的其它文章读标题乃至全文确认。",
  "3. 只提出有充分理由的操作：",
  "- merge：两篇主讲同一知识维度（主题重合过半），或一篇不足约 300 字且可自然并入母篇。",
  "- split：一篇超过约 2000 字且含至少两个可独立成篇的子主题。",
  "4. 不确定则不动；操作之间不得共享源文件。",
  "返回 ops：op（merge/split）、sources、target、reason（split 时含新文件名清单）。",
].join("\n")

function applyPrompt(op) {
  return [
    "在 " + ROOT + " 应用一个站点结构操作，只动站点/docs/ 下的文件：",
    JSON.stringify(op),
    op.op === "merge"
      ? "把 sources 每篇的全部小节并入 target（重写涵盖合并范围的导语）；先写好 target 再删除 sources 文件。"
      : "把 target 按子主题拆成多篇文章（文件名取 reason 清单或自拟中文名，每篇配导语）；先写好全部新文件再删除 target。",
    "铁律：任何小节的实质内容不得丢失或删减；不改动其它文件。",
    "返回：done、detail、targets（最终产物文件名列表）、movedTitles（被移动的全部小节标题列表）。",
  ].join("\n")
}

function verifyPrompt(op, res) {
  return [
    "在 " + ROOT + " 校验一个结构操作的结果：",
    JSON.stringify({ op: op.op, sources: op.sources, target: op.target }),
    "应用代理报告：detail=" + res.detail + "，targets=" + JSON.stringify(res.targets) + "，movedTitles=" + JSON.stringify(res.movedTitles),
    "逐项检查：1) 每个 movedTitles 标题（或其等义改写）在 targets 某文件中存在；2) targets 每个文件恰有一个一级标题；3) 文中没有 [[ 形式的 wiki 链接。",
    "返回 ok 与 detail（列出每一个失败项）。",
  ].join("\n")
}

const pushPrompt = [
  "在 " + ROOT + " 执行发布，严格按顺序：",
  "1. git add 站点 提问记录 GLOSSARY.md",
  "2. 若 git diff --cached --quiet 通过（无变更）：返回 pushed=true、detail=\"无变更\"。",
  "3. 否则 git -c user.name=luguosong -c user.email=1054595718@qq.com commit -m \"整理：" + (args.domains || []).join("、") + "\"",
  "4. git pull --rebase origin main && git push —— 两者都成功才返回 pushed=true。",
  "5. rebase 冲突：git rebase --abort，返回 pushed=false 并说明；push 失败：返回 pushed=false 附错误摘要。绝不使用 force。",
  "只提交上述路径，不提交其它未暂存内容。",
].join("\n")

phase("更新")
const updates = (await parallel(
  (args.domains || []).map(d => () => agent(updatePrompt(d), { schema: UPDATE_SCHEMA, phase: "更新", label: "更新:" + d }))
)).filter(Boolean)

phase("结构")
const plan = (await agent(structPrompt, { schema: OPS_SCHEMA, phase: "结构", label: "结构判断" })) || { ops: [] }

phase("重构")
const verifyResults = (await pipeline(
  plan.ops,
  op => agent(applyPrompt(op), { schema: APPLY_SCHEMA, phase: "重构", label: "改:" + op.target }),
  (res, op) => res && agent(verifyPrompt(op, res), { schema: DONE_SCHEMA, phase: "重构", label: "验:" + op.target })
    .then(v => ({ target: op.target, ok: v ? v.ok : false, verify: v ? v.detail : "校验代理失败" }))
)).filter(Boolean)

phase("发布")
const push = (await agent(pushPrompt, { schema: PUSH_SCHEMA, phase: "发布", label: "commit+push" })) || { pushed: false, detail: "发布代理失败" }

return {
  updated: updates.map(u => u.domain + " (" + u.updated + " 节)"),
  ops: plan.ops,
  verifyResults: verifyResults,
  pushed: push.pushed,
  pushDetail: push.detail,
}