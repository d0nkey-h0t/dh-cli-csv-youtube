# youtube_reports

CLI utility that reads YouTube video metrics from CSV files and prints reports
to the console.

## Usage

```bash
python -m youtube_reports --files examples/videos.csv --report clickbait
```

Multiple files can be combined into a single report:

```bash
python -m youtube_reports --files file_a.csv file_b.csv --report clickbait
```

### Available reports

- `clickbait` — videos with CTR > 15 and `retention_rate` < 40, sorted by CTR
  descending. Columns: `title`, `ctr`, `retention_rate`.

## Adding a new report

1. Create a module under `youtube_reports/reports/`.
2. Subclass `youtube_reports.reports.base.Report`, set a unique `name`,
   declare `headers`, and implement `build(rows)`.
3. Import it in `youtube_reports/reports/__init__.py` so it gets registered.

The new report becomes available automatically as a `--report` option.

## Development

Install dependencies:

```bash
pip install tabulate pytest
```

Run the tests:

```bash
pytest
```
