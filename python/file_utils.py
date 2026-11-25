"""Python file helpers."""

from __future__ import annotations

import os
import uuid
import logging
from collections.abc import Iterable
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

type PathLike = str | os.PathLike[str]

# ensure_directory

def ensure_directory(directory: PathLike) -> Path:
    """Create `directory` (and parents) if needed and return it as a Path."""

    path = Path(directory).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    logger.debug("Ensured directory: %s", path)
    return path

# get_file_size

def get_file_size(path: Pathlike) -> int:
    "Return the size of a file in bites."

    path = Path(path).expanduser()    
    if path.is_dir():
        raise IsADirectoryError(f"Expected a file, got a directory: {path}")
    return path.stat().st_size

# read_text_file

def read_text_file(path: Pathlike, encoding:str = "utf-8", *, errors: str = "strict", newline: str | None = None) -> str:
    """Read an entire text file and return it's content as string."""

    path = Path(path).expanduser()
    with open(path, mode="r", encoding=encoding, errors=errors, newline=newline) as file:
        text = file.read()
    logger.debug("Read %d characters from %s", len(text), path)
    return text

# write_text_file

def write_text_file(path, text: str, encoding='utf-8', *, make_dirs=True, newline=None, errors='strict') -> Path:
    """Write text to a file and return the path."""

    path = Path(path).expanduser()
    if make_dirs:
        ensure_directory(path.parent)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with open(tmp, mode="x", encoding=encoding, errors=errors, newline=newline) as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        tmp.replace(path)          
    except BaseException:         
        tmp.unlink(missing_ok=True)
        raise
    logger.debug("Wrote %d characters to %s", len(text), path)
    return path

# find_files_by_extension

def find_files_by_extension(directory, extensions: str | Iterable[str], *, recursive=True) -> Lisr[Path]:
    """Return a sorted list of files in a directory that are extensions."""
    
    root = Path(directory).expanduser()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a director: {root}")
    if isinstance(extensions, str):
        extensions = list(extensions)
    suffixes = tuple("." + e.lower().lstrip(".") for e in extensions)
    if not suffixes or "." in suffixes:
        raise ValueError("Provide at least one non-empty extension.")
    canidates = root.rglob("*") if recursive else root.iterdir()
    found = sorted(p for p in candidares if p.is_file() and p.name.lower().endswith(suffixes))
    logger.debug("Found %d fill(s) in %s matching %s", len(found), root, suffixes)
    return found