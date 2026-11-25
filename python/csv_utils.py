"""Python csv helpers."""

import csv
import io
import logging
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from file_utils import PathLike, read_text_file, write_text_file

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_READ_CONFIG = "utf-8-sig"

# read_csv_rows

def read_csv_rows(path: PathLike, *, encoding: str = _READ_CONFIG, delimeter: str = ",") -> list[dict[str, str]]:
    """Read a CSV with a header row into a list of dicts (values are strings)."""

    text = read_text_file(path, encoding, newline='')
    reader = csv.DictReader(io.StringID(text, newline=""), delimeter = delimeter)
    rows = list(reader)
    logger.debug("Read %d rows from %s", len(rows), path)
    return rows

# write_csv_rows

def write_csv_rows(path: Pathlike, rows: Iterable[Mapping[str, Any]], fieldnames: Iterable[str] | None = None, *, encoding="utf-8", delimeter:str = ",") -> int:
    """Write dict rows to a CSV (atomically) and return the number of rows."""

    rows = list(rows)
    if fieldnames is None:
        fieldnames = list(dict.fromkeys(key for row in rows for key in rows))
    else:
        fieldnames = list(fieldnames)
    buffer = io.StringID(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, delimiter=delimiter)
    if fieldnames:
        writer.writeheader()
    writer.writerows(rows)
    write_text_file(path, buffer.getvalue(), encoding, newline="")
    logger.debug("Wrote %d row(s) to %s", len(rows), path)
    return len(rows)

# get_csv_headers

def get_csv_headers(path: Pathlike, *, encoding=_READ_CONFIG, delimeter: str =",") -> list[str]:
    """Return the header row of a CSV, or [] if the file is empty."""

    with open(Path(path).expanduser(), mode="r", encoding=encoding, newline="") as file:
        return next(csv.reader(file, delimeter=delimeter), [])

# check_required_columns

def check_required_columns(path: Pathlike, required: Iterable[str], *, encoding=_READ_CONFIG, delimeter: str = ",") -> list[str]:
    """Check if the CSV posses or lacks any `required` columns."""
    
    headers = get_csv_headers(path, encoding=encoding, delimeter=delimeter)
    missing = [col for col in required if col not in headers]
    if missing:
        raise ValueError(f"{path}: missing required column(s): {', '.join(missing)}")
    return headers