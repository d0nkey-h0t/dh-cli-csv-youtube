"""CSV loading utilities."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterable, Iterator, Union


def read_rows(
    paths: Union[str, Path, Iterable[Union[str, Path]]],
    skip_missing: bool = True,
    verbose: bool = True,
) -> Iterator[dict[str, str]]:
    """Yield rows from one or more CSV files as dicts.

    Each file must have a header row. Rows are yielded in the order
    files are passed and in document order within each file.
    """
    # Поддержка единичного пути
    if isinstance(paths, (str, Path)):
        paths = [paths]

    for path in paths:
        path_obj = Path(path)
        try:
            if not path_obj.exists():
                if skip_missing:
                    if verbose:
                        print(f"Warning: Skipping missing file: {path_obj}", file=sys.stderr)
                    continue
                else:
                    raise FileNotFoundError(f"CSV file not found: {path_obj}")

            if path_obj.is_dir():
                raise IsADirectoryError(f"Is a directory (not a file): {path_obj}")

            with path_obj.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames is None:
                    raise ValueError(f"CSV file has no header: {path_obj}")

                for row in reader:
                    clean_row = {key: row[key] for key in reader.fieldnames if key in row}
                    yield clean_row

        except (FileNotFoundError, IsADirectoryError) as e:
            if not skip_missing:
                raise e
            if verbose:
                print(f"Warning: {e}", file=sys.stderr)
        except PermissionError as e:
            msg = f"Permission denied when reading CSV: {path_obj}"
            if not skip_missing:
                raise PermissionError(msg) from e
            if verbose:
                print(f"Warning: {msg}", file=sys.stderr)
        except UnicodeDecodeError as e:
            msg = f"Cannot decode CSV as UTF-8: {path_obj}. Check encoding."
            if not skip_missing:
                raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, msg) from None
            if verbose:
                print(f"Warning: {msg}", file=sys.stderr)
        except Exception as e:
            msg = f"Unexpected error reading CSV file {path_obj}: {type(e).__name__}: {e}"
            if not skip_missing:
                raise RuntimeError(msg) from e
            if verbose:
                print(f"Warning: {msg}", file=sys.stderr)


def load_rows(
    paths: Union[str, Path, Iterable[Union[str, Path]]],
    skip_missing: bool = True,
    verbose: bool = True,
) -> list[dict[str, str]]:
    """Read all rows from the given files into a single list."""
    return list(read_rows(paths, skip_missing=skip_missing, verbose=verbose))
