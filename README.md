# WinForge Configs — Example Consumer Repo

This is a **consumer** of [phantomic12/winforge](https://github.com/phantomic12/winforge).
It contains the build configs and the workflow that calls winforge's
reusable workflow. **You don't fork winforge itself** — you fork this
repo (or use it as a template) and customize it.

## How it works

```
┌─────────────────────────┐                  ┌──────────────────────────┐
│  winforge-configs (you) │  workflow_call   │  winforge (the tool)     │
│                         │ ────────────────▶│                          │
│  config/profiles/*.yaml │                  │  scripts/                │
│  autounattend/*.xml     │                  │  easimon/maximize-space  │
│  secrets: RCLONE_CONF,  │                  │  reusable workflow       │
│           ACCOUNTS_YAML │                  │  (the heavy lifting)     │
└─────────────────────────┘                  └──────────────────────────┘
```

1. The `.github/workflows/build.yml` workflow in *this* repo calls
   `phantomic12/winforge/.github/workflows/build.yml@v1` via `uses:`
2. WinForge's reusable workflow checks out *this* repo for `config/`
   and `autounattend/`, then checks out itself for `scripts/`
3. It builds the ISO, then uploads to Google Drive (if you've set
   `RCLONE_CONF`) and/or as a GitHub Actions artifact

## Use this template

```bash
# 1. Use this repo as a template (or fork it)
gh repo create myorg/my-winforge-configs --template phantomic12/winforge-configs

# 2. Add your secrets (RCLONE_CONF, ACCOUNTS_YAML, admin creds, product keys)
gh secret set RCLONE_CONF -R myorg/my-winforge-configs < ~/.config/rclone/rclone.conf.b64
gh secret set ACCOUNTS_YAML -R myorg/my-winforge-configs < my-accounts.yaml
# ... and the autounattend secrets (see autounattend/README.md)

# 3. Edit config/profiles/*.yaml to match your product/edition/language
$EDITOR config/profiles/win11-prod.yaml

# 4. Edit autounattend/<product>.xml — add {{LOCAL_ADMIN_NAME}},
#    {{LOCAL_ADMIN_PASS}}, {{COMPUTER_NAME}}, {{PRODUCT_KEY}} placeholders

# 5. Trigger a build
gh workflow run build.yml -R myorg/my-winforge-configs -f profile=win11-prod
```

## Required secrets

Set these on this repo at **Settings → Secrets and variables → Actions**:

| Secret | Required? | Used for |
|---|---|---|
| `RCLONE_CONF` | yes | rclone config (Google Drive accounts) |
| `ACCOUNTS_YAML` | yes | `config/accounts.yaml` content (account pool) |
| `LOCAL_ADMIN_NAME` | if your autounattend uses `{{LOCAL_ADMIN_NAME}}` |
| `LOCAL_ADMIN_PASS` | if your autounattend uses `{{LOCAL_ADMIN_PASS}}` |
| `COMPUTER_NAME` | optional | `{{COMPUTER_NAME}}` in autounattend |
| `PRODUCT_KEY` | optional | `{{PRODUCT_KEY}}` in autounattend |

## Repo layout

```
winforge-configs/
├── .github/workflows/
│   └── build.yml                # thin wrapper that calls winforge
├── config/
│   ├── accounts.yaml.example    # template for ACCOUNTS_YAML secret
│   ├── editions.yaml            # which editions exist per product
│   ├── products.yaml            # product URLs + latest UUP UUIDs
│   └── profiles/
│       ├── win11-prod.yaml      # production build (most users start here)
│       ├── win11-dev.yaml       # dev channel
│       ├── win11-ent.yaml       # enterprise edition
│       ├── win11-ltsc.yaml      # LTSC edition
│       ├── win11-min.yaml       # debloated minimum
│       └── win10-legacy.yaml    # Windows 10 22H2
└── autounattend/
    ├── base.xml                 # generic OOBE-skip template
    ├── oobe-skip.xml            # minimal — no placeholders
    ├── win11-24h2.xml           # per-product override
    ├── win11-25h2.xml
    └── README.md                # placeholder variable reference
```

## Updating winforge

WinForge is pinned to `v1` in `.github/workflows/build.yml`. To upgrade:

```yaml
uses: phantomic12/winforge/.github/workflows/build.yml@v1   # stable
uses: phantomic12/winforge/.github/workflows/build.yml@main # bleeding edge
uses: phantomic12/winforge/.github/workflows/build.yml@<sha> # exact pin
```

Renovate, Dependabot, etc. will detect new tags/releases on winforge
and open PRs on this repo.

## Triggering from external automation

```bash
# Trigger a build via repo_dispatch
gh api repos/myorg/my-winforge-configs/dispatches \
  -f event_type=build-request \
  -f client_payload[profile]=win11-prod
```

## See also

- [phantomic12/winforge](https://github.com/phantomic12/winforge) — the tool repo (no need to fork)
- [UUP-dump](https://uupdump.net) — source of the UUP files
- [UUP-dump converter](https://github.com/uup-dump/converter) — what winforge wraps
