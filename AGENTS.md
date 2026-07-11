# AGENTS.md

Customer accounts export from Django Accounts to Magento via the Magento REST API —
distribution `entirius-django-accounts-export-to-magento-api`, Django app
`django_accounts_export_to_magento_api`. Celery-driven bulk export with per-customer status tracking.

**Tech:** Python >=3.11, Django >=5.0, Celery, entirius-django-accounts, entirius-py-magento2-sdk2

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest + pytest-django) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the package / Django app_label / DB table prefix `django_accounts_export_to_magento_api` —
  it is a schema contract.
- Migrations are part of the public contract — never edit an already released migration.
- Default: do not commit — git is the user's call.

## Architecture

```
Management command all-accounts-export-to-magento (direct or --celery)
  → tasks.export_accounts_to_magento (celery, QueueOnce)
    → domain/export_accounts.py AccountsToMagentoExporter
      → django_accounts.models.Customer (source accounts)
      → magento2-sdk2 (Magento REST client, bulk customer POST)
      → models.CustomerInMagento (per-customer export state, data hash)
```

| Path | Purpose |
|------|---------|
| `models.py` | `CustomerInMagento` — export state per customer; `Channel` — Magento store mapping |
| `domain/export_accounts.py` | exporter: builds Magento payloads, bulk POST, records results |
| `tasks.py` | celery task `export_accounts_to_magento` (QueueOnce — single instance) |
| `management/commands/` | `all-accounts-export-to-magento` CLI wrapper |
| `utils/` | address mapping, password-change via allauth, request params |
| `admin.py` | read-only admin for `CustomerInMagento`, `Channel` admin |
| `settings.py` | Magento endpoint configuration |

## Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| `MAGENTO2_URL_FOR_CHECKOUT_EXPORT` | `None` | Magento REST API base URL (required; log code 4005 when missing) |
| `MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT` | `None` | Magento API token (required; log code 4005 when missing) |

Log codes reference: `docs/log_codes.md`.

## Gotchas

- `tasks.py` imports `celery_once` eagerly — the host needs `ONCE`/`CELERY_ONCE` settings even to
  import the module.
- `utils/change_password.py` imports `allauth.account` — the host must have allauth installed
  (any host running `django_accounts` already does).
- Export skips customers already marked successful in `CustomerInMagento` unless
  `--force_all_accounts` is set; payload dedup uses `data_hash`.
