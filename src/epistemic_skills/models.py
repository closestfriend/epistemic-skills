"""
Data models for Epistemic Skills validation and packaging.
Zero mandatory external dependencies (pure dataclasses with optional dict serialization).
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any


@dataclass
class SkillMetadata:
    name: str
    description: str
    has_positive_trigger: bool = False
    has_negative_boundary: bool = False
    raw_frontmatter: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EpistemicRuleResult:
    rule_id: str
    name: str
    passed: bool
    message: str
    severity: str = "error"  # "error" or "warning"


@dataclass
class SkillReport:
    skill_name: str
    file_path: str
    word_count: int
    line_count: int
    code_block_count: int
    code_line_count: int
    has_applicability_section: bool
    has_verification_section: bool
    rules: List[EpistemicRuleResult] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return all(r.passed for r in self.rules if r.severity == "error")

    @property
    def integrity_score(self) -> float:
        """Score from 0.0 to 100.0 based on rule passes and density."""
        if not self.rules:
            return 0.0
        passed_rules = sum(1 for r in self.rules if r.passed)
        score = (passed_rules / len(self.rules)) * 80.0
        # bonus for healthy code-to-prose density (up to 20 pts)
        if self.word_count > 0:
            code_density = min(1.0, (self.code_line_count * 8) / self.word_count)
            score += code_density * 20.0
        return round(min(100.0, score), 1)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["is_valid"] = self.is_valid
        d["integrity_score"] = self.integrity_score
        return d
