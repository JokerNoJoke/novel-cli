"""
Utility modules for novel-cli.
"""
from .file import atomic_write
from .text import (
    DEFAULT_CHAPTER_PATTERN,
    detect_encoding,
    get_chapter_match,
    get_compiled_pattern,
    sanitize_filename,
)

__all__ = [
    "atomic_write",
    "DEFAULT_CHAPTER_PATTERN",
    "detect_encoding",
    "get_chapter_match",
    "get_compiled_pattern",
    "sanitize_filename",
]
