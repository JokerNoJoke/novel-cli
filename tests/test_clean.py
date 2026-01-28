import unittest
import tempfile
import shutil
import json
from pathlib import Path
from novel_cli.core.clean import deduplicate_chapters, clean_content

class TestCleanFeature(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.input_path = self.test_dir / "test_novel.txt"
        self.config_path = self.test_dir / "novel_cli_replacements.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_correction_and_deduplication(self):
        # Create input file with typos and duplicate chapters
        content = [
            "第1章 开始\n",
            "这幺好的天气，那幺多人。\n", # Typos: 这幺 -> 这么, 那幺 -> 那么
            "第2章 中间\n", # Duplicate chapter title
            "第2章 中间\n", # Duplicate chapter title (should be removed)
            "什幺是快乐？怎幺寻找？\n", # Typos: 什幺 -> 什么, 怎幺 -> 怎么
            "   什幺是快乐？怎幺寻找？\n", # Duplicate content with more indentation
            "第3章 结束\n",
            "正常内容。\n"
        ]

        with open(self.input_path, 'w', encoding='utf-8') as f:
            f.writelines(content)

        # Run clean command
        output_path = deduplicate_chapters(self.input_path, r"^\s*第[0-9]+章")

        # Verify result
        self.assertTrue(output_path.exists())

        with open(output_path, 'r', encoding='utf-8') as f:
            result = f.read()

        # Check corrections
        self.assertIn("这么好的天气", result)
        self.assertNotIn("这幺", result)
        self.assertIn("那么多人", result)
        self.assertNotIn("那幺", result)
        self.assertIn("什么是快乐", result)
        self.assertNotIn("什幺", result)
        self.assertIn("怎么寻找", result)
        self.assertNotIn("怎幺", result)

        # Check deduplication (should only have one "第2章")
        self.assertEqual(result.count("第2章"), 1)

    def test_custom_config(self):
        # Create custom config in the test directory
        custom_replacements = {
            "foo": "bar",
            "这幺": "这幺" # Override default to keep it (test valid JSON loading)
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(custom_replacements, f)

        # Create input file
        content = ["第1章 测试\n", "This is foo text. 这幺\n"]
        with open(self.input_path, 'w', encoding='utf-8') as f:
            f.writelines(content)

        # Run clean command with explicit config path
        output_path = deduplicate_chapters(
            self.input_path,
            r"^\s*第[0-9]+章",
            config_path=self.config_path
        )

        with open(output_path, 'r', encoding='utf-8') as f:
            result = f.read()

        # "foo" should become "bar"
        self.assertIn("This is bar text.", result)
        # "这幺" should stay "这幺" because we overrode it in custom config
        self.assertIn("这幺", result)

    def test_clean_content_logic_pure(self):
        """Test the core logic without file IO"""
        lines = [
            "Chapter 1\n",
            "Content A\n",
            "Chapter 1\n", # Duplicate, should be removed (indentation tie-breaker or first one kept)
            "Content B\n",
            "Chapter 2\n",
            "   Chapter 2\n", # Duplicate with indent, should be removed
            "Content C\n"
        ]

        # Scenario: adjacent duplicates.
        # Our logic checks if contents are identical.
        # Here "Chapter 1\n" == "Chapter 1\n". Indents are 0 and 0.
        # Logic: if curr_indent <= next_indent (0<=0): keep current, delete next.

        # "Chapter 2\n" (indent 0) vs "   Chapter 2\n" (indent 3).
        # 0 <= 3: keep current, delete next.

        cleaned = clean_content(lines, r"^\s*Chapter \d+", replacements={})

        self.assertEqual(len(cleaned), 5)
        self.assertEqual(cleaned[0], "Chapter 1\n")
        self.assertEqual(cleaned[1], "Content A\n")
        # Second Chapter 1 removed
        self.assertEqual(cleaned[2], "Content B\n")
        self.assertEqual(cleaned[3], "Chapter 2\n")
        # Indented Chapter 2 removed
        self.assertEqual(cleaned[4], "Content C\n")

if __name__ == '__main__':
    unittest.main()
