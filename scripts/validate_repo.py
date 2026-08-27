#!/usr/bin/env python3
"""Validate the functional-enrichment-workbench repository contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^---\s*\n(.*?)\n---\s*\n", text)
    if not match:
        raise ValueError("missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def validate_skill() -> list[str]:
    skill_dir = ROOT / "skills/functional-enrichment-workbench"
    errors: list[str] = []
    try:
        data = frontmatter(skill_dir / "SKILL.md")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"{skill_dir}/SKILL.md: {exc}"]
    for field in ("name", "description", "tool_type", "primary_tool"):
        if field not in data:
            errors.append(f"skill: missing {field}")
    if data.get("name") != skill_dir.name:
        errors.append("skill: name does not match directory")
    if "Use when" not in str(data.get("description", "")):
        errors.append("skill: description lacks Use when trigger")
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for heading in ("## Version Compatibility", "## References", "## Related Skills"):
        if heading not in text:
            errors.append(f"skill: missing {heading}")
    guide = skill_dir / "usage-guide.md"
    if not guide.exists():
        errors.append("skill: missing usage-guide.md")
    return errors


def validate_openclaw() -> list[str]:
    path = ROOT / "openclaw.plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: {exc}"]
    errors: list[str] = []
    if data.get("id") != "functional-enrichment-workbench":
        errors.append("manifest: unexpected id")
    for relative in data.get("skills", []):
        if not (ROOT / relative).is_dir():
            errors.append(f"manifest: missing skill path {relative}")
    return errors


def validate_input_manifest() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_manifest.py"), str(ROOT / "assets/test-data/enrichment.csv"), "--check-paths"],
        cwd=ROOT, capture_output=True, text=True, check=False
    )
    return [result.stderr.strip()] if result.returncode else []


def validate_fixture() -> list[str]:
    path = ROOT / "assets/test-data/genesets.tsv"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        header = lines[0].split("\t")
    except (OSError, IndexError) as exc:
        return [f"{path}: {exc}"]
    required = {"set_id", "description", "genes"}
    missing = required - set(header)
    return [f"{path}: missing columns {sorted(missing)}"] if missing else []


def main() -> int:
    errors = validate_skill() + validate_openclaw() + validate_input_manifest() + validate_fixture()
    required = [
        "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "requirements.txt", ".gitignore",
        "enrichment/__init__.py", "enrichment/core.py", "enrichment/cli.py",
        "scripts/validate_manifest.py", "scripts/validate_repo.py", "scripts/collect_report.py",
        "modules/run_ora.nf", "modules/run_ranked.nf", "modules/collect_report.nf", "modules/provenance.nf",
        "main.nf", "nextflow.config", "tests/test_enrichment.py",
        "assets/test-data/enrichment.csv", "assets/test-data/query_genes.txt", "assets/test-data/ranked_genes.tsv",
        "assets/test-data/universe_genes.txt", "assets/test-data/genesets.tsv"
    ]
    errors.extend(f"missing required file: {relative}" for relative in required if not (ROOT / relative).exists())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository is valid: skill, manifest, inputs, gene sets, algorithms, tests, and workflow modules checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
