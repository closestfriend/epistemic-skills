"""
Tests for the EpistemicLinter.
"""

import pytest
from pathlib import Path
from epistemic_skills.linter import EpistemicLinter


@pytest.fixture
def linter():
    return EpistemicLinter(target_word_budget=900)


def test_lint_all_library_skills(linter):
    library_path = Path(__file__).parent.parent / "library" / "skills"
    reports = linter.lint_directory(library_path)
    assert len(reports) == 11

    for r in reports:
        assert r.is_valid, f"Skill {r.skill_name} failed validation: {r.rules}"
        assert r.word_count <= 900, f"Skill {r.skill_name} exceeds 900 words ({r.word_count})"
        assert r.integrity_score >= 60.0


def test_missing_frontmatter(linter, tmp_path):
    bad_skill = tmp_path / "SKILL.md"
    bad_skill.write_text("# Bad Skill\nNo frontmatter here.")
    report = linter.lint_file(bad_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E001" and not rule.passed for rule in report.rules)


def test_excessive_words(linter, tmp_path):
    long_skill = tmp_path / "SKILL.md"
    body = "word " * 1200
    long_skill.write_text(f"---\nname: test\ndescription: Use for tests. Not for prod.\n---\n# Test\n## Applicability\n```python\npass\n```\n## Verify\n{body}")
    report = linter.lint_file(long_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E003" and not rule.passed for rule in report.rules)


def test_missing_code_blocks(linter, tmp_path):
    no_code_skill = tmp_path / "SKILL.md"
    no_code_skill.write_text("---\nname: doc-parser\ndescription: Use for parsing. Not for edits.\n---\n# Parser\n## Applicability\nWorks on files.\n## Verify\nCheck output.")
    report = linter.lint_file(no_code_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E004" and not rule.passed for rule in report.rules)
