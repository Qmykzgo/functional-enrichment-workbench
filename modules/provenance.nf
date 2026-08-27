process WRITE_PROVENANCE {
    publishDir params.outdir, mode: 'copy', pattern: 'provenance/*'

    input:
    path manifest

    output:
    path 'provenance'

    script:
    """
    mkdir -p provenance
    cp ${manifest} provenance/enrichment.csv
    cat > provenance/run_context.tsv <<'EOF'
field	value
workflow	functional-enrichment-workbench
mode	${params.mode}
nextflow_version	${workflow.nextflow.version}
ora_model	exact hypergeometric over-representation with explicit universe
multiple_testing	Benjamini-Hochberg q-values across tested gene sets
ranked_model	weighted running-sum descriptive score; no permutation p-value
provenance	gene-set collection, release, species, namespace, inputs, and thresholds are required
narrative_guardrail	enrichment is annotation-overlap evidence, not mechanism or causality
stub_guardrail	STUB fixtures make no biological claim
EOF
    """
}
