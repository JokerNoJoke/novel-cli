import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path
from novel_cli.core import tts

class TestTTS(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.sample_path = self.test_dir / "novel.txt"
        self.sample_path.write_text("第1章 One\nContent\n", encoding='utf-8')
        self.output_dir = self.test_dir / "novel_tts"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('urllib.request.urlopen')
    def test_process_tts(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"fake_audio_data"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        tts.process_tts(
            self.sample_path, 
            None, 
            1, 
            "http://fake.api", 
            "ref.wav", 
            concurrency=2
        )
        
        # Verify file created
        # 1_One (sanitized) -> 0001_One.wav
        # sanitize_filename removes spaces but keeps Chinese characters (isalnum)
        # "第1章 One" -> "第1章One"
        expected_file = self.output_dir / "0001_第1章One.wav"
        # We need to verify if the file exists. 
        # But wait, tts.py creates directory: input_file.parent / f"{input_file.stem}_tts"
        # stem is "novel", so "novel_tts"
        
        self.assertTrue(expected_file.exists())
        self.assertEqual(expected_file.read_bytes(), b"fake_audio_data")
