---
name: functional-enrichment-workbench
description: Plans and interprets over-representation and ranked gene-set enrichment analyses with explicit universes, multiple-testing correction, identifier resolution, and gene-set provenance. Use when an agent must turn differential or ranked gene lists into statistically qualified functional evidence without overstating pathways as mechanisms.
tool_type: mixed
primary_tool: Python
workflow: true
depends_on:
  - differential-expression
  - gene-sets
  - statistical-testing
  - database-access
qc_checkpoints:
  inputs: "Query, eligible universe, species, identifier namespace, and gene-set release are explicit"
  resolution: "Mapped, unresolved, duplicated, and dropped identifiers are counted"
  statistics: "Method, minimum set size, p-values, correction family, and alpha are recorded"
  narrative: "Enrichment evidence is separated from mechanism, causality, and clinical interpretation"
---

## Version Compatibility

Examples assume Python 3.11+, tab-separated gene lists, and Nextflow 24.04+. The baseline ORA uses exact finite-population arithmetic and Benjamini–Hochberg correction without requiring SciPy. The ranked route is a descriptive weighted running-sum score; it does not claim a permutation p-value. For production use, pin the exact GO, MSigDB, Reactome, KEGG, or other gene-set release and the identifier-mapping release.

# Functional enrichment

**Goal:** Convert selected or ranked genes into reproducible, statistically qualified evidence about annotation overlap and gene-set concentration.

**Principle:** enrichment is conditional on the query, eligible universe, identifier mapping, gene-set collection/release, method, and multiple-testing family. It is not a causal pathway model.

## Input contract

| Field | Required | Purpose |
|---|---:|---|
| `sample` | yes | Stable analysis key |
| `query_genes` | ORA | Selected genes, one per line |
| `ranked_genes` | ranked | Gene/score pairs ordered or sortable by the analysis design |
| `universe_genes` | ORA | Genes that could have appeared in the query |
| `gene_sets` | yes | Versioned set ID, description, and genes |
| `species` | yes | Organism context |
| `identifier_namespace` | yes | Gene symbol, Ensembl, UniProt, or another declared namespace |
| `gene_set_collection` | yes | GO, Reactome, MSigDB, custom, or other source |
| `gene_set_release` | yes | Release/date/commit or fixture identity |
| `method` | yes | `ora` or `ranked` |
| `alpha` | recommended | Predeclared interpretation threshold |

Do not infer species or identifier type from filenames. Resolve and report duplicates and unresolved IDs before testing.

## Over-representation analysis

ORA tests whether a gene set overlaps the query more than expected under a finite population. For a query of size `n`, universe of size `N`, gene set size `K`, and overlap `k`, the one-sided hypergeometric tail is evaluated under the declared universe. The expected overlap is `nK/N`.

The workbench returns overlap, set size, query size, universe size, expected overlap, p-value, Benjamini–Hochberg q-value, direction, and leading genes. It omits sets below the declared minimum size so the tested family is explicit.

A custom background is often essential. If a differential-expression list contains only genes that were detected and tested, using every annotated gene in the genome can change the sampling model and bias interpretation. The universe should represent genes that could have entered the query.

## Ranked enrichment

The baseline ranked route computes a weighted running-sum enrichment score using the absolute ranking statistic as hit weight and reports leading-edge genes. It is intentionally marked `RANKED_DESCRIPTIVE` because it does not yet estimate a null distribution or permutation p-value.

Do not translate a large running-sum score into statistical significance without a validated null model. Preserve the ranking statistic, direction convention, ties policy, gene-set release, and leading-edge members.

## Multiple testing

A gene-set analysis tests many terms. Report raw p-values and adjusted q-values, the correction method, the tested set family, the minimum size, and any filtering performed before correction. A q-value is conditional on the tested family; changing the collection or size filter changes the multiplicity problem.

Related GO terms are not independent. Parent/child redundancy can produce a list of terms that describes one underlying annotation pattern. Redundancy reduction, if added, must be a documented post-processing step and must not erase the original results.

## Identifier resolution

Track total input IDs, unique IDs, resolved IDs, unresolved IDs, duplicated IDs, and genes excluded by the universe. Silent identifier loss changes the effective query and can create misleading enrichment. The same namespace must not be assumed across count matrices, differential-expression tables, GO annotations, and pathway collections.

## From result to narrative

A defensible statement is:

> “Under the declared universe, identifier namespace, gene-set release, and multiple-testing procedure, this selected gene list overlaps the named term more often than expected.”

An indefensible shortcut is:

> “The treatment activated this pathway and caused the phenotype.”

The stronger claim requires direction and effect size, independent replication, perturbation or functional validation, cell-composition assessment, pathway topology or activity modeling, and biological context. Annotation overlap alone is not mechanism.

## Release states

| State | Meaning |
|---|---|
| `STUB` | Synthetic wiring or fixture output; no biological claim |
| `MISSING_EVIDENCE` | Universe, mapping, release, or required method input is absent |
| `REVIEW` | Statistical result exists but requires context or redundancy review |
| `READY_FOR_REVIEW` | Inputs, universe, release, method, correction, and report are auditable |
| `RANKED_DESCRIPTIVE` | Ranked score is reported without a null-model significance claim |

## Failure modes

### The background universe is all genes by default

**Trigger:** The tested list came from a filtered experiment, but the universe is the entire genome.

**Fix:** Supply all eligible/detected genes and document the selection process.

### Unresolved identifiers are ignored

**Trigger:** The input list is passed to enrichment after failed mappings are discarded.

**Fix:** Count unresolved and duplicated identifiers and report the effective query size.

### Raw p-values are treated as discoveries

**Trigger:** A long list of terms is called significant without family correction.

**Fix:** Report Benjamini–Hochberg q-values and the tested family.

### Ranked scores are called GSEA p-values

**Trigger:** A running-sum score is described as statistically significant without permutations or a null.

**Fix:** Keep `RANKED_DESCRIPTIVE` until the null model is implemented and validated.

### Enrichment is written as causal biology

**Trigger:** Annotation overlap becomes a mechanistic or clinical conclusion.

**Fix:** Separate statistical evidence from biological inference and require orthogonal evidence.

## References

- Gene Ontology Consortium guidance on input lists, custom backgrounds, and result interpretation [1].
- GSEA and MSigDB documentation on a priori gene sets, ranked analysis, and release provenance [2].
- Subramanian et al. 2005, *PNAS*, Gene Set Enrichment Analysis [3].

[1]: https://geneontology.org/docs/go-enrichment-analysis/ "Gene Ontology: GO enrichment analysis"
[2]: https://www.gsea-msigdb.org/gsea/index.jsp "GSEA and MSigDB"
[3]: https://doi.org/10.1073/pnas.0506580102 "Gene set enrichment analysis: a knowledge-based approach"

## Related Skills

differential-expression
gene-sets
statistical-testing
database-access
pathway-analysis
varcal-truthset-workbench
assembly-annotation-workbench
