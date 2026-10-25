"""
Tests for CLI invocations.
"""

from pathlib import Path
from epistemic_skills.cli import cmd_lint, cmd_package, cmd_list
import argparse


def test_cli_lint(capsys):
    library_path = str(Path(__file__).parent.parent / "library" / "skills")
    args = argparse.Namespace(path=library_path, max_words=900, verbose=False)
    exit_code = cmd_lint(args)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "All skills passed epistemic validation" in captured.out


def test_cli_list(capsys):
    library_path = str(Path(__file__).parent.parent / "library" / "skills")
    args = argparse.Namespace(library=library_path)
    exit_code = cmd_list(args)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "docx" in captured.out
    assert "pptx" in captured.out
