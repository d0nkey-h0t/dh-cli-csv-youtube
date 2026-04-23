"""Command-line entrypoint."""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

from tabulate import tabulate

from youtube_reports.csv_loader import read_rows
from youtube_reports.reports import available_reports, get_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtube_reports",
        description="Generate reports from YouTube video metrics CSV files.",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        metavar="FILE",
        help="Paths to one or more CSV files with video metrics.",
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=available_reports(),
        help="Name of the report to generate.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = get_report(args.report)
    table = report.build(read_rows(args.files))

    print(tabulate(table, headers=list(report.headers), tablefmt="simple"))
    return 0


def main() -> None:
    sys.exit(run())
