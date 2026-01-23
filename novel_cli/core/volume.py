"""
Core logic for adding volume markers to novel files.
"""
import logging
import re
from pathlib import Path
from typing import Union

from ..utils.file import atomic_write
from ..utils.text import DEFAULT_CHAPTER_PATTERN, detect_encoding

logger = logging.getLogger(__name__)


def add_markers(
    input_path: Union[str, Path],
    volume_step: int = 50,
    regex_pattern: str = DEFAULT_CHAPTER_PATTERN
) -> str:
    """
    Reads a novel file and adds volume markers every `volume_step` chapters.

    Args:
        input_path: Path to source novel file.
        volume_step: Number of chapters per volume.
        regex_pattern: Regex to identify chapter lines.

    Returns:
        The path to the generated output file.
    """
    input_file = Path(input_path)
    output_filename = input_file.with_name(f"{input_file.stem}_with_volumes{input_file.suffix}")
    encoding = detect_encoding(input_file)

    # Pre-compile regex for performance in loop
    chapter_regex = re.compile(regex_pattern)
    
    chapter_count = 0

    with atomic_write(output_filename) as temp_path:
        with input_file.open('r', encoding=encoding) as infile, \
             temp_path.open('w', encoding='utf-8') as outfile:

            for line in infile:
                # Use pre-compiled regex match
                match = chapter_regex.match(line)

                if match:
                    if chapter_count % volume_step == 0:
                        volume_num = (chapter_count // volume_step) + 1
                        outfile.write(f"\n第{volume_num}卷\n\n")

                    chapter_count += 1

                outfile.write(line)

    return str(output_filename)
