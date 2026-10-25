"""
Epistemic Linter: Formal enforcement of the 6 Authoring Laws discovered
during the Agent Skill Lift campaign.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .models import SkillMetadata, SkillReport, EpistemicRuleResult


class EpistemicLinter:
    """
    Validates skills against empirical laws of causal agent lift.
    """

    WORD_BUDGET_TARGET = 900
    WORD_BUDGET_HARD_CAP = 1100

    def __init__(self, target_word_budget: int = 900):
        self.target_word_budget = target_word_budget

    def parse_frontmatter(self, content: str) -> Tuple[Optional[SkillMetadata], str]:
        """
        Parses YAML frontmatter without requiring PyYAML dependency.
        Falls back to PyYAML if installed.
        """
        if not content.startswith("---"):
            return None, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content

        raw_yaml = parts[1].strip()
        body = parts[2].strip()

        meta_dict = {}
        # Try PyYAML if available
        try:
            import yaml
            meta_dict = yaml.safe_load(raw_yaml) or {}
        except Exception:
            # Clean lightweight fallback parser for key: value
            for line in raw_yaml.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    meta_dict[k] = v

        name = meta_dict.get("name", "")
        desc = meta_dict.get("description", "")

        has_positive = any(
            trigger in desc.lower()
            for trigger in ["use for", "use when", "read this first", "use whenever"]
        )
        has_negative = any(
            neg in desc.lower()
            for neg in ["not for", "not needed for", "not applicable", "never use"]
        )

        metadata = SkillMetadata(
            name=name,
            description=desc,
            has_positive_trigger=has_positive,
            has_negative_boundary=has_negative,
            raw_frontmatter=meta_dict,
        )
        return metadata, body

    def lint_file(self, file_path: str | Path) -> SkillReport:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8", errors="ignore")
        skill_name = path.parent.name if path.name == "SKILL.md" else path.stem

        metadata, body = self.parse_frontmatter(content)
        words = len(content.split())
        lines = len(content.splitlines())

        # Extract code blocks
        code_blocks = re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", content, re.DOTALL)
        code_line_count = sum(len(b.splitlines()) for b in code_blocks)

        has_applicability = bool(
            re.search(r"##\s+Applicability", content, re.IGNORECASE)
        )
        has_verification = bool(
            re.search(r"##\s+(Verify|Output\s+contract|Verification)", content, re.IGNORECASE)
            or "verify" in content.lower()
        )

        rules: List[EpistemicRuleResult] = []

        # Rule 1: Frontmatter presence and schema
        if metadata and metadata.name and metadata.description:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E001",
                    name="frontmatter_schema",
                    passed=True,
                    message=f"Valid YAML frontmatter with name '{metadata.name}'",
                )
            )
        else:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E001",
                    name="frontmatter_schema",
                    passed=False,
                    message="Missing or malformed frontmatter (requires name and description)",
                    severity="error",
                )
            )

        # Rule 2: Frontmatter Dual-Trigger (Positive + Negative boundaries)
        if metadata:
            if metadata.has_positive_trigger and metadata.has_negative_boundary:
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E002",
                        name="trigger_surface_boundaries",
                        passed=True,
                        message="Description specifies both when-to-use AND negative boundary ('Not for')",
                    )
                )
            else:
                missing = []
                if not metadata.has_positive_trigger:
                    missing.append("positive trigger ('Use for...' / 'Use when...')")
                if not metadata.has_negative_boundary:
                    missing.append("negative boundary ('Not for...' / 'Not needed for...')")
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E002",
                        name="trigger_surface_boundaries",
                        passed=False,
                        message=f"Weak trigger surface. Missing: {', '.join(missing)}",
                        severity="warning",
                    )
                )

        # Rule 3: Word Budget
        if words <= self.target_word_budget:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E003",
                    name="word_budget_law",
                    passed=True,
                    message=f"Word count ({words}) within target budget (<= {self.target_word_budget})",
                )
            )
        elif words <= self.WORD_BUDGET_HARD_CAP:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E003",
                    name="word_budget_law",
                    passed=True,
                    message=f"Word count ({words}) exceeds ideal ({self.target_word_budget}) but within cap",
                    severity="warning",
                )
            )
        else:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E003",
                    name="word_budget_law",
                    passed=False,
                    message=f"Word count ({words}) exceeds hard cap ({self.WORD_BUDGET_HARD_CAP})",
                    severity="error",
                )
            )

        # Rule 4: Executable Snippets vs Prose Hints
        # Non-discipline skills should contain concrete code blocks
        is_conduct_skill = skill_name in ["task-discipline", "scope-safety"]
        if is_conduct_skill or len(code_blocks) >= 1:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E004",
                    name="executable_snippets_law",
                    passed=True,
                    message=f"Contains {len(code_blocks)} executable code blocks ({code_line_count} lines of runnable logic)",
                )
            )
        else:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E004",
                    name="executable_snippets_law",
                    passed=False,
                    message="Weak models convert executable snippets, not prose hints. No runnable code blocks found.",
                    severity="error",
                )
            )

        # Rule 5: Applicability & Fallback Boundary
        if has_applicability or is_conduct_skill:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E005",
                    name="applicability_fallback_boundary",
                    passed=True,
                    message="Explicit applicability conditions and failure fallback path declared",
                )
            )
        else:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E005",
                    name="applicability_fallback_boundary",
                    passed=False,
                    message="Missing '## Applicability & fallback' section (prevents agent regressions on edge cases)",
                    severity="error",
                )
            )

        # Rule 6: Output Verification Step
        if has_verification:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E006",
                    name="verification_enforcement",
                    passed=True,
                    message="Verification instructions / output contract present",
                )
            )
        else:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E006",
                    name="verification_enforcement",
                    passed=False,
                    message="Missing explicit output verification steps before declaring completion",
                    severity="warning",
                )
            )

        return SkillReport(
            skill_name=skill_name,
            file_path=str(path),
            word_count=words,
            line_count=lines,
            code_block_count=len(code_blocks),
            code_line_count=code_line_count,
            has_applicability_section=has_applicability,
            has_verification_section=has_verification,
            rules=rules,
        )

    def lint_directory(self, root_dir: str | Path) -> List[SkillReport]:
        root = Path(root_dir)
        reports = []
        for path in sorted(root.rglob("SKILL.md")):
            reports.append(self.lint_file(path))
        return reports
