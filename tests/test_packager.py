"""
Tests for SkillPackager: verifies deterministic builds and checksum stability.
"""

from pathlib import Path
from epistemic_skills.packager import SkillPackager


def test_deterministic_packaging(tmp_path):
    library_path = Path(__file__).parent.parent / "library" / "skills"
    out_dir1 = tmp_path / "dist1"
    out_dir2 = tmp_path / "dist2"

    p1 = SkillPackager(library_dir=library_path, output_dir=out_dir1)
    m1 = p1.build_package(version="1.0.0")

    p2 = SkillPackager(library_dir=library_path, output_dir=out_dir2)
    m2 = p2.build_package(version="1.0.0")

    # Hashes MUST be bitwise identical for reproducible builds
    assert m1["sha256"] == m2["sha256"]
    assert m1["skill_count"] == 11
    assert (out_dir1 / "skills-v1.0.0.zip").exists()
    assert (out_dir1 / "manifest.json").exists()
    assert (out_dir1 / "RELEASE-CERTIFICATE.md").exists()
