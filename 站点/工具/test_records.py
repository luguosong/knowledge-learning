"""通过命令行验证文章检索、关联、校验与迁移验收。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


TOOL = Path(__file__).with_name("records.py")


class RecordsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("docs/主题.md", """# 主题

<!-- domain: 测试 -->
**范围**：协议与实验。
**综述**：每次请求必须自包含。
<!-- /domain -->

## 请求机制

请求自带版本。[一手资料](https://example.org/spec)

## 提问记录

### q-20261027-001

- **原题**：2026-10-27 · 协议如何运行
- **问**：重启后还需要协商吗？
- **领域**：测试
- **首次**：2026-10-27
- **更新**：2026-10-29
- **正文**：[请求机制](#请求机制)
""")
        self.write("管理/兼容链接.json", json.dumps([
            {"domain": "测试", "title": "旧协议标题", "id": "q-20261027-001"}
        ], ensure_ascii=False))

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOL), "--root", str(self.root), *args],
            capture_output=True, text=True,
        )

    def test_find_by_question_id_old_title_and_domain_returns_article_section(self):
        for query in ["q-20261027-001", "旧协议标题", "重启", "自带"]:
            with self.subTest(query=query):
                result = self.run_tool("find", query, "--domain", "测试")
                self.assertEqual(0, result.returncode, result.stderr + result.stdout)
                self.assertIn("docs/主题.md#请求机制", result.stdout)
                self.assertIn("q-20261027-001", result.stdout)
                self.assertIn("2026-10-29", result.stdout)

    def test_sync_is_idempotent_and_invalid_body_link_blocks_writes(self):
        result = self.run_tool("sync")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        index = self.root / "管理/索引.json"
        first = index.read_bytes()
        self.assertEqual(0, self.run_tool("sync").returncode)
        self.assertEqual(first, index.read_bytes())
        self.assertEqual(0, self.run_tool("check").returncode)
        path = self.root / "docs/主题.md"
        path.write_text(path.read_text().replace("(#请求机制)", "(#不存在)"))
        result = self.run_tool("sync")
        self.assertEqual(1, result.returncode)
        self.assertIn("无效标题", result.stdout)
        self.assertEqual(first, index.read_bytes())

    def test_backlinks_resolves_question_anchor_and_ignores_code_examples(self):
        self.write("docs/另一篇.md", """# 另一篇

[关联问题](主题.md#q-20261027-001)
[重复链接](主题.md#q-20261027-001)

```markdown
[示例](不存在.md)
```
""")
        result = self.run_tool("backlinks", "q-20261027-001")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(1, result.stdout.count("docs/另一篇.md"))
        self.assertIn("1 篇文章", result.stdout)
        self.assertEqual(0, self.run_tool("sync").returncode)

    def test_audit_rejects_changed_knowledge_dates_and_damaged_attachments(self):
        self.write("docs/附件/原件.json", '{"version": 1}\n')
        self.write("管理/迁移核对.json", json.dumps({
            "questions": [{"id": "q-20261027-001", "created": "2026-10-27",
                           "updated": "2026-10-29", "title": "2026-10-27 · 协议如何运行",
                           "domain": "测试", "query": "重启后还需要协商吗？"}],
            "attachments": [{"path": "docs/附件/原件.json",
                             "sha256": hashlib.sha256(b'{"version": 1}\n').hexdigest()}],
        }, ensure_ascii=False))
        self.assertEqual(0, self.run_tool("audit").returncode)
        path = self.root / "docs/主题.md"
        path.write_text(path.read_text().replace("**更新**：2026-10-29", "**更新**：2026-11-01"))
        self.assertIn("迁移改变了 updated", self.run_tool("audit").stdout)
        self.write("docs/附件/原件.json", '{}\n')
        result = self.run_tool("audit")
        self.assertEqual(1, result.returncode)
        self.assertIn("附件哈希不符", result.stdout)

    def test_find_searches_only_the_linked_body_and_follows_appendices(self):
        path = self.root / "docs/主题.md"
        text = path.read_text().replace("\n## 提问记录\n", "\n## 无关主题\n\n鲸鱼迁徙。\n\n## 提问记录\n")
        text += """
### q-20261027-002

- **原题**：2026-10-27 · 鲸鱼去哪里
- **问**：鲸鱼迁徙路径是什么？
- **领域**：测试
- **首次**：2026-10-27
- **更新**：2026-10-27
- **正文**：[无关主题](#无关主题)
"""
        path.write_text(text)
        result = self.run_tool("find", "鲸鱼")
        self.assertIn("q-20261027-002", result.stdout)
        self.assertNotIn("q-20261027-001", result.stdout)
        self.write("docs/附录/详细.md", "# 详细\n\n独有参数。\n")
        path.write_text(text.replace("[请求机制](#请求机制)", "[请求机制](#请求机制)；[附录](附录/详细.md)"))
        result = self.run_tool("find", "独有参数")
        self.assertIn("q-20261027-001", result.stdout)
        self.assertIn("docs/附录/详细.md", result.stdout)

    def test_history_cannot_contain_an_answer_or_point_back_to_itself(self):
        path = self.root / "docs/主题.md"
        original = path.read_text()
        for text in [original + "\n- **答**：另一份答案。\n",
                     original + "\n这里又复制了一份完整推导。\n",
                     original.replace("(#请求机制)", "(#q-20261027-001)")]:
            with self.subTest(text=text[-50:]):
                path.write_text(text)
                self.assertEqual(1, self.run_tool("sync").returncode)
                self.assertFalse((self.root / "管理/索引.json").exists())

    def test_fenced_markdown_heading_does_not_hide_following_body(self):
        path = self.root / "docs/主题.md"
        path.write_text(path.read_text().replace("请求自带版本。", """请求自带版本。

```markdown
## 示例标题
```

重启后必须保留本地缓存。
"""))
        result = self.run_tool("find", "本地缓存")
        self.assertIn("docs/主题.md#请求机制", result.stdout)

    def test_bad_identity_dates_and_missing_fields_cannot_replace_index(self):
        self.assertEqual(0, self.run_tool("sync").returncode)
        index = self.root / "管理/索引.json"
        before = index.read_bytes()
        path = self.root / "docs/主题.md"
        original = path.read_text()
        for modified, message in [
            (original.replace("**更新**：2026-10-29", "**更新**：2026-10-26"), "更新日期无效"),
            (original.replace("**首次**：2026-10-27", "**首次**：2026-10-28"), "首次日期与 ID 不符"),
            (original.replace("- **问**：重启后还需要协商吗？\n", ""), "字段不全"),
        ]:
            with self.subTest(message=message):
                path.write_text(modified)
                result = self.run_tool("sync")
                self.assertEqual(1, result.returncode)
                self.assertIn(message, result.stdout)
                self.assertEqual(before, index.read_bytes())
        path.write_text(original)
        self.write("docs/重复.md", original)
        self.assertIn("问题 ID 重复", self.run_tool("check").stdout)

    def test_writer_lock_and_invalid_search_options_are_rejected(self):
        self.write("管理/.records.lock", "other-writer")
        result = self.run_tool("sync")
        self.assertEqual(1, result.returncode)
        self.assertIn("存在写入锁", result.stdout)
        self.assertFalse((self.root / "管理/索引.json").exists())
        self.assertEqual(1, self.run_tool("find", "协议", "--limit", "0").returncode)
        self.assertEqual(1, self.run_tool("find", "协议", "--domain", "未知").returncode)


if __name__ == "__main__":
    unittest.main()
