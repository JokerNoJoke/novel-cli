"""
Shared text utilities for novel-cli.
"""
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

# Default regex pattern for matching chapter titles
DEFAULT_CHAPTER_PATTERN = r"^\s*第[0-9零一二三四五六七八九十百千]+章(?:\s|$)"


@lru_cache(maxsize=8)
def get_compiled_pattern(pattern: str) -> re.Pattern:
    """
    Returns a cached compiled regex pattern.
    Uses LRU cache to avoid recompiling the same pattern.
    """
    return re.compile(pattern)


def get_chapter_match(line: str, pattern: str = DEFAULT_CHAPTER_PATTERN) -> Optional[re.Match]:
    """
    Checks if a line matches the chapter pattern.
    Uses cached compiled pattern for better performance.
    """
    compiled = get_compiled_pattern(pattern)
    return compiled.match(line)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use in filenames.
    Keeps only alphanumeric characters, underscores, and hyphens.
    """
    if not name:
        return "untitled"
    return "".join(c for c in name if c.isalnum() or c in ('_', '-')).strip()


def detect_encoding(file_path: Union[str, Path]) -> str:
    """
    Detect file encoding by attempting to read with UTF-8 first,
    falling back to GB18030 for Chinese text files.
    """
    path = Path(file_path)
    try:
        # Just read a small chunk
        with path.open('r', encoding='utf-8') as f:
            f.read(1024)
        return 'utf-8'
    except UnicodeDecodeError:
        return 'gb18030'
    except Exception:
        # Fallback safe default if something else goes wrong (e.g. file not found handling upstream)
        return 'utf-8'
