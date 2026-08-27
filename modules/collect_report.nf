process COLLECT_REPORT {
    publishDir params.outdir, mode: 'copy', pattern: 'enrichment_summary.*'

    input:
    path reports

    output:
    path 'enrichment_summary.tsv', emit: summary_tsv
    path 'enrichment_summary.md', emit: summary_md

    script:
    def report_args = reports.collect { it.toString() }.join(' ')
    """
    python3 ${projectDir}/scripts/collect_report.py ${report_args} --output enrichment_summary.tsv --markdown enrichment_summary.md
    """
}
