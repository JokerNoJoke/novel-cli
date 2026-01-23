import unittest
import tempfile
import shutil
from pathlib import Path
from novel_cli.core import volume

class TestVolume(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.sample_path = self.test_dir / "novel.txt"
        
        # 10 chapters
        content_lines = []
        for i in range(1, 11):
            content_lines.append(f"第{i}章 Chapter {i}\nContent {i}\n")
            
        self.sample_path.write_text("".join(content_lines), encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_markers(self):
        # 5 chapters per volume
        output = volume.add_markers(self.sample_path, volume_step=5)
        
        content = Path(output).read_text(encoding='utf-8')
        
        self.assertIn("第1卷", content) # Should appear after chapter 5 (index 4 in 0-based if strict, but logic says count % step == 0)
        # Logic check:
        # count starts at 0.
        # Match Ch1 (count=0). 0 % 5 == 0 -> Vol 1 inserted before Ch1?
        # Let's check logic:
        # if match:
        #    if count % step == 0: write vol marker
        #    count += 1
        # output.write(line)
        # So Vol 1 is before Ch1.
        
        self.assertEqual(content.count("第1卷"), 1)
        self.assertEqual(content.count("第2卷"), 1) # Before Ch6 (count=5)
