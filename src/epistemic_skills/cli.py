"""
CLI interface for Epistemic Skills: Linter, Packager, and Release Manager.
"""

import argparse
import json
import sys
from pathlib import Path

from .linter import EpistemicLinter
from .packager import SkillPackager


def cmd_lint(args):
    target = Path(args.path)
    linter = EpistemicLinter(target_word_budget=args.max_words)

    if target.is_file():
        reports = [linter.lint_file(target)]
    elif target.is_dir():
        reports = linter.lint_directory(target)
    else:
        print(f"Error: Target path does not exist: {target}", file=sys.stderr)
        return 1

    if not reports:
        print(f"No SKILL.md files found in {target}")
        return 0

    all_valid = all(r.is_valid for r in reports)

    if getattr(args, "json", False):
        payload = {
            "all_valid": all_valid,
            "skill_count": len(reports),
            "total_words": sum(r.word_count for r in reports),
            "skills": [r.to_dict() for r in reports],
        }
        print(json.dumps(payload, indent=2))
        return 0 if all_valid else 1

    print(f"Linting {len(reports)} skill(s) against the 6 Authoring Laws & Epistemic Calibration Gate:\n")

    for r in reports:
        status_symbol = "PASS" if r.is_valid else "FAIL"
        print(
            f"[{status_symbol}] {r.skill_name:<24} "
            f"({r.word_count:>4} words | {r.code_line_count:>3} code lines | "
            f"Score: {r.integrity_score:>4.1f}%)"
        )

        for rule in r.rules:
            if not rule.passed:
                severity_tag = "[ERROR]" if rule.severity == "error" else "[WARN]"
                print(f"    {severity_tag} ({rule.rule_id}) {rule.name}: {rule.message}")
            elif args.verbose:
                print(f"    [OK]    ({rule.rule_id}) {rule.name}: {rule.message}")

    print("-" * 68)
    total_words = sum(r.word_count for r in reports)
    avg_score = sum(r.integrity_score for r in reports) / len(reports)
    print(f"Summary: {len(reports)} skills | {total_words} words total | Avg Integrity: {avg_score:.1f}%")

    if not all_valid:
        print("\nEpistemic validation FAILED. Fix errors above before packaging.")
        return 1

    print("\nAll skills passed epistemic validation.")
    return 0


def cmd_package(args):
    packager = SkillPackager(library_dir=args.library, output_dir=args.out)
    print(f"Building deterministic package from '{args.library}'...")

    try:
        manifest = packager.build_package(version=args.version, label=args.label)
        print(f"Archive:     {packager.output_dir / manifest['artifact_name']}")
        print(f"SHA256:      {manifest['sha256']}")
        print(f"Skills:      {manifest['skill_count']}")
        print(f"Total Words: {manifest['total_words']}")
        print(f"Manifest:    {packager.output_dir / 'manifest.json'}")
        print(f"Certificate: {packager.output_dir / 'RELEASE-CERTIFICATE.md'}")
        return 0
    except Exception as e:
        print(f"Packaging failed: {e}", file=sys.stderr)
        return 1


def cmd_list(args):
    target = Path(args.library)
    linter = EpistemicLinter()
    reports = linter.lint_directory(target)

    if not reports:
        print(f"No skills found in {target}")
        return 0

    print(f"\nEpistemic Skills Library ({len(reports)} skills in {target}):\n")
    print(f"{'Skill Name':<24} | {'Words':<6} | {'Code':<6} | {'Integrity':<9} | {'Applicability':<13} | {'Verify'}")
    print("-" * 75)
    for r in reports:
        app_str = "Yes" if r.has_applicability_section else "No"
        ver_str = "Yes" if r.has_verification_section else "No"
        print(f"{r.skill_name:<24} | {r.word_count:<6} | {r.code_line_count:<6} | {r.integrity_score:>5.1f}%   | {app_str:<13} | {ver_str}")
    print()
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="epistemic-skills",
        description="Epistemic Skills Linter, Packager, and Release Certifier for AI Agents",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    parser_lint = subparsers.add_parser("lint", help="Lint SKILL.md file(s) against the 6 Authoring Laws")
    parser_lint.add_argument("path", nargs="?", default="library/skills", help="Path to SKILL.md or directory of skills")
    parser_lint.add_argument("--max-words", type=int, default=900, help="Target maximum word count per skill (default: 900)")
    parser_lint.add_argument("-v", "--verbose", action="store_true", help="Show all passing rules in output")
    parser_lint.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")

    parser_pkg = subparsers.add_parser("package", help="Build a deterministic release zip and manifest")
    parser_pkg.add_argument("--library", default="library/skills", help="Path to skills library directory")
    parser_pkg.add_argument("--out", default="dist", help="Output directory for zip and manifest")
    parser_pkg.add_argument("--version", default="1.0.0", help="Version tag for the release artifact")
    parser_pkg.add_argument("--label", default=None, help="Optional custom label for artifact")

    parser_list = subparsers.add_parser("list", help="List all skills and their epistemic metrics")
    parser_list.add_argument("--library", default="library/skills", help="Path to skills library directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "lint":
        return cmd_lint(args)
    elif args.command == "package":
        return cmd_package(args)
    elif args.command == "list":
        return cmd_list(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
