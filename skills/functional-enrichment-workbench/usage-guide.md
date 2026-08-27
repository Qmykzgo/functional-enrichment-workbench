## Overview

This skill turns selected or ranked genes into auditable enrichment evidence. It is designed for differential-expression follow-up, pathway review, and method teaching.

## Prerequisites

- A query gene list or ranked gene-score table.
- For ORA, an explicit universe of eligible genes.
- A versioned gene-set collection with species and identifier namespace.
- A declared method, minimum set size, correction method, and alpha.

## Quick Start

```bash
python3 -m enrichment.cli \
  --gene-sets assets/test-data/genesets.tsv \
  --query assets/test-data/query_genes.txt \
  --universe assets/test-data/universe_genes.txt \
  --mode ora --output /tmp/ora.tsv
```

## Example Prompts

> "Run ORA using the genes detected in the experiment as the universe and report the BH q-values."

> "Which genes form the leading edge of the top ranked enrichment result?"

> "How would the result change if the universe were every annotated gene rather than every tested gene?"

> "Write a cautious paragraph that distinguishes enrichment evidence from pathway activation or causality."

## What the Agent Will Do

The agent will check identifiers, query/universe compatibility, gene-set release, minimum sizes, and correction settings. It will preserve raw and adjusted statistics, expose unresolved IDs, and label the ranked baseline as descriptive until a validated null model is supplied.

## Tips

Do not omit the universe for ORA. Do not report raw p-values without the tested family and correction method. Do not describe a large ranked running-sum score as a significant GSEA result unless an appropriate null model and permutation policy were run. Overlapping GO terms may describe one annotation pattern rather than independent mechanisms.

## Related Skills

differential-expression
gene-sets
statistical-testing
database-access
pathway-analysis
varcal-truthset-workbench
assembly-annotation-workbench
