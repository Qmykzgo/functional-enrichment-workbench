nextflow.enable.dsl=2

include { RUN_ORA } from './modules/run_ora'
include { RUN_RANKED } from './modules/run_ranked'
include { COLLECT_REPORT } from './modules/collect_report'
include { WRITE_PROVENANCE } from './modules/provenance'

params.input = params.input ?: 'assets/test-data/enrichment.csv'
params.outdir = params.outdir ?: 'results/enrichment'
params.mode = params.mode ?: 'REAL'

workflow {
    if (!file(params.input).exists()) {
        error "Input manifest not found: ${params.input}"
    }
    manifest = Channel.fromPath(params.input, checkIfExists: true)
    rows = manifest.splitCsv(header: true)
    ora_inputs = rows.map { row ->
        def meta = [sample: row.sample.toString().trim(), species: row.species.toString().trim(), identifier_namespace: row.identifier_namespace.toString().trim(), gene_set_collection: row.gene_set_collection.toString().trim(), gene_set_release: row.gene_set_release.toString().trim(), method: row.method.toString().trim(), min_size: row.min_size.toString().trim() ?: '2']
        tuple(meta, file(row.query_genes.toString().trim()), file(row.universe_genes.toString().trim()), file(row.gene_sets.toString().trim()))
    }
    ranked_inputs = rows.map { row ->
        def meta = [sample: row.sample.toString().trim(), species: row.species.toString().trim(), identifier_namespace: row.identifier_namespace.toString().trim(), gene_set_collection: row.gene_set_collection.toString().trim(), gene_set_release: row.gene_set_release.toString().trim(), method: row.method.toString().trim(), min_size: row.min_size.toString().trim() ?: '2']
        tuple(meta, file(row.ranked_genes.toString().trim()), file(row.gene_sets.toString().trim()))
    }

    ora = RUN_ORA(ora_inputs)
    ranked = RUN_RANKED(ranked_inputs)
    all_reports = ora.ora.map { it[1] }.mix(ranked.ranked.map { it[1] })
    COLLECT_REPORT(all_reports.collect())
    WRITE_PROVENANCE(manifest)
}
