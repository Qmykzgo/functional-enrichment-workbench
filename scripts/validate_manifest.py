#!/usr/bin/env python3
"""Validate a functional-enrichment analysis manifest."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REQUIRED = {
    "sample", "query_genes", "ranked_genes", "universe_genes", "gene_sets",
    "species", "identifier_namespace", "gene_set_collection", "gene_set_release",
    "method", "alpha"
}
METHODS = {"ora", "ranked", "both"}


def validate(path: Path, check_paths: bool) -> list[str]:
    errors: list[str] = []
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or [])
            missing = REQUIRED - fields
            if missing:
                return [f"missing required columns: {', '.join(sorted(missing))}"]
            seen: set[str] = set()
            for line_number, raw in enumerate(reader, start=2):
                row = {key: (value or "").strip() for key, value in raw.items() if key}
                sample = row.get("sample", "")
                if not sample:
                    errors.append(f"line {line_number}: sample is required")
                if sample in seen:
                    errors.append(f"line {line_number}: duplicate sample '{sample}'")
                seen.add(sample)
                for field in sorted(REQUIRED - {"ranked_genes", "query_genes", "universe_genes"}):
                    if not row.get(field):
                        errors.append(f"line {line_number}: {field} is required")
                if row.get("method") not in METHODS:
                    errors.append(f"line {line_number}: method must be one of {sorted(METHODS)}")
                try:
                    alpha = float(row.get("alpha", ""))
                    if not 0 < alpha <= 1:
                        errors.append(f"line {line_number}: alpha must be in (0, 1]")
                except ValueError:
                    errors.append(f"line {line_number}: alpha must be numeric")
                if check_paths:
                    for field in ("query_genes", "ranked_genes", "universe_genes", "gene_sets"):
                        value = row.get(field, "")
                        if value and not Path(value).expanduser().exists():
                            errors.append(f"line {line_number}: {field} does not exist: {value}")
    except FileNotFoundError:
        errors.append(f"manifest not found: {path}")
    except csv.Error as exc:
        errors.append(f"CSV parsing error: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--check-paths", action="store_true")
    args = parser.parse_args()
    errors = validate(args.manifest, args.check_paths)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid enrichment manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
