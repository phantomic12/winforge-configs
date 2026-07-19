"""Tests for the winforge-configs consumer workflows.

These verify the config repo's plumbing is wired correctly: it must call
winforge as a reusable workflow, and it must react to product-updated
dispatches by triggering builds for the affected profiles.
"""
from pathlib import Path
import yaml
import json

REPO_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


def test_build_workflow_calls_winforge_reusable():
    """build.yml and build-all.yml must use win-forge/winforge as a reusable workflow."""
    for wf in ["build.yml", "build-all.yml"]:
        text = (WORKFLOWS_DIR / wf).read_text()
        assert "uses: win-forge/winforge/" in text, f"{wf} missing winforge reusable call"
        assert "secrets:" in text, f"{wf} missing secrets forwarding"
        # Must forward at least RCLONE_CONF + ACCOUNTS_YAML (those are required
        # by winforge's reusable workflow). Local Admin + Product Key + GoFile
        # are optional and may be absent in test repos.
        assert "RCLONE_CONF:" in text, f"{wf} missing RCLONE_CONF"
        assert "ACCOUNTS_YAML:" in text, f"{wf} missing ACCOUNTS_YAML"


def test_build_all_has_matrix():
    """build-all.yml must use a matrix strategy with all six profiles."""
    data = yaml.safe_load((WORKFLOWS_DIR / "build-all.yml").read_text())
    jobs = data.get("jobs", {})
    build_job = jobs.get("build", {})
    strategy = build_job.get("strategy", {})
    matrix = strategy.get("matrix", {})
    profiles = matrix.get("profile", [])
    expected = {"win11-prod", "win11-ent", "win11-ltsc", "win11-min", "win10-legacy", "win10-ltsc"}
    assert set(profiles) == expected, f"build-all matrix missing profiles: {expected - set(profiles)}"
    assert strategy.get("fail-fast") == False, "build-all should set fail-fast: false"


def test_on_product_updated_resolves_profiles():
    """on-product-updated.yml must match dispatch payload against config/profiles/."""
    data = yaml.safe_load((WORKFLOWS_DIR / "on-product-updated.yml").read_text())
    triggers = data.get(True) or data.get("on") or {}
    # Must trigger on repository_dispatch with type product-updated
    rd = triggers.get("repository_dispatch", {})
    types = rd.get("types", [])
    assert "product-updated" in types
    # The resolve step must read config/profiles
    text = json.dumps(data)
    assert "config/profiles" in text
    assert "build-request" in text  # triggers build-request dispatches
