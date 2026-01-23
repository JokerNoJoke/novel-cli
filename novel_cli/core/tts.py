import json
import shutil
import logging
import urllib.request
import urllib.error
import time
from socket import timeout as SocketTimeout
from pathlib import Path
from typing import Optional, Union, Dict, Any, List

from .chapter import iter_chapters
from ..utils.text import DEFAULT_CHAPTER_PATTERN, sanitize_filename

logger = logging.getLogger(__name__)

# Default timeout for TTS requests (increased to 20 minutes)
DEFAULT_TIMEOUT = 1200
MAX_RETRIES = 3

def _tts_worker(
    text: str,
    title: str,
    idx: int,
    output_dir: Path,
    api_url: str,
    payload_template: Dict[str, Any]
) -> bool:
    """
    Worker function to process a single chapter.
    """
    safe_title = sanitize_filename(title)
    ext = payload_template.get("media_type", "wav")
    file_name = output_dir / f"{str(idx).zfill(4)}_{safe_title}.{ext}"
    
    if file_name.exists():
        logger.info(f"Skipping existing: {title}")
        return True

    payload = payload_template.copy()
    payload["text"] = text

    data = json.dumps(payload).encode('utf-8')
    
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                api_url, 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    with file_name.open('wb') as f:
                        shutil.copyfileobj(response, f)
                    return True
                else:
                    logger.error(f"Failed {title}: HTTP {response.status}")
                    # Non-200 responses might not be transient, but we can verify.
                    # Usually 5xx are transient, 4xx are not.
                    if 400 <= response.status < 500:
                         return False
        
        except (urllib.error.URLError, SocketTimeout) as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {title}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 * (attempt + 1)) # Backoff
        except Exception as e:
            logger.error(f"Error processing {title}: {e}")
            # If it's not a network error, maybe don't retry? 
            # But just to be safe let's treat it as failure and continue.
            return False
    
    logger.error(f"All {MAX_RETRIES} attempts failed for {title}")
    return False


def process_tts(
    input_path: Union[str, Path],
    start_pattern: Optional[str],
    count: int,
    api_url: str,
    ref_audio_path: str,
    regex_pattern: str = DEFAULT_CHAPTER_PATTERN
) -> str:
    """
    Iterates over chapters and calls TTS API for each sequentially.

    Args:
        input_path: Path to novel file.
        start_pattern: Start chapter pattern.
        count: Number of chapters to process.
        api_url: TTS API endpoint.
        ref_audio_path: Path to reference audio on the TTS server.
        regex_pattern: Regex for chapter detection.

    Returns:
        Path to the output directory as a string.
    """
    input_file = Path(input_path)
    output_dir = input_file.parent / f"{input_file.stem}_tts"
    
    output_dir.mkdir(exist_ok=True)

    payload_template: Dict[str, Any] = {
        "text_lang": "zh",
        "ref_audio_path": ref_audio_path,
        "prompt_lang": "zh",
        "prompt_text": "",
        "text_split_method": "cut3",
        "batch_size": 8,
        "seed": 0,
        "media_type": "aac",
        "streaming_mode": True
    }
    
    print("Starting TTS...")

    completed = 0
    for title, content, idx in iter_chapters(input_file, start_pattern, count, regex_pattern):
        try:
            success = _tts_worker(
                content, 
                title, 
                idx, 
                output_dir, 
                api_url, 
                payload_template
            )
            if success:
                completed += 1
                print(f"[{completed}] Completed: {title}")
            else:
                print(f"[{completed}] FAILED: {title}")
        except Exception as exc:
            print(f"[{completed}] EXCEPTION: {title} - {exc}")

    return str(output_dir)
