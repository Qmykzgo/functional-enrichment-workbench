# functional-enrichment-workbench

A reproducible workbench for turning ranked gene lists into **auditable functional-enrichment evidence** rather than an undigested list of pathway names.

## Why this project exists

Functional enrichment is often presented as the final decorative step of an RNA-seq analysis: select significant genes, submit them to a website, copy a few pathway names into a paragraph, and call the result a mechanism. That shortcut hides the decisions that determine the answer. Which genes were eligible to appear in the list? Which identifier namespace was used? Which Gene Ontology or pathway release was loaded? Were the tests corrected across all terms? Did the ranking preserve effect direction and magnitude? Are the enriched terms redundant parents of the same annotation cluster?

This repository treats enrichment as a **statistical evidence layer**. It records the tested universe, input list, gene-set release, identifier resolution, method, thresholds, multiple-testing correction, and limitations. It supports two complementary views:

| View | Question | Baseline method | What it does not prove |
|---|---|---|---|
| Over-representation analysis | Is a term represented more often in a selected list than expected under a defined universe? | Exact hypergeometric tail probability | Causality, pathway activity, or independence of related terms |
| Ranked-list enrichment | Do members of a gene set concentrate toward one end of a ranked list? | Transparent weighted running-sum score | Statistical significance without a null model or permutation scheme |
| Narrative layer | What can be said without overstating the result? | Evidence-aware Markdown report | A mechanistic explanation by itself |

The design follows the Gene Ontology guidance to use a custom reference list containing genes that could have appeared in the analysis list, and it keeps background and sample frequencies visible [1]. It also follows the GSEA principle that a priori gene sets can be evaluated across a ranked list, while preserving gene-set collection and release metadata [2].

## What the workbench demonstrates

The portfolio value is not merely that it runs a pathway command. It demonstrates statistical reasoning, data-contract design, multiple-testing control, provenance, and communication of uncertainty.

| Capability | Implementation |
|---|---|
| Explicit background universe | ORA rejects query genes absent from the declared universe |
| Exact finite-population test | Hypergeometric survival probability is computed without a black-box statistics dependency |
| Multiple testing | Benjamini–Hochberg q-values are returned in the original gene-set order |
| Ranked analysis | A deterministic weighted running-sum score reports leading-edge genes |
| Identifier accounting | Input and gene-set files retain the namespace and unresolved-ID fields in the manifest |
| Gene-set provenance | Collection, species, release, source URL, and version are manifest fields |
| Safe narrative | Reports distinguish enrichment evidence from mechanism or causality |
| Reproducibility | Nextflow DSL2, deterministic fixtures, provenance files, and GitHub Actions |

## Quick start

```bash
python3 -m py_compile enrichment/*.py scripts/*.py
python3 -m pytest -q
python3 scripts/validate_manifest.py assets/test-data/enrichment.csv --check-paths
PYTHONPATH=. python3 -m enrichment.cli \
  --gene-sets assets/test-data/genesets.tsv \
  --query assets/test-data/query_genes.txt \
  --universe assets/test-data/universe_genes.txt \
  --mode ora \
  --output /tmp/ora.tsv
PYTHONPATH=. python3 -m enrichment.cli \
  --gene-sets assets/test-data/genesets.tsv \
  --query assets/test-data/ranked_genes.tsv \
  --mode ranked \
  --output /tmp/ranked.tsv
nextflow run main.nf -profile test -stub-run --outdir results/test
```

The fixtures are deliberately small and deterministic. They validate algorithm and workflow behavior; they are not a biological finding and should not be cited as one.

## Manifest contract

Each analysis row declares the query, universe, gene-set collection, species, identifier namespace, and correction policy.

```csv
sample,query_genes,ranked_genes,universe_genes,gene_sets,species,identifier_namespace,gene_set_collection,gene_set_release,method,alpha
synthetic_tCDD,assets/test-data/query_genes.txt,assets/test-data/ranked_genes.tsv,assets/test-data/universe_genes.txt,assets/test-data/genesets.tsv,synthetic,GENE_SYMBOL,GO-like-fixture,fixture-1,ora,0.05
```

For ORA, the `universe_genes` file is not optional. For ranked analysis, `ranked_genes` contains `gene` and `score` columns separated by tabs. `query_genes` is still retained so the same manifest can support both analysis views.

## The central statistical decision: the universe

Suppose ten genes are selected from an experiment. Comparing those ten genes with every protein-coding gene in a genome can be inappropriate if many genes were never detected or tested. The relevant universe is usually the set of genes that could have entered the selected list, such as genes that passed expression and quality filters. Gene Ontology explicitly recommends adding a custom reference list for this reason [1].

A result should therefore report:

