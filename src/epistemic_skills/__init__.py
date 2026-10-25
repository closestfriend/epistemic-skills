"""
Epistemic Skills: Deterministic Skill Compiler & Linter for AI Agents
Derived from empirical lift research in BenchFlow / Agent Skill Lift (Kaggle 2026).
"""

__version__ = "1.0.0"
__author__ = "Hunter Noah Karman"

from .linter import EpistemicLinter
from .packager import SkillPackager
from .models import SkillMetadata, SkillReport, EpistemicRuleResult

__all__ = [
    "EpistemicLinter",
    "SkillPackager",
    "SkillMetadata",
    "SkillReport",
    "EpistemicRuleResult",
    "__version__",
]
