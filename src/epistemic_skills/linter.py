"""
Epistemic Linter: Formal enforcement of the 6 Authoring Laws and Track 2
Epistemic Ledger calibration rules (Boundary-Timidity Guard & Anti-Disclaimer Gate).
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import SkillMetadata, SkillReport, EpistemicRuleResult


class EpistemicLinter:
    """
    Validates skills against empirical laws of causal agent lift and epistemic calibration.
    """

    WORD_BUDGET_TARGET = 900
    WORD_BUDGET_HARD_CAP = 1100
    BOUNDARY_TIMIDITY_MAX_RATIO = 0.25

    BANNED_DISCLAIMERS = (
        "may not always work",
        "might not work",
        "use with caution",
        "results may vary",
        "not guaranteed to work",
    )

    CONDUCT_SKILLS = {"task-discipline", "scope-safety"}

    def __init__(self, target_word_budget: int = 900):
        self.target_word_budget = target_word_budget

    def parse_frontmatter(self, content: str) -> Tuple[Optional[SkillMetadata], str]:
        """
        Parses YAML frontmatter (including multi-line block scalars) without requiring PyYAML.
        """
        if not content.startswith("---"):
            return None, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content

        raw_yaml = parts[1].strip()
        body = parts[2].strip()

        meta_dict: Dict[str, str] = {}
        try:
            import yaml
            loaded = yaml.safe_load(raw_yaml) or {}
            if isinstance(loaded, dict):
                meta_dict = {str(k): str(v) for k, v in loaded.items() if v is not None}
        except Exception:
            current_key: Optional[str] = None
            for line in raw_yaml.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if not line.startswith((" ", "\t")) and ":" in line:
                    k, v = line.split(":", 1)
                    current_key = k.strip()
                    v_clean = v.strip().strip('"').strip("'")
                    meta_dict[current_key] = "" if v_clean in ("|", ">", "|-", ">-") else v_clean
                elif current_key:
                    meta_dict[current_key] = (meta_dict[current_key] + " " + stripped).strip()

        name = meta_dict.get("name", "").strip()
        desc = meta_dict.get("description", "").strip()
        desc_lower = desc.lower()

        has_positive = any(
            trigger in desc_lower
            for trigger in ["use for", "use when", "read this first", "use whenever", "relevant when"]
        )
        has_negative = any(
            neg in desc_lower
            for neg in ["not for", "not needed for", "not applicable", "never use", "do not use", "don't use"]
        ) or (name in self.CONDUCT_SKILLS and "conflicts with the task" in body.lower())

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
        if metadata and metadata.name:
            skill_name = metadata.name

        words = len(content.split())
        lines = len(content.splitlines())

        code_blocks = re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", content, re.DOTALL)
        code_line_count = sum(len(b.splitlines()) for b in code_blocks)

        app_match = re.search(
            r"^##\s+Applicability[^\n]*\n(.*?)(?=^##\s+|\Z)",
            body,
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        has_applicability = app_match is not None
        has_verification = bool(
            re.search(
                r"^##\s+(Verify|Output\s+contract|Verification|Step\s+\d+\s+[—-]\s+prove|One-way\s+doors:\s+verify|Report\s+what\s+actually\s+happened)",
                body,
                re.MULTILINE | re.IGNORECASE,
            )
        )

        rules: List[EpistemicRuleResult] = []

        # Rule E001: Frontmatter presence and schema
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

        # Rule E002: Frontmatter Dual-Trigger (Positive + Negative boundaries)
        if metadata:
            if metadata.has_positive_trigger and metadata.has_negative_boundary:
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E002",
                        name="trigger_surface_boundaries",
                        passed=True,
                        message="Description specifies both positive trigger and negative/override boundary",
                    )
                )
            else:
                missing = []
                if not metadata.has_positive_trigger:
                    missing.append("positive trigger ('Use for...' / 'Use when...')")
                if not metadata.has_negative_boundary:
                    missing.append("negative boundary ('Not for...' / 'Do not use...')")
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E002",
                        name="trigger_surface_boundaries",
                        passed=False,
                        message=f"Weak trigger surface. Missing: {', '.join(missing)}",
                        severity="warning",
                    )
                )

        # Rule E003: Word Budget
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

        # Rule E004: Executable Snippets vs Prose Hints
        is_conduct_skill = skill_name in self.CONDUCT_SKILLS
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

        # Rule E005: Applicability & Operational Fallback Boundary + Track 2 Calibration Gate
        if has_applicability:
            app_text = app_match.group(1) if app_match else ""
            body_words = max(1, len(body.split()))
            app_words = len(app_text.split())
            unquoted_app = re.sub(r'["“”\'].*?["“”\']|`.*?`', "", app_text.lower())
            found_disclaimer = next((d for d in self.BANNED_DISCLAIMERS if d in unquoted_app), None)

            if found_disclaimer:
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E005",
                        name="applicability_fallback_boundary",
                        passed=False,
                        message=f"Banned vague disclaimer '{found_disclaimer}' in Applicability; use observable condition + fallback",
                        severity="error",
                    )
                )
            elif body_words > 100 and (app_words / body_words) > self.BOUNDARY_TIMIDITY_MAX_RATIO:
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E005",
                        name="applicability_fallback_boundary",
                        passed=False,
                        message=f"Boundary-timidity violation: Applicability is {app_words}/{body_words} words ({app_words/body_words:.0%} > 25%)",
                        severity="error",
                    )
                )
            else:
                rules.append(
                    EpistemicRuleResult(
                        rule_id="E005",
                        name="applicability_fallback_boundary",
                        passed=True,
                        message="Explicit operational applicability and fallback path declared",
                    )
                )
        elif is_conduct_skill:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E005",
                    name="applicability_fallback_boundary",
                    passed=True,
                    message="Conduct skill boundary declared",
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

        # Rule E006: Output Verification Step
        if has_verification:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E006",
                    name="verification_enforcement",
                    passed=True,
                    message="Explicit verification steps / output contract present",
                )
            )
        else:
            rules.append(
                EpistemicRuleResult(
                    rule_id="E006",
                    name="verification_enforcement",
                    passed=False,
                    message="Missing explicit output verification section before declaring completion",
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
