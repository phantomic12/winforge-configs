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
    """build.yml must use win-forge/winforge as a reusable workflow."""
    text = (WORKFLOWS_DIR / "build.yml").read_text()
    assert "uses: win-forge/winforge/" in text
    assert "secrets:" in text
    # Must forward at least RCLONE_CONF + ACCOUNTS_YAML (those are required
    # by winforge's reusable workflow). Local Admin + Product Key + GoFile
    # are optional and may be absent in test repos.
    assert "RCLONE_CONF:" in text
    assert "ACCOUNTS_YAML:" in text


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
