"""
Core logic for extracting chapters from novel files.
"""
import logging
import re
from pathlib import Path
from typing import Generator, List, Optional, Tuple, Union

from ..utils.file import atomic_write
from ..utils.text import DEFAULT_CHAPTER_PATTERN, detect_encoding, sanitize_filename

logger = logging.getLogger(__name__)


def iter_chapters(
    input_path: Union[str, Path],
    start_pattern: Optional[str],
    count: int,
    regex_pattern: str = DEFAULT_CHAPTER_PATTERN
) -> Generator[Tuple[str, str, int], None, None]:
    """
    Generator that iterates over chapters in the novel file.

    Yields:
        Tuple[str, str, int]: (chapter_title, chapter_content, chapter_index)
        chapter_index is 1-based index of the extracted chapter.
    """
    input_file = Path(input_path)
    encoding = detect_encoding(input_file)
    
    chapter_regex = re.compile(regex_pattern)

    found_start = False
    chapters_extracted = 0
    current_title = ""
    current_content: List[str] = []

    try:
        with input_file.open('r', encoding=encoding) as infile:
            for line in infile:
                match = chapter_regex.match(line)

                if match:
                    # Use the full line as the title, not just the matching prefix
                    new_title = line.strip()
                    
                    # If we haven't found the start yet
                    if not found_start:
                        if start_pattern is None or start_pattern in new_title:
                            found_start = True
                            current_title = new_title
                            current_content = [line]
                        continue
                    
                    # We have found the start, thus we have a previous chapter to yield
                    chapters_extracted += 1
                    yield current_title, "".join(current_content), chapters_extracted

                    if count > 0 and chapters_extracted >= count:
                        current_title = ""
                        current_content = []
                        return

                    current_title = new_title
                    current_content = [line]
                
                elif found_start:
                    current_content.append(line)

            # Yield last chapter if we are still collecting
            if found_start and current_title:
                 chapters_extracted += 1
                 yield current_title, "".join(current_content), chapters_extracted

    except (IOError, OSError) as e:
        logger.error("Error reading file: %s", e)
        raise


def extract(
    input_path: Union[str, Path],
    start_pattern: Optional[str],
    count: int,
    regex_pattern: str = DEFAULT_CHAPTER_PATTERN
) -> Optional[str]:
    """
    Streams the input file, finds the starting chapter, and writes N chapters to a file.
    Returns the path to the output file as a string.
    """
    input_file = Path(input_path)

    first_chapter_title = None
    last_chapter_title = None
    chapters_found = 0

    # Determine final filename after we know the chapters
    # Use a placeholder that we'll rename
    temp_final = input_file.parent / f"{input_file.stem}_extract_temp{input_file.suffix}"

    with atomic_write(temp_final) as temp_path:
        with temp_path.open('w', encoding='utf-8') as outfile:
            for title, content, idx in iter_chapters(input_file, start_pattern, count, regex_pattern):
                if idx == 1:
                    first_chapter_title = title
                last_chapter_title = title
                outfile.write(content)
                chapters_found += 1

    if chapters_found > 0 and first_chapter_title:
        safe_start = sanitize_filename(first_chapter_title)
        safe_end = sanitize_filename(last_chapter_title) if last_chapter_title else safe_start

        if safe_start == safe_end or count == 1:
            final_filename = input_file.with_name(f"{input_file.stem}_{safe_start}{input_file.suffix}")
        else:
            final_filename = input_file.with_name(f"{input_file.stem}_{safe_start}_{safe_end}{input_file.suffix}")

        # Rename from temp_final to actual final name
        if final_filename.exists():
            final_filename.unlink()
        temp_final.rename(final_filename)
        return str(final_filename)
    else:
        # Clean up if nothing was extracted
        if temp_final.exists():
            temp_final.unlink()
        return None
