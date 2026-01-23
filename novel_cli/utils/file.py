"""
File utilities for novel-cli.
"""
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


@contextmanager
def atomic_write(output_path: Path, suffix: str = "") -> Generator[Path, None, None]:
    """
    Context manager for atomic file writing.
    
    Writes to a temporary file first, then atomically renames on success.
    Automatically cleans up the temp file on failure.
    
    Args:
        output_path: Final destination path.
        suffix: Optional suffix for the temp file (e.g., ".txt").
    
    Yields:
        Path to the temporary file for writing.
    """
    temp_path = output_path.parent / f"{output_path.stem}_{uuid.uuid4().hex[:8]}{suffix or output_path.suffix}"
    try:
        yield temp_path
        # Success: atomic rename
        if output_path.exists():
            output_path.unlink()
        temp_path.rename(output_path)
    except Exception:
        # Failure: cleanup temp file
        if temp_path.exists():
            temp_path.unlink()
        raise
