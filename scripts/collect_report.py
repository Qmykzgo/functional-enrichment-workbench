#!/usr/bin/env python3
"""Aggregate ORA and ranked enrichment TSVs into a provenance-aware report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(paths: list[Path]) -> list[tuple[Path, list[str], list[str]]]:
    rows: list[tuple[Path, list[str], list[str]]] = []
    for path in sorted(paths, key=lambda item: item.name):
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader((line for line in handle if not line.startswith("#")), delimiter="\t")
            header = next(reader)
            for row in reader:
                rows.append((path, header, row))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    rows = read_rows(args.reports)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["source_file", "analysis_mode", "columns", "row"])
        for source, header, row in rows:
            mode = "ranked" if "enrichment_score" in header else "ora"
            writer.writerow([source.name, mode, ",".join(header), "\t".join(row)])
    with args.markdown.open("w", encoding="utf-8") as handle:
        handle.write("# Functional-enrichment summary\n\n")
        handle.write("This report preserves ORA and ranked-list outputs as separate evidence layers. ORA statistics depend on the declared universe and multiple-testing family. Ranked scores are descriptive unless a validated null model is supplied. `STUB` fixtures make no biological claim.\n\n")
        handle.write("| source | mode | result row |\n| --- | --- | --- |\n")
        for source, header, row in rows:
            mode = "ranked" if "enrichment_score" in header else "ora"
            display_row = "; ".join(row).replace("|", "\\|")
            handle.write(f"| {source.name} | {mode} | {display_row} |\n")
        handle.write("\n## Interpretation guardrails\n\n")
        handle.write("Enrichment is annotation-overlap evidence under a defined model. It is not proof of pathway activation, mechanism, causality, treatment effect, or clinical significance.\n")
    print(f"Wrote {len(rows)} enrichment report rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
