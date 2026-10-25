"""
Tests for the EpistemicLinter (Track 1 Static Library + Track 2 Meta-Skill Calibration Gate).
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
        assert all(rule.passed for rule in r.rules), f"Skill {r.skill_name} had warnings: {r.rules}"
        assert r.word_count <= 900, f"Skill {r.skill_name} exceeds 900 words ({r.word_count})"
        assert r.integrity_score >= 80.0


def test_lint_track2_skill_creator(linter):
    meta_path = Path(__file__).parent.parent / "track2" / "meta" / "skill-creator" / "SKILL.md"
    report = linter.lint_file(meta_path)
    assert report.is_valid, f"Track 2 skill-creator failed validation: {report.rules}"
    assert all(rule.passed for rule in report.rules), f"Track 2 skill-creator had warnings: {report.rules}"
    assert report.word_count <= 900


def test_missing_frontmatter(linter, tmp_path):
    bad_skill = tmp_path / "SKILL.md"
    bad_skill.write_text("# Bad Skill\nNo frontmatter here.")
    report = linter.lint_file(bad_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E001" and not rule.passed for rule in report.rules)


def test_excessive_words(linter, tmp_path):
    long_skill = tmp_path / "SKILL.md"
    body = "word " * 1200
    long_skill.write_text(
        f"---\nname: test\ndescription: Use for tests. Not for prod.\n---\n# Test\n## Applicability & fallback\nWorks here.\n```python\npass\n```\n## Verify\n{body}"
    )
    report = linter.lint_file(long_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E003" and not rule.passed for rule in report.rules)


def test_missing_code_blocks(linter, tmp_path):
    no_code_skill = tmp_path / "SKILL.md"
    no_code_skill.write_text(
        "---\nname: doc-parser\ndescription: Use for parsing. Not for edits.\n---\n# Parser\n## Applicability & fallback\nWorks on files.\n## Verify\nCheck output."
    )
    report = linter.lint_file(no_code_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E004" and not rule.passed for rule in report.rules)


def test_banned_vague_disclaimer_in_applicability(linter, tmp_path):
    disclaimer_skill = tmp_path / "SKILL.md"
    disclaimer_skill.write_text(
        "---\nname: pdf-tool\ndescription: Use for PDFs. Not for Word.\n---\n# PDF\n## Applicability & fallback\nThis approach may not always work on complex files.\n## Steps\n```python\npass\n```\n## Verify\n1. Check output."
    )
    report = linter.lint_file(disclaimer_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E005" and not rule.passed for rule in report.rules)


def test_boundary_timidity_guard(linter, tmp_path):
    timid_skill = tmp_path / "SKILL.md"
    bloat_boundary = "boundary condition fallback words " * 25
    main_body = "step " * 30
    timid_skill.write_text(
        f"---\nname: timid\ndescription: Use for x. Not for y.\n---\n# Timid\n## Applicability & fallback\n{bloat_boundary}\n## Steps\n{main_body}\n```python\npass\n```\n## Verify\n1. Assert ok."
    )
    report = linter.lint_file(timid_skill)
    assert not report.is_valid
    assert any(rule.rule_id == "E005" and not rule.passed for rule in report.rules)
