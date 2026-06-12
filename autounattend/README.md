# Autounattend — Local Templates

This is the **local** autounattend directory for this consumer repo.
WinForge's reusable workflow reads templates from here (and falls back
to the winforge-vendored `base.xml` if a per-product override is missing).

## How it works

Build workflow's render step looks for templates in this order:
1. `autounattend/${PRODUCT}.xml` (e.g. `autounattend/win11-24h2.xml`)
2. `autounattend/base.xml`
3. (fallback) winforge's vendored `base.xml`

`{{PLACEHOLDER}}` tokens are rendered against GitHub Actions Secrets
**on this repo** (not on phantomic12/winforge).

## Placeholder variables

| Variable | Secret |
|---|---|
| `{{LOCAL_ADMIN_NAME}}` | `LOCAL_ADMIN_NAME` |
| `{{LOCAL_ADMIN_PASS}}` | `LOCAL_ADMIN_PASS` |
| `{{COMPUTER_NAME}}` | `COMPUTER_NAME` |
| `{{PRODUCT_KEY}}` | `PRODUCT_KEY` |

If a template contains no `{{...}}` placeholders, it's copied verbatim
(useful for product-specific tweaks that don't need secrets).

## Required secrets

Set these at **Settings → Secrets and variables → Actions** on *this* repo:

| Secret | Required? | Used for |
|---|---|---|
| `LOCAL_ADMIN_NAME` | yes* | `{{LOCAL_ADMIN_NAME}}` |
| `LOCAL_ADMIN_PASS` | yes* | `{{LOCAL_ADMIN_PASS}}` (PlainText) |
| `COMPUTER_NAME` | optional | `{{COMPUTER_NAME}}` |
| `PRODUCT_KEY` | optional | `{{PRODUCT_KEY}}` |
| `RCLONE_CONF` | yes | rclone config for Google Drive upload |
| `ACCOUNTS_YAML` | yes | account pool metadata for upload |

*Required if your template uses that placeholder.

If a template references a placeholder whose secret is unset, the build
fails with a clear error listing the missing variables.

## File naming

Place files as `autounattend/<product>.xml` where `<product>` matches
the product name in `config/products.yaml` (e.g. `win11-24h2.xml`).

## Examples

- `oobe-skip.xml` — minimal, no placeholders, just bypasses OOBE prompts.
  Use this if you don't want to bake in a local admin account.
- `base.xml` — generic OOBE-skip with `{{LOCAL_ADMIN_*}}` placeholders.
  This is the default for any product without a per-product override.
- `win11-24h2.xml` — per-product override. Useful when one product needs
  different defaults (e.g. `{{PRODUCT_KEY}}` for Windows Pro vs Enterprise).
