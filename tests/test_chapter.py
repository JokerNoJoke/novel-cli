import unittest
import tempfile
import shutil
from pathlib import Path
from novel_cli.core import chapter

class TestChapter(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.sample_file = self.test_dir / "sample.txt"
        
        # Create a sample novel
        content = """Preface
Line 1

第1章 Chapter One
Content of chapter 1.
More content.

第2章 Chapter Two
Content of chapter 2.

第3章 Chapter Three
Content of chapter 3.
"""
        self.sample_file.write_text(content, encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_iter_chapters_all(self):
        chapters = list(chapter.iter_chapters(self.sample_file, None, 10))
        self.assertEqual(len(chapters), 3)
        self.assertIn("第1章", chapters[0][0])
        self.assertIn("Content of chapter 1", chapters[0][1])

    def test_extract_specific(self):
        output = chapter.extract(self.sample_file, "第2章", 1)
        self.assertIsNotNone(output)
        content = Path(output).read_text(encoding='utf-8')
        self.assertIn("第2章", content)
        self.assertNotIn("第1章", content)
        self.assertNotIn("第3章", content)

    def test_count_limit(self):
        chapters = list(chapter.iter_chapters(self.sample_file, None, 2))
        self.assertEqual(len(chapters), 2)
