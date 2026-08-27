from enrichment.core import GeneSet, benjamini_hochberg, ora, ranked_enrichment


def test_benjamini_hochberg_is_monotone():
    p_values = [0.01, 0.04, 0.05, 0.5]
    q_values = benjamini_hochberg(p_values)
    assert q_values[0] <= q_values[1] <= q_values[2] <= q_values[3]
    assert q_values[0] == 0.04  # 0.01 * 4 / 1


def test_ora_detects_overrepresentation():
    universe = [f"G{i}" for i in range(100)]
    query = [f"G{i}" for i in range(10)]
    gene_sets = [
        GeneSet("S1", "Enriched", frozenset([f"G{i}" for i in range(5)])),
        GeneSet("S2", "Not Enriched", frozenset([f"G{i}" for i in range(50, 60)])),
    ]
    results = ora(query, universe, gene_sets)
    assert results[0].set_id == "S1"
    assert results[0].overlap_size == 5
    assert results[0].direction == "overrepresented"
    assert results[0].p_value < 0.001


def test_ranked_enrichment_running_sum():
    ranked = [("G1", 10.0), ("G2", 5.0), ("G3", 1.0), ("G4", -1.0), ("G5", -10.0)]
    gene_sets = [GeneSet("S1", "Top", frozenset(["G1", "G2"]))]
    results = ranked_enrichment(ranked, gene_sets)
    assert results[0].enrichment_score > 0.5
    assert "G1" in results[0].leading_genes
