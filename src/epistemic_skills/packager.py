"""
Deterministic packager and release certifier for Epistemic Skills.
Produces bitwise-reproducible zip archives and JSON manifests.
"""

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from .linter import EpistemicLinter
from .models import SkillReport


class SkillPackager:
    """
    Builds verified, reproducible release artifacts.
    """

    def __init__(self, library_dir: str | Path, output_dir: str | Path = "dist"):
        self.library_dir = Path(library_dir)
        self.output_dir = Path(output_dir)
        self.linter = EpistemicLinter()

    def build_package(
        self,
        version: str = "1.0.0",
        label: Optional[str] = None,
        author: str = "Hunter Noah Karman",
    ) -> Dict[str, Any]:
        """
        Lints all skills, stages files cleanly, and builds a deterministic zip.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        reports = self.linter.lint_directory(self.library_dir)

        # Fail if any critical errors
        failed_reports = [r for r in reports if not r.is_valid]
        if failed_reports:
            error_details = "\n".join(
                f"- {r.skill_name}: " + ", ".join(rule.message for rule in r.rules if not rule.passed and rule.severity == 'error')
                for r in failed_reports
            )
            raise ValueError(f"Packaging aborted. {len(failed_reports)} skills failed epistemic validation:\n{error_details}")

        zip_filename = f"skills-v{version}.zip" if not label else f"skills-{label}.zip"
        zip_path = self.output_dir / zip_filename

        # Write deterministic zip (fixed timestamps)
        fixed_dt = (2026, 10, 21, 0, 0, 0)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for report in sorted(reports, key=lambda x: x.skill_name):
                skill_path = Path(report.file_path)
                skill_dir = skill_path.parent
                skill_name = report.skill_name

                # Add SKILL.md
                arcname = f"skills/{skill_name}/SKILL.md"
                zinfo = zipfile.ZipInfo(arcname, fixed_dt)
                zinfo.external_attr = 0o644 << 16
                content = skill_path.read_bytes()
                zf.writestr(zinfo, content)

                # Add any auxiliary scripts/ or references/
                for subfolder in ["scripts", "references"]:
                    sub_path = skill_dir / subfolder
                    if sub_path.exists() and sub_path.is_dir():
                        for child in sorted(sub_path.rglob("*")):
                            if child.is_file() and not child.name.startswith("."):
                                rel = child.relative_to(skill_dir)
                                aux_arcname = f"skills/{skill_name}/{rel}"
                                aux_zinfo = zipfile.ZipInfo(aux_arcname, fixed_dt)
                                aux_zinfo.external_attr = 0o644 << 16
                                zf.writestr(aux_zinfo, child.read_bytes())

            # Add LICENSE
            license_text = f"""Apache License 2.0\n\nCopyright 2026 {author}\n\nLicensed under the Apache License, Version 2.0."""
            lic_info = zipfile.ZipInfo("skills/LICENSE", fixed_dt)
            lic_info.external_attr = 0o644 << 16
            zf.writestr(lic_info, license_text.encode("utf-8"))

        # Compute SHA256
        sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        total_words = sum(r.word_count for r in reports)
        avg_words = total_words // len(reports) if reports else 0

        manifest = {
            "version": version,
            "artifact_name": zip_filename,
            "sha256": sha256,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "skill_count": len(reports),
            "total_words": total_words,
            "average_words": avg_words,
            "skills": [
                {
                    "name": r.skill_name,
                    "words": r.word_count,
                    "lines": r.line_count,
                    "code_lines": r.code_line_count,
                    "integrity_score": r.integrity_score,
                }
                for r in sorted(reports, key=lambda x: x.skill_name)
            ],
        }

        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Generate Release Certificate
        cert_path = self.output_dir / "RELEASE-CERTIFICATE.md"
        self._write_release_certificate(cert_path, manifest)

        return manifest

    def _write_release_certificate(self, cert_path: Path, manifest: Dict[str, Any]):
        skills_table = "\n".join(
            f"| `{s['name']}` | {s['words']} | {s['code_lines']} | {s['integrity_score']}% |"
            for s in manifest["skills"]
        )

        cert_md = f"""# Epistemic Skills — RELEASE CERTIFICATE

**Version:** {manifest['version']}  
**Generated:** {manifest['generated_at']}  
**Artifact:** `{manifest['artifact_name']}`  
**SHA256:** `{manifest['sha256']}`  

## Library Inventory

| Skill Name | Word Count | Code Lines | Epistemic Integrity |
|:---|---:|---:|---:|
{skills_table}

**Total Skills:** {manifest['skill_count']}  
**Total Word Budget:** {manifest['total_words']} (Avg: {manifest['average_words']} words/skill)  
**License:** Apache 2.0  

## Verification Standards

Every skill in this release has passed validation against the 6 Authoring Laws:
1. Executable code snippets with recursive patterns over vague prose hints.
2. Explicit applicability conditions and operational boundaries ('Not for...').
3. Frontmatter dual-trigger surface (positive trigger + negative scope limit).
4. Strict token budget enforcement (<= 900 words body target).
5. Mandatory verification post-conditions before reporting completion.
6. Inline safety boundaries for side-effect operations.

Reproduce this build:
```bash
python3 -m epistemic_skills.cli package --library library/skills --version {manifest['version']}
```
"""
        cert_path.write_text(cert_md, encoding="utf-8")
