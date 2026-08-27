# Contributing

Keep the statistical contract visible. Any new method should document its null model, tested family, background universe, identifier policy, minimum set size, correction method, and whether it produces inferential or descriptive output.

Run the complete suite before opening a pull request:

```bash
python3 -m py_compile enrichment/*.py scripts/*.py
python3 -m pytest -q
python3 scripts/validate_repo.py
python3 scripts/validate_manifest.py assets/test-data/enrichment.csv --check-paths
nextflow run main.nf -profile test -stub-run --outdir results/test
```

Synthetic fixtures may verify code behavior but must not be described as biological discovery, pathway activation, treatment mechanism, or clinical evidence.