| Quantity | Interpretation |
|---|---|
| `query_size` | Number of unique genes in the selected list |
| `universe_size` | Number of unique eligible genes |
| `overlap` | Query genes annotated to the gene set |
| `expected` | Expected overlap under the universe proportion |
| `p_value` | Probability of at least the observed overlap under the hypergeometric model |
| `q_value` | Benjamini–Hochberg adjusted p-value across tested gene sets |

Changing the universe can change the enrichment result without changing the query genes. That is not a software inconsistency; it is a change in the sampling model.

## Ranked-list analysis and honest limits

The ranked route computes a weighted running-sum score using the absolute ranking statistic as hit weight. This is useful for showing whether a gene set concentrates near the top or bottom of a list and for exposing the leading-edge genes. The baseline intentionally does **not** invent a permutation p-value. Results are marked `RANKED_DESCRIPTIVE` until a validated null model, permutation strategy, and gene-correlation policy are added.

This choice is deliberate. A visually convincing running-sum curve is not automatically evidence of statistical significance. The official GSEA site describes GSEA as testing a priori defined sets across biological states and maintains versioned MSigDB collections; the collection and release are therefore part of the analysis identity [2].

## Interpreting a result without writing a false mechanism

An enriched term supports a statement such as:

> “Under the declared gene universe, identifier mapping, gene-set release, and multiple-testing procedure, genes in the selected list overlap the DNA-repair set more often than expected.”

It does not by itself support:

> “The treatment activated DNA repair and caused the phenotype.”

The stronger statement requires additional evidence: direction and magnitude of expression changes, independent replication, perturbation or functional assays, pathway topology or activity modeling, cell composition controls, and biological context. Enrichment is a structured summary of annotation overlap, not a causal experiment.

## Analysis modes

### ORA

ORA uses a one-sided hypergeometric tail probability for each gene set. It applies a minimum gene-set size, reports expected and observed overlap, and adjusts p-values across the tested sets. It does not assume that terms are independent; the report should therefore expose related terms rather than implying that each significant term is an independent discovery.

### Ranked enrichment

The ranked mode orders the supplied gene-score pairs as given, computes a weighted running sum, and reports the leading-edge genes. It is a descriptive baseline designed to make the algorithm inspectable. It should not be substituted for a fully validated GSEA implementation when statistical significance is required.

## Evidence and provenance

The workbench records the following in its manifest and provenance output:

| Provenance item | Why it matters |
|---|---|
| Species and identifier namespace | Gene symbols, Ensembl IDs, and UniProt IDs are not interchangeable without mapping |
| Gene-set collection and release | Ontology and pathway membership changes over time |
| Query and universe checksums | Reconstructs the exact gene sets used |
| Method and minimum size | Changes the tested hypothesis and multiplicity burden |
| Correction method and alpha | Determines how discoveries are called |
| Resolved/unresolved IDs | Prevents silent loss of input genes |
| Workflow mode and software versions | Separates real execution from fixtures and stub runs |

## Output layout

```text
results/<analysis>/
├── 01_inputs/
├── 02_ora/
├── 03_ranked/
├── 04_reports/
│   ├── enrichment_summary.tsv
│   └── enrichment_summary.md
└── provenance/
```

## Failure modes the repository is designed to expose

| Failure mode | Why it matters | Workbench response |
|---|---|---|
| The universe is omitted | P-values depend on the sampling frame | ORA requires an explicit universe |
| Unresolved IDs disappear silently | The effective query changes | Manifest/report retains resolution counts |
| P-values are reported without correction | Many tested terms create false positives | BH q-values are emitted |
| GO terms are treated as independent | Parent/child redundancy inflates narratives | Reports retain all tested terms and warn about redundancy |
| Ranked score is called a p-value | No null model was established | Ranked output is `RANKED_DESCRIPTIVE` |
| A term is treated as a mechanism | Annotation overlap is not causality | Narrative guardrails remain in README/report |

## Non-goals

The initial release does not download a live GO/MSigDB release, perform ID mapping against a remote service, model gene-gene correlation, infer pathway activity, run permutation-based GSEA significance, or make treatment, diagnostic, or clinical recommendations. Real analyses should supply versioned gene-set files and a validated identifier map.

## Roadmap

Future extensions may add GO DAG-aware parent/child reduction, local MSigDB/Reactome/KEGG adapters, permutation-based ranked enrichment, camera/fgsea-style correlation-aware testing, identifier-resolution reports, redundancy clustering, interactive plots, and a real TCDD dataset reproduction. Each extension should preserve database release, query/universe provenance, and an explicit statistical contract.

## References

[1]: https://geneontology.org/docs/go-enrichment-analysis/ "Gene Ontology: GO enrichment analysis"
[2]: https://www.gsea-msigdb.org/gsea/index.jsp "GSEA and MSigDB"
[3]: https://doi.org/10.1038/nmeth.2016.105 "Gene set enrichment analysis: a knowledge-based approach"
