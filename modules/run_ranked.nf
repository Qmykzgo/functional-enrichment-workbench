process RUN_RANKED {
    tag "${meta.sample}"
    publishDir "${params.outdir}/03_ranked", mode: 'copy'

    input:
    tuple val(meta), path(ranked_genes), path(gene_sets)

    output:
    tuple val(meta), path("${meta.sample}.ranked.tsv"), emit: ranked

    script:
    """
    python3 ${projectDir}/enrichment/cli.py --gene-sets ${gene_sets} --query ${ranked_genes} --mode ranked --min-size ${meta.min_size} --output ${meta.sample}.ranked.tsv
    """

    stub:
    """
    python3 ${projectDir}/enrichment/cli.py --gene-sets ${gene_sets} --query ${ranked_genes} --mode ranked --min-size ${meta.min_size} --output ${meta.sample}.ranked.tsv
    sed -i '1i# STUB: synthetic fixture only; ranked score is descriptive' ${meta.sample}.ranked.tsv
    """
}
