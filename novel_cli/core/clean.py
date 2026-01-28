"""
Core logic for cleaning duplicate chapters in novel files.
"""
import json
import os
from pathlib import Path
from typing import List, Dict
import re
from novel_cli.utils.text import get_chapter_match, detect_encoding, sanitize_filename
from novel_cli.utils.file import atomic_write

# Default replacements for common typos
DEFAULT_REPLACEMENTS = {
    "这幺": "这么",
    "那幺": "那么",
    "什幺": "什么",
    "怎幺": "怎么",
    "特幺": "特么",
    "要幺": "要么",
    "多幺": "多么",
    "的幺": "的么"
}

CONFIG_FILENAME = "novel_cli_replacements.json"

def load_replacements() -> Dict[str, str]:
    """
    Load replacements from configuration files.
    Priority:
    1. Current working directory config
    2. Home directory config (~/.novel_cli/)
    3. Default hardcoded values
    """
    replacements = DEFAULT_REPLACEMENTS.copy()

    # Check home directory
    home_config = Path.home() / ".novel_cli" / CONFIG_FILENAME
    if home_config.exists():
        try:
            with open(home_config, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                replacements.update(user_config)
        except Exception:
            pass # Ignore config errors

    # Check current directory (overrides home)
    cwd_config = Path.cwd() / CONFIG_FILENAME
    if cwd_config.exists():
        try:
            with open(cwd_config, 'r', encoding='utf-8') as f:
                cwd_replacements = json.load(f)
                replacements.update(cwd_replacements)
        except Exception:
            pass

    return replacements

def apply_corrections(lines: List[str]) -> List[str]:
    """
    Apply text replacements to a list of lines.
    """
    replacements = load_replacements()
    if not replacements:
        return lines

    corrected_lines = []
    for line in lines:
        for old, new in replacements.items():
            if old in line:
                line = line.replace(old, new)
        corrected_lines.append(line)
    return corrected_lines

def deduplicate_chapters(input_path: Path, regex_pattern: str) -> Path:
    """
    Remove duplicate chapters from the input file and fix common typos.
    Strategies:
    1. Apply text corrections (e.g. "这幺" -> "这么")
    2. Identify chapter titles using regex_pattern.
    3. If two adjacent chapter titles are identical (after stripping whitespace), keep the one with less leading indentation.

    Args:
        input_path: Path to the input novel file.
        regex_pattern: Regex pattern to identify chapter titles.

    Returns:
        Path to the cleaned file.
    """
    encoding = detect_encoding(input_path)
    lines: List[str] = []

    with input_path.open('r', encoding=encoding) as f:
        lines = f.readlines()

    if not lines:
        return input_path

    # Step 1: Apply text corrections
    lines = apply_corrections(lines)

    # Step 2: Deduplication
    to_delete = [False] * len(lines)

    # Iterate through lines to find duplicates
    # We look at pairs of i and i+1
    i = 0
    while i < len(lines) - 1:
        current_line = lines[i]
        next_line = lines[i+1]

        # Check if both are chapter titles
        curr_match = get_chapter_match(current_line, regex_pattern)
        next_match = get_chapter_match(next_line, regex_pattern)

        if curr_match and next_match:
            # Check if contents are identical stripped
            if current_line.strip() == next_line.strip():
                # Duplicate found!
                # Prefer the one with less indentation (length of leading whitespace)
                curr_indent = len(current_line) - len(current_line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())

                if curr_indent <= next_indent:
                    # Keep current, delete next
                    to_delete[i+1] = True
                    # Look ahead logic handled by just marking and moving to next iteration
                    pass
                else:
                    # Keep next, delete current
                    to_delete[i] = True

        i += 1

    # Construct new content
    cleaned_lines = [line for idx, line in enumerate(lines) if not to_delete[idx]]

    # Save to a new file using atomic_write for safety
    output_path = input_path.with_name(f"{input_path.stem}_clean{input_path.suffix}")

    with atomic_write(output_path) as temp_path:
        with open(temp_path, 'w', encoding=encoding) as f:
            f.writelines(cleaned_lines)

    return output_path
