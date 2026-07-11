# Django Accounts Export to Magento API

Customer accounts export from
[entirius-django-accounts](https://github.com/entirius/entirius-django-accounts) to Magento via the
Magento REST API. Celery-driven bulk export with per-customer status tracking.

## Installation

```shell
pip install entirius-django-accounts-export-to-magento-api
```

Add the app to your project:

```python
INSTALLED_APPS = [
    ...
    "django_accounts_export_to_magento_api",
]
```

Requires `django_accounts` in `INSTALLED_APPS` and the settings
`MAGENTO2_URL_FOR_CHECKOUT_EXPORT` + `MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT`.

## Usage

```bash
python manage.py all-accounts-export-to-magento [--force_all_accounts] [--bulk_size N] [--celery]
```

Log codes reference: [docs/log_codes.md](docs/log_codes.md).

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Architecture and settings reference: [AGENTS.md](AGENTS.md).

## License

Mozilla Public License 2.0 — see [LICENSE](LICENSE).
