"""
Core logic for cleaning duplicate chapters in novel files.
"""
import json
from pathlib import Path
from novel_cli.utils.text import get_chapter_match, detect_encoding
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

def load_replacements(config_path: Path | None = None) -> dict[str, str]:
    """
    Load replacements from configuration file if provided.
    Otherwise uses default hardcoded values.

    Args:
        config_path: Optional path to a JSON configuration file.

    Returns:
        Dictionary of replacements.
    """
    replacements = DEFAULT_REPLACEMENTS.copy()

    if config_path:
        # Resolve to absolute path if needed, though usually handled by caller
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    if isinstance(user_config, dict):
                        replacements.update(user_config)
            except Exception:
                # If explicit config fails, we might want to warn, but keeping it simple for now
                pass

    return replacements

def apply_corrections(lines: list[str], replacements: dict[str, str]) -> list[str]:
    """
    Apply text replacements to a list of lines.
    """
    if not replacements:
        return lines

    corrected_lines = []
    for line in lines:
        for old, new in replacements.items():
            if old in line:
                line = line.replace(old, new)
        corrected_lines.append(line)
    return corrected_lines

def clean_content(lines: list[str], regex_pattern: str, replacements: dict[str, str]) -> list[str]:
    """
    Core logic to deduplicate chapters and fix typos.

    Strategies:
    1. Apply text corrections.
    2. Identify chapter titles using regex_pattern.
    3. If two chapter titles are identical (after stripping whitespace), keep the one with less leading indentation.
    """
    # Step 1: Apply text corrections
    lines = apply_corrections(lines, replacements)

    if not lines:
        return lines

    # Step 2: Deduplication
    # We use a set of indices to mark lines for deletion
    to_delete = set()

    # Identify all chapter titles first to avoid repeated regex matching
    # structure: list of (line_index, match_object, stripped_content, indentation_level)
    chapter_indices = []
    for idx, line in enumerate(lines):
        match = get_chapter_match(line, regex_pattern)
        if match:
            indent = len(line) - len(line.lstrip())
            chapter_indices.append({
                'index': idx,
                'content': line.strip(),
                'indent': indent
            })

    # Compare adjacent chapter titles
    # We iterate through the identified chapters
    i = 0
    while i < len(chapter_indices) - 1:
        current_chap = chapter_indices[i]
        next_chap = chapter_indices[i+1]

        # Check if contents are identical
        if current_chap['content'] == next_chap['content']:
            # Duplicate found!
            # Prefer the one with less indentation
            if current_chap['indent'] <= next_chap['indent']:
                # Keep current, mark next for deletion
                to_delete.add(next_chap['index'])
                # Effectively, we skip the 'next_chap' in the next comparison
                # The 'current_chap' (i) will now be compared with i+2
                # So we delete i+1 from our logical list of chapters to compare
                del chapter_indices[i+1]
                # i stays the same, so we compare current against the new next
                continue
            else:
                # Keep next, mark current for deletion
                to_delete.add(current_chap['index'])
                # We move to next pair, but since current is deleted,
                # effectively next_chap becomes the new 'current' for the next iteration
                i += 1
        else:
            i += 1

    # Construct new content
    cleaned_lines = [line for idx, line in enumerate(lines) if idx not in to_delete]

    return cleaned_lines

def deduplicate_chapters(input_path: Path, regex_pattern: str, config_path: Path | None = None) -> Path:
    """
    Remove duplicate chapters from the input file and fix common typos.
    Wrapper around clean_content that handles file IO.

    Args:
        input_path: Path to the input novel file.
        regex_pattern: Regex pattern to identify chapter titles.
        config_path: Optional path to replacements config JSON.

    Returns:
        Path to the cleaned file.
    """
    encoding = detect_encoding(input_path)
    lines: list[str] = []

    with input_path.open('r', encoding=encoding) as f:
        lines = f.readlines()

    if not lines:
        return input_path

    # Load config
    replacements = load_replacements(config_path)

    # Process
    cleaned_lines = clean_content(lines, regex_pattern, replacements)

    # Save to a new file using atomic_write for safety
    output_path = input_path.with_name(f"{input_path.stem}_clean{input_path.suffix}")

    with atomic_write(output_path) as temp_path:
        with open(temp_path, 'w', encoding=encoding) as f:
            f.writelines(cleaned_lines)

    return output_path
