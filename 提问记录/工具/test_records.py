"""离线集成验证：在记录目录内的隔离临时目录运行，不改动真实问题。"""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import knowledge
import records


class RecordsIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(__file__).resolve().parent
        self.temporary = tempfile.TemporaryDirectory(prefix=".records-test-", dir=self.workspace)
        self.root = Path(self.temporary.name).resolve()
        assert self.root.is_relative_to(self.workspace)
        self.write("索引.md", "# 索引\n\n测试 —— 不得被生成器改写的范围 · 999 条 · 至 2020-01-01\n")
        self.write("测试.md", "# 测试\n\n## 综述\n\n必须保留的人工综合。\n\n## 问题目录\n\n<!-- catalog:start -->\n<!-- catalog:end -->\n\n<!-- legacy:start -->\n<!-- legacy:end -->\n")
        self.write("管理/兼容链接.json", "[]\n")
        self.add_entry(1)

    def tearDown(self):
        assert self.root.resolve().is_relative_to(self.workspace.resolve())
        self.temporary.cleanup()

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")

    def add_entry(self, number, extra="", domain="测试"):
        ident = f"q-20261027-{number:03}"
        self.write(f"条目/{ident}.md", f'---\nid: {ident}\ndomain: "{domain}"\n---\n\n# 2026-10-27 · 问题 {number}\n\n- **问**：问题 {number}\n- **答**：核心结论\n- **信源**：\n  - [一手] [原文](https://example.org/primary)\n{extra}')
        return ident

    def run_tool(self, *args):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = records.main(["--root", str(self.root), *args])
        return code, buffer.getvalue()

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}

    def test_rebuild_is_idempotent_and_keeps_human_content(self):
        self.assertEqual(1, self.run_tool("check")[0])
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])
        before = self.snapshot()
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(before, self.snapshot())
        self.assertIn("不得被生成器改写的范围 · 1 条 · 至 2026-10-27", records.read(self.root / "索引.md"))
        self.assertIn("必须保留的人工综合。", records.read(self.root / "测试.md"))

    def test_broken_link_blocks_sync_without_partial_write(self):
        self.assertEqual(0, self.run_tool("sync")[0])
        self.add_entry(2, "\n[[条目/q-20261027-999|不存在]]\n")
        before = self.snapshot()
        code, output = self.run_tool("sync")
        self.assertEqual(1, code)
        self.assertIn("无效链接", output)
        self.assertEqual(before, self.snapshot())

    def test_fifty_one_entries_create_two_linked_catalog_pages(self):
        for number in range(2, 52):
            self.add_entry(number)
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])
        first = records.read(self.root / "目录/测试/001.md")
        second = records.read(self.root / "目录/测试/002.md")
        self.assertEqual(50, first.count("- [[条目/"))
        self.assertEqual(1, second.count("- [[条目/"))
        self.assertIn("下一页", first)
        self.assertIn("上一页", second)

    def test_shrinking_domain_retires_extra_pages(self):
        for number in range(2, 52):
            self.add_entry(number)
        self.assertEqual(0, self.run_tool("sync")[0])
        stale_page = self.root / "目录/测试/002.md"
        self.write("目录/测试/002.md", records.read(stale_page) + "\n手写附加行\n")
        for number in range(2, 52):
            (self.root / f"条目/q-20261027-{number:03}.md").unlink()
        code, output = self.run_tool("sync")
        self.assertEqual(0, code)
        self.assertIn("退役：目录/测试/002.md", output)
        self.assertFalse(stale_page.exists())
        self.assertEqual(1, records.read(self.root / "目录/测试/001.md").count("- [[条目/"))
        self.assertNotIn("第 2 页", records.read(self.root / "测试.md"))
        before = self.snapshot()
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(before, self.snapshot())

    def test_unregistered_domain_page_is_retired_with_empty_dir(self):
        self.assertEqual(0, self.run_tool("sync")[0])
        self.write("目录/旧领域/001.md", "# 旧领域 · 第 1 页\n\n> 自动生成；请编辑问题条目及领域综述。\n")
        code, output = self.run_tool("sync")
        self.assertEqual(0, code)
        self.assertIn("退役：目录/旧领域/001.md", output)
        self.assertFalse((self.root / "目录/旧领域").exists())

    def test_appendix_is_searchable_and_contributes_backlinks(self):
        self.add_entry(2, "\n[[附录/q-20261027-002|详细内容]]\n")
        self.write("附录/q-20261027-002.md", "# 专题\n\n独有关键词。[[条目/q-20261027-001|相关问题]]\n")
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])
        self.assertIn("q-20261027-002.md", self.run_tool("find", "独有关键词")[1])
        self.assertIn("q-20261027-002.md", self.run_tool("backlinks", "q-20261027-001")[1])

    def test_wikilinks_inside_examples_are_not_followed(self):
        self.add_entry(1, "\n~~~markdown\n[[不存在]]\n~~~\n\n`[[也是示例]]`\n")
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])

    def test_filename_mismatch_and_unknown_domain_fail_closed(self):
        self.add_entry(2, domain="未知领域")
        self.assertEqual(1, self.run_tool("sync")[0])
        path = self.root / "条目/q-20261027-001.md"
        path.rename(path.with_name("q-20261027-003.md"))
        self.assertIn("文件名与 id 不符", self.run_tool("check")[1])

    def test_writer_lock_prevents_second_writer(self):
        self.write("管理/.records.lock", "other-process")
        before = self.snapshot()
        code, output = self.run_tool("sync")
        self.assertEqual(1, code)
        self.assertIn("存在写入锁", output)
        self.assertEqual(before, self.snapshot())

    def test_unknown_file_is_reported_and_preserved(self):
        self.assertEqual(0, self.run_tool("sync")[0])
        self.write("目录/测试/old.md", "# 旧页面\n")
        self.write("目录/测试/003.md", "# 别的领域 · 第 3 页\n\n> 自动生成；请编辑问题条目及领域综述。\n")
        before = self.snapshot()
        code, output = self.run_tool("sync")
        self.assertEqual(1, code)
        self.assertIn("未知文件", output)
        self.assertEqual(before, self.snapshot())

    def test_reversed_markers_and_orphan_appendix_are_reported(self):
        text = records.read(self.root / "测试.md")
        self.write("测试.md", text.replace("<!-- catalog:start -->\n<!-- catalog:end -->", "<!-- catalog:end -->\n<!-- catalog:start -->"))
        self.assertIn("生成区 catalog", self.run_tool("sync")[1])
        self.write("附录/q-20261027-999.md", "# 无所属问题\n")
        self.assertIn("附录缺少所属问题", self.run_tool("check")[1])

    def test_accepted_question_links_have_the_same_backlink(self):
        self.write("管理/兼容链接.json", json.dumps([{
            "domain": "测试", "title": "2026-10-27 · 问题 1", "id": "q-20261027-001"
        }], ensure_ascii=False))
        links = [
            "[[条目/q-20261027-001|稳定编号]]",
            "[普通链接](q-20261027-001.md)",
            "[[测试#2026-10-27 · 问题 1|旧标题]]",
            "[旧标题](../测试.md#2026-10-27%20%C2%B7%20问题%201)",
        ]
        for link in links:
            with self.subTest(link=link):
                self.add_entry(2, "\n" + link + "\n")
                self.assertEqual(0, self.run_tool("sync")[0])
                self.assertEqual(0, self.run_tool("check")[0])
                code, output = self.run_tool("backlinks", "q-20261027-001")
                self.assertEqual(0, code)
                self.assertIn("q-20261027-002.md", output)
                self.assertIn("1 个问题引用", output)

    def test_appendix_targets_belong_to_their_question(self):
        self.add_entry(1, "\n[[附录/q-20261027-001|详细内容]]\n")
        self.write("附录/q-20261027-001.md", "# 详细内容\n\n## 具体段落\n\n证据\n")
        for link in ["[[附录/q-20261027-001#具体段落]]", "[详细证据](../附录/q-20261027-001.md#具体段落)"]:
            with self.subTest(link=link):
                self.add_entry(2, "\n" + link + "\n")
                self.assertEqual(0, self.run_tool("sync")[0])
                self.assertEqual(0, self.run_tool("check")[0])
                output = self.run_tool("backlinks", "q-20261027-001")[1]
                self.assertIn("q-20261027-002.md", output)
                self.assertNotIn("q-20261027-001.md |", output)

    def test_source_question_is_deduplicated_and_self_links_are_excluded(self):
        self.add_entry(1, "\n[[附录/q-20261027-001]]\n[[条目/q-20261027-001]]\n")
        self.write("附录/q-20261027-001.md", "# 附录\n\n[[条目/q-20261027-001|返回]]\n")
        self.add_entry(2, "\n[[附录/q-20261027-002]]\n[[条目/q-20261027-001]]\n[再次引用](q-20261027-001.md)\n")
        self.write("附录/q-20261027-002.md", "# 附录\n\n[[条目/q-20261027-002|返回]]\n[相对引用](../条目/q-20261027-001.md)\n")
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])
        output = self.run_tool("backlinks", "q-20261027-001")[1]
        self.assertIn("1 个问题引用", output)
        self.assertEqual(1, output.count("q-20261027-002.md"))
        self.assertNotIn("q-20261027-001.md |", output)

    def test_appendix_local_anchors_keep_their_document_location(self):
        self.add_entry(1, "\n[详细内容](../附录/q-20261027-001.md)\n")
        self.write("附录/q-20261027-001.md", "# 附录\n\n## 仅在附录\n\n[[#仅在附录]]\n[同页](#仅在附录)\n")
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])
        self.assertIn("0 个问题引用", self.run_tool("backlinks", "q-20261027-001")[1])

    def test_markdown_anchors_are_checked_before_counting_references(self):
        for link in ["[坏标题](q-20261027-001.md#不存在)", "[坏标题](#不存在)"]:
            with self.subTest(link=link):
                self.add_entry(2, "\n" + link + "\n")
                code, output = self.run_tool("sync")
                self.assertEqual(1, code)
                self.assertIn("无效标题", output)
                self.assertIn("0 个问题引用", self.run_tool("backlinks", "q-20261027-001")[1])

    def test_generated_navigation_and_examples_do_not_create_backlinks(self):
        self.write("管理/兼容链接.json", json.dumps([{
            "domain": "测试", "title": "2026-10-27 · 问题 1", "id": "q-20261027-001"
        }], ensure_ascii=False))
        self.add_entry(2, "\n`[示例](q-20261027-001.md)`\n\n~~~markdown\n[[条目/q-20261027-001]]\n~~~\n")
        self.assertEqual(0, self.run_tool("sync")[0])
        self.assertEqual(0, self.run_tool("check")[0])
        self.assertIn("0 个问题引用", self.run_tool("backlinks", "q-20261027-001")[1])

    def test_unrelated_domain_damage_does_not_block_scoped_find(self):
        self.write("条目/q-20261027-009.md", '---\nid: q-20261027-002\ndomain: "乙"\n---\n\n# 2026-10-27 · 错位\n\n- **问**：x\n- **答**：y\n- **信源**：\n  - [一手] [a](https://example.org)\n')
        code, output = self.run_tool("find", "问题 1", "--domain", "测试")
        self.assertEqual(0, code)
        self.assertIn("q-20261027-001.md", output)
        self.assertIn("DIAG 其他领域 · q-20261027-009.md: 文件名与 id 不符", output)

    def test_local_domain_damage_degrades_to_diagnostic(self):
        self.add_entry(2, "\n- **更新**：2020-01-01\n")
        code, output = self.run_tool("find", "问题 1", "--domain", "测试")
        self.assertEqual(0, code)
        self.assertIn("q-20261027-001.md", output)
        self.assertIn("DIAG 本领域 · q-20261027-002.md: 更新日期无效", output)

    def test_check_still_fails_on_the_same_damage(self):
        self.assertEqual(0, self.run_tool("sync")[0])
        text = records.read(self.root / "条目/q-20261027-001.md")
        self.write("条目/q-20261027-001.md", text + "\n- **更新**：2020-01-01\n")
        code, output = self.run_tool("check")
        self.assertEqual(1, code)
        self.assertIn("更新日期无效", output)

    def test_scoped_find_does_not_read_unrelated_bodies_or_index(self):
        self.add_entry(2, domain="乙")
        counted = []
        original = knowledge.read

        def counting(path):
            if Path(path).name in {"q-20261027-002.md", "索引.md"}:
                counted.append(Path(path).name)
            return original(path)

        knowledge.read = counting
        try:
            code, output = self.run_tool("find", "问题 1", "--domain", "测试")
        finally:
            knowledge.read = original
        self.assertEqual(0, code)
        self.assertIn("q-20261027-001.md", output)
        self.assertEqual([], counted)

    def test_backlinks_degrades_and_warns_incomplete(self):
        self.add_entry(2, "\n- **更新**：2020-01-01\n")
        self.add_entry(3, "\n[[条目/q-20261027-001|相关]]\n")
        code, output = self.run_tool("backlinks", "q-20261027-001")
        self.assertEqual(0, code)
        self.assertIn("q-20261027-003.md", output)
        self.assertIn("1 个问题引用", output)
        self.assertIn("DIAG 未归属 · 1 条未解析，入链可能不全", output)

    def test_backlinks_rejects_missing_or_unparseable_target(self):
        self.add_entry(2, "\n- **更新**：2020-01-01\n")
        code, output = self.run_tool("backlinks", "q-20261027-999")
        self.assertEqual(1, code)
        self.assertIn("条目不存在", output)
        code, output = self.run_tool("backlinks", "q-20261027-002")
        self.assertEqual(1, code)
        self.assertIn("目标条目无法解析", output)

    def test_find_is_independent_of_index_health(self):
        self.write("索引.md", "# 索引\n\n坏行 —— 没有完整格式\n")
        code, output = self.run_tool("find", "问题 1", "--domain", "测试")
        self.assertEqual(0, code)
        self.assertIn("q-20261027-001.md", output)


if __name__ == "__main__":
    unittest.main()
