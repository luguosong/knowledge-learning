export const meta = {
  name: "curate-site",
  description: "整理发布：把本次问答的记录增量更新进人类站点，做拆分/合并/裂变/塌缩判断，校验后提交并推送 GitHub",
  phases: [
    { title: "更新", detail: "每个触及领域更新对应文章" },
    { title: "结构", detail: "触及+邻居+标题扫描的拆分/合并/裂变/塌缩判断" },
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
          op: { type: "string", enum: ["merge", "split", "fission", "collapse"] },
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
    "先定位该领域的现有文章，按优先级：① 任意层级下的同名文件（find 站点/docs -name '" + d + ".md'）；② 同名专题目录（小写连字符，如 Java SE → java-se/）内按问题主题最贴合的成员文章；③ grep -rl 标题含领域名的文章。只动定位到的文件，不运行 git。",
    "",
    "步骤：",
    "1. 读 提问记录/" + d + ".md（综述与问题目录）。",
    "2. 文章已存在时：先 grep 它的小节标题（^## ），与目录的问题清单对比；只为缺失或主题已变的问题读 提问记录/条目/ 对应文件；综述有变则重写导语（至多 120 字）。",
    "3. 文章不存在时：按目录读全部问题新建文章（以 \"# " + d + "\" 开头，不用 frontmatter，含导语）。落位：优先放入同族专题目录（如 Java 家族 → 站点/docs/软件开发/java/，成员见其 .nav.yml），否则放最贴切的分类目录根，路径 <目录>/" + d + ".md。分类即顶部导航（八类固定，不新建）；可在专题内新建小写英文子目录并配 .nav.yml（首条「导读: index.md」）。",
    "",
    "写作规范：每问题一节（主题化标题，不用日期），讲结论、原因与取舍，保留条件、单位、限制与例外；关键信源为 Markdown 链接并保留一手/二手标注；复杂结构用 text 代码块 ASCII 图；短句、一词一义；术语首次出现写「中文名（English Name，缩写）」。跨文章知识遵守归属页规则：知识点已有专门文章时，本文只写一句话并附相对链接（如 [JVM](../jvm.md)），完整解释只在归属文章出现一次。",
    "铁律：不引入记录中没有的结论；矛盾并列并注明；禁止把 [[...]] wiki 链接原样写入；内容性改写仅限本文。",
    "",
    "返回 JSON：domain、updated（新增或改写的小节数）、notes（结构异常说明，如文章过长含多个子主题，可空）。",
  ].join("\n")
}

const structPrompt = [
  "你是人类站点的结构编辑，仓库根 " + ROOT + "。本次触及领域：" + JSON.stringify(args.domains),
  "1. 通读触及领域的文章全文（find 站点/docs 定位，可能在专题目录任意层级）。分类目录即顶部导航（八类固定），层级由专题目录承载；结构操作的产物留在目标文章所在目录。",
  "2. 用 grep -rE \"^# \" 站点/docs/ 做全站标题扫描；对与触及文章疑似同主题或名字相邻的其它文章读标题乃至全文确认。",
  "3. 只提出有充分理由的操作：",
  "- merge：两篇主讲同一知识维度（主题重合过半），或一篇不足约 300 字且可自然并入母篇；产物留在目标文章所在目录。",
  "- split：一篇超过约 2000 字且含至少两个可独立成篇的子主题；拆出文章与原文同目录。",
  "- fission：split 条件成立且文章名即主题锚点（位于分类根或专题根、无同名目录）时裂变：新建同名小写英文目录，概览/路线内容改写为 index.md 导读（一句话介绍 + 指向全部成员文章的链接，不承载具体知识解释），其余小节各自成篇放入，配 .nav.yml（首条「导读: index.md」，成员按学习顺序）。",
  "- collapse：专题目录经合并后只剩一篇文章时，收回为上级目录的同名单文件，删除空目录及其 .nav.yml。",
  "4. 不确定则不动；操作之间不得共享源文件。",
  "返回 ops：op（merge/split）、sources、target、reason（split 时含新文件名清单）。",
].join("\n")

function applyPrompt(op) {
  return [
    "在 " + ROOT + " 应用一个站点结构操作，只动站点/docs/ 下的文件：",
    JSON.stringify(op),
    op.op === "merge"
      ? "把 sources 每篇的全部小节并入 target（重写涵盖合并范围的导语）；先写好 target 再删除 sources 文件。"
      : op.op === "split"
      ? "把 target 按子主题拆成多篇文章（文件名取 reason 清单或自拟中文名，每篇配导语，与 target 同目录）；先写好全部新文件再删除 target。"
      : op.op === "fission"
      ? "把 sources 文章裂变为专题目录 target/（小写英文名）：概览与路线内容改写为 target/index.md 导读（一句话介绍 + 指向全部成员的相对链接，不承载具体知识解释），其余小节各自成篇放入 target/，并写 target/.nav.yml（首条「导读: index.md」，成员按学习顺序）；先写好全部新文件再删除原文。"
      : "把 sources（某专题目录仅剩的文章）的全部小节并入 target 单文件（重写导语）；先写好 target 再删除 sources 文件、其空目录与该目录的 .nav.yml。",
    "铁律：任何小节的实质内容不得丢失或删减；不改动其它文件。",
    "返回：done、detail、targets（最终产物文件名列表）、movedTitles（被移动的全部小节标题列表）。",
  ].join("\n")
}

function verifyPrompt(op, res) {
  return [
    "在 " + ROOT + " 校验一个结构操作的结果：",
    JSON.stringify({ op: op.op, sources: op.sources, target: op.target }),
    "应用代理报告：detail=" + res.detail + "，targets=" + JSON.stringify(res.targets) + "，movedTitles=" + JSON.stringify(res.movedTitles),
    "逐项检查：1) 每个 movedTitles 标题（或其等义改写）在 targets 某文件中存在；2) targets 每个文件恰有一个一级标题；3) 文中没有 [[ 形式的 wiki 链接；4) fission 时 target/index.md 存在且链接全部成员、成员都在 target/ 内，collapse 时原目录与 .nav.yml 已删除；5) 站内相对链接的目标文件存在。",
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