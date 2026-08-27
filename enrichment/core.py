"""Evidence-aware functional enrichment primitives.

The baseline implements exact over-representation analysis (ORA) and a
transparent descriptive ranked-list enrichment score. It deliberately keeps
gene-set and identifier provenance outside the numerical routines.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterable, Sequence


@dataclass(frozen=True)
class GeneSet:
    set_id: str
    description: str
    genes: frozenset[str]


@dataclass(frozen=True)
class OraResult:
    set_id: str
    description: str
    overlap_size: int
    set_size: int
    query_size: int
    universe_size: int
    expected_overlap: float
    p_value: float
    q_value: float
    direction: str
    leading_genes: tuple[str, ...]


@dataclass(frozen=True)
class RankedResult:
    set_id: str
    description: str
    set_size: int
    observed_genes: int
    enrichment_score: float
    leading_genes: tuple[str, ...]
    status: str


def hypergeom_sf(at_least: int, population: int, successes: int, draws: int) -> float:
    """Return P(X >= at_least) for a finite-population hypergeometric draw."""
    if not 0 <= successes <= population or not 0 <= draws <= population:
        raise ValueError("invalid hypergeometric population or draw size")
    lower = max(at_least, draws - (population - successes))
    upper = min(draws, successes)
    denominator = comb(population, draws)
    return sum(comb(successes, x) * comb(population - successes, draws - x) for x in range(lower, upper + 1)) / denominator


def benjamini_hochberg(p_values: Sequence[float]) -> list[float]:
    """Return monotone Benjamini–Hochberg q-values in input order."""
    n = len(p_values)
    if not n:
        return []
    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    q_values = [1.0] * n
    running = 1.0
    for rank, (index, p_value) in reversed(list(enumerate(indexed, start=1))):
        running = min(running, p_value * n / rank)
        q_values[index] = min(1.0, running)
    return q_values


def ora(query_genes: Iterable[str], universe_genes: Iterable[str], gene_sets: Sequence[GeneSet], min_size: int = 2) -> list[OraResult]:
    """Compute ORA for a query against an explicit experiment universe."""
    query = frozenset(g.strip() for g in query_genes if g.strip())
    universe = frozenset(g.strip() for g in universe_genes if g.strip())
    if not query <= universe:
        raise ValueError("query contains genes absent from the declared universe")
    if not universe:
        raise ValueError("universe must not be empty")
    results: list[tuple[GeneSet, int, float, tuple[str, ...]]] = []
    for gene_set in gene_sets:
        genes = gene_set.genes & universe
        if len(genes) < min_size:
            continue
        overlap = query & genes
        p_value = hypergeom_sf(len(overlap), len(universe), len(genes), len(query))
        leading = tuple(sorted(overlap))
        results.append((gene_set, len(overlap), p_value, leading))
    q_values = benjamini_hochberg([item[2] for item in results])
    output: list[OraResult] = []
    for (gene_set, overlap, p_value, leading), q_value in zip(results, q_values):
        set_size = len(gene_set.genes & universe)
        expected = len(query) * set_size / len(universe)
        direction = "overrepresented" if overlap >= expected else "underrepresented"
        output.append(OraResult(gene_set.set_id, gene_set.description, overlap, set_size, len(query), len(universe), expected, p_value, q_value, direction, leading))
    return sorted(output, key=lambda result: (result.q_value, result.p_value, result.set_id))


def ranked_enrichment(ranked_genes: Sequence[tuple[str, float]], gene_sets: Sequence[GeneSet], min_size: int = 2) -> list[RankedResult]:
    """Compute a deterministic weighted running-sum enrichment score.

    This is a descriptive GSEA-like score. It does not generate a null model or
    permutation p-value; results are marked accordingly so a narrative cannot
    overstate significance.
    """
    ranked = [(gene, float(score)) for gene, score in ranked_genes if gene]
    scores = {gene: abs(score) for gene, score in ranked}
    total_weight = sum(scores.values()) or 1.0
    results: list[RankedResult] = []
    for gene_set in gene_sets:
        members = [gene for gene, _ in ranked if gene in gene_set.genes]
        if len(members) < min_size:
            continue
        hit_weight = sum(scores[gene] for gene in members) or float(len(members))
        miss_penalty = 1.0 / max(1, len(ranked) - len(members))
        running = 0.0
        maximum = (0.0, 0)
        minimum = (0.0, 0)
        member_set = set(members)
        for index, (gene, _) in enumerate(ranked, start=1):
            if gene in member_set:
                running += scores[gene] / hit_weight
            else:
                running -= miss_penalty
            if running > maximum[0]:
                maximum = (running, index)
            if running < minimum[0]:
                minimum = (running, index)
        es, edge = maximum if abs(maximum[0]) >= abs(minimum[0]) else minimum
        leading = tuple(gene for gene, _ in ranked[:edge] if gene in member_set)
        results.append(RankedResult(gene_set.set_id, gene_set.description, len(members), len(members), round(es, 6), leading, "RANKED_DESCRIPTIVE"))
    return sorted(results, key=lambda result: (-abs(result.enrichment_score), result.set_id))
