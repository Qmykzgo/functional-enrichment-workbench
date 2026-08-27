"""Transparent ORA and ranked gene-set enrichment primitives."""

from .core import GeneSet, OraResult, RankedResult, benjamini_hochberg, ora, ranked_enrichment

__all__ = ["GeneSet", "OraResult", "RankedResult", "benjamini_hochberg", "ora", "ranked_enrichment"]
