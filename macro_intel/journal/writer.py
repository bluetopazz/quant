from __future__ import annotations

import csv
import os

from .schema import get_pair_journal_schema


def append_row(log_file: str, fieldnames: tuple[str, ...] | list[str], row: dict[str, object]) -> None:
    file_exists = os.path.isfile(log_file)
    is_empty = os.path.getsize(log_file) == 0 if file_exists else True

    with open(log_file, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        if is_empty:
            writer.writeheader()
        writer.writerow(row)


def append_pair_journal(pair_id: str, row: dict[str, object], *, log_file: str | None = None) -> str:
    schema = get_pair_journal_schema(pair_id)
    destination = log_file or schema.log_file
    append_row(destination, schema.fieldnames, row)
    return destination
