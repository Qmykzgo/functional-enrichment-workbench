#!/usr/bin/env python3
"""CLI for evidence-aware functional enrichment."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

try:
    from .core import GeneSet, ora, ranked_enrichment
except ImportError:
    from core import GeneSet, ora, ranked_enrichment


def read_gene_sets(path: Path) -> list[GeneSet]:
    sets: list[GeneSet] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            sets.append(GeneSet(row["set_id"], row["description"], frozenset(row["genes"].split(","))))
    return sets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gene-sets", required=True, type=Path)
    parser.add_argument("--query", required=True, type=Path, help="One gene per line for ORA, or gene\\tscore for ranked")
    parser.add_argument("--universe", type=Path, help="Required for ORA")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=["ora", "ranked"], default="ora")
    parser.add_argument("--min-size", type=int, default=2)
    args = parser.parse_args()
    gene_sets = read_gene_sets(args.gene_sets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "ora":
        if not args.universe:
            print("ERROR: --universe is required for ORA", file=sys.stderr)
            return 1
        query = args.query.read_text(encoding="utf-8").splitlines()
        universe = args.universe.read_text(encoding="utf-8").splitlines()
        results = ora(query, universe, gene_sets, args.min_size)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(["set_id", "description", "overlap", "set_size", "query_size", "universe_size", "expected", "p_value", "q_value", "direction", "leading_genes"])
            for r in results:
                writer.writerow([r.set_id, r.description, r.overlap_size, r.set_size, r.query_size, r.universe_size, f"{r.expected_overlap:.4f}", f"{r.p_value:.4e}", f"{r.q_value:.4e}", r.direction, ",".join(r.leading_genes)])
    else:
        ranked = []
        with args.query.open(newline="", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip() or line.startswith("#"):
                    continue
                fields = line.strip().split("\t")
                if fields[0].lower() == "gene":
                    continue
                ranked.append((fields[0], float(fields[1]) if len(fields) > 1 else 1.0))
        results = ranked_enrichment(ranked, gene_sets, args.min_size)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(["set_id", "description", "set_size", "observed", "enrichment_score", "status", "leading_genes"])
            for r in results:
                writer.writerow([r.set_id, r.description, r.set_size, r.observed_genes, f"{r.enrichment_score:.4f}", r.status, ",".join(r.leading_genes)])
    print(f"Wrote {len(results)} enrichment rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
