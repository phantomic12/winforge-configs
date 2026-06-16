"""Verify autounattend XMLs carry the Win11 system-requirement bypass.

Mirrors winforge/tests/test_autounattend_bypass.py — same check applied
to the consumer config repo's templates. Both must have the LabConfig
RunSynchronousCommand block for the bypass to be the default at build time.
"""
from pathlib import Path

from lxml import etree

NS = {"u": "urn:schemas-microsoft-com:unattend",
      "wcm": "http://schemas.microsoft.com/WMIConfig/2002/State"}

REPO_ROOT = Path(__file__).resolve().parent.parent
WIN11_TEMPLATES = ["base.xml", "win11-24h2.xml", "win11-25h2.xml"]


def _all_win11_xmls() -> list[Path]:
    return [REPO_ROOT / "autounattend" / name for name in WIN11_TEMPLATES]


def _has_labconfig_keys(tree) -> bool:
    paths = tree.xpath(
        './/u:settings[@pass="windowsPE"]/'
        'u:component[@name="Microsoft-Windows-Setup"]/'
        'u:RunSynchronousCommand/u:Path/text()',
        namespaces=NS,
    )
    pstrs = [str(c) for c in paths]
    return (
        any("BypassTPMCheck" in p for p in pstrs)
        and any("BypassSecureBootCheck" in p for p in pstrs)
        and any("BypassRAMCheck" in p for p in pstrs)
    )


def test_every_win11_autounattend_has_bypass_keys():
    files = _all_win11_xmls()
    assert all(f.exists() for f in files), f"missing templates: {[f.name for f in files if not f.exists()]}"
    missing = [f.name for f in files if not _has_labconfig_keys(etree.parse(str(f)))]
    assert not missing, f"missing bypass LabConfig keys in: {missing}"


def test_bypass_orders_are_sequential():
    """The three commands should be ordered 1, 2, 3 — order matters for
    RunSynchronousCommand (sequential, not parallel)."""
    for f in _all_win11_xmls():
        tree = etree.parse(str(f))
        cmds = tree.xpath(
            './/u:settings[@pass="windowsPE"]/'
            'u:component[@name="Microsoft-Windows-Setup"]/'
            'u:RunSynchronousCommand',
            namespaces=NS,
        )
        orders = [int(c.find("u:Order", NS).text) for c in cmds]
        assert orders == sorted(orders), f"{f.name}: orders not sequential: {orders}"


def test_bypass_keys_write_to_labconfig_path():
    for f in _all_win11_xmls():
        tree = etree.parse(str(f))
        paths = tree.xpath(
            './/u:settings[@pass="windowsPE"]/'
            'u:component[@name="Microsoft-Windows-Setup"]/'
            'u:RunSynchronousCommand/u:Path/text()',
            namespaces=NS,
        )
        for p in paths:
            pstr = str(p)
            assert 'HKLM\\SYSTEM\\Setup\\LabConfig' in pstr, f"{f.name}: bad path {pstr}"
            assert pstr.startswith("reg add "), f"{f.name}: not a reg add command: {pstr}"


def test_oobe_skip_does_not_have_bypass():
    """oobe-skip.xml is a generic no-credential fallback — Win11-only bypass
    should not be in there. (It's not a Win11-specific template.)"""
    oobe_skip = REPO_ROOT / "autounattend" / "oobe-skip.xml"
    if oobe_skip.exists():
        tree = etree.parse(str(oobe_skip))
        assert not _has_labconfig_keys(tree), "oobe-skip.xml should not have bypass keys"
