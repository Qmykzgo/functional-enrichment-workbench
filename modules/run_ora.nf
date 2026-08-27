process RUN_ORA {
    tag "${meta.sample}"
    publishDir "${params.outdir}/02_ora", mode: 'copy'

    input:
    tuple val(meta), path(query_genes), path(universe_genes), path(gene_sets)

    output:
    tuple val(meta), path("${meta.sample}.ora.tsv"), emit: ora

    script:
    """
    python3 ${projectDir}/enrichment/cli.py --gene-sets ${gene_sets} --query ${query_genes} --universe ${universe_genes} --mode ora --min-size ${meta.min_size} --output ${meta.sample}.ora.tsv
    """

    stub:
    """
    python3 ${projectDir}/enrichment/cli.py --gene-sets ${gene_sets} --query ${query_genes} --universe ${universe_genes} --mode ora --min-size ${meta.min_size} --output ${meta.sample}.ora.tsv
    sed -i '1i# STUB: synthetic fixture only; no biological inference' ${meta.sample}.ora.tsv
    """
}
