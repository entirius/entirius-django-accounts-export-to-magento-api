# entirius-django-accounts-export-to-magento-api

A Django module that exports customer accounts from Entirius, the open-source modular ecommerce platform, to an
existing Magento 2 store over its REST API. Accounts go out in bulk requests, and the result is tracked per customer
so that a re-run sends only the accounts that were never sent.

[![PyPI](https://img.shields.io/pypi/v/entirius-django-accounts-export-to-magento-api.svg)](https://pypi.org/project/entirius-django-accounts-export-to-magento-api/)
[![Python](https://img.shields.io/pypi/pyversions/entirius-django-accounts-export-to-magento-api.svg)](https://pypi.org/project/entirius-django-accounts-export-to-magento-api/)
[![License: MPL-2.0](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://github.com/entirius/entirius-django-accounts-export-to-magento-api/blob/develop/LICENSE)

## What it does

- Exports customer accounts to Magento 2 with bulk customer requests.
- Tracks the export state of every customer, with a hash of the data that was sent.
- Skips customers that already have an export record; a force option sends all of them again.
- Maps each source channel of the accounts to a Magento store.
- Runs in the calling process or as a single-instance Celery task.

## Installation

```shell
uv add entirius-django-accounts-export-to-magento-api
pip install entirius-django-accounts-export-to-magento-api
```

```python
INSTALLED_APPS = [
    ...
    "django_accounts",
    "django_accounts_export_to_magento_api",
]
```

`django_accounts` brings its own app requirements. Required settings: `MAGENTO2_URL_FOR_CHECKOUT_EXPORT` and
`MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT`, the same pair the checkout bridges read; reference in
https://github.com/entirius/entirius-django-accounts-export-to-magento-api/blob/develop/AGENTS.md (section Settings).

## Quick start

```python
# settings.py
MAGENTO2_URL_FOR_CHECKOUT_EXPORT = "https://magento.example.com/rest/"
MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT = "<api-token>"

# a shell or a scheduled job
from django.core.management import call_command

call_command("all-accounts-export-to-magento", bulk_size=100)
```

`bulk_size` is the number of accounts per request. Every source channel of the exported accounts needs a `Channel`
of this module (Django admin) that names its Magento store; the export stops when one is missing.

## Requirements

- Python 3.11 or newer, Django 5.0 or newer.
- Celery with a configured `celery-once` backend: the task module imports it.
- `django-allauth` (any service that runs `django_accounts` has it).
- A Magento 2 store with a REST API integration token.
- Entirius packages pulled in: `entirius-django-accounts`, `entirius-py-magento2-sdk2`,
  `entirius-py-process-logger`, `entirius-py-idx-normalizator`.

## Documentation

- Module docs (log codes): https://github.com/entirius/entirius-django-accounts-export-to-magento-api/tree/develop/docs
- Entirius documentation: https://docs.entirius.com/
- Releases: https://github.com/entirius/entirius-django-accounts-export-to-magento-api/releases

## Part of Entirius

This module runs inside the Entirius backend service (Volkanos) and is one of the bridges that connect it to an
existing Magento 2 store.

- Backend service: https://github.com/entirius/entirius-service-volkanos
- Docker harness: https://github.com/entirius/entirius-zeno
- Accounts module: https://github.com/entirius/entirius-django-accounts
- Magento 2 SDK it uses: https://github.com/entirius/entirius-py-magento2-sdk2
- Sibling bridges: https://github.com/entirius/entirius-django-pim-export-to-magento-api,
  https://github.com/entirius/entirius-django-checkout-export-to-magento-api,
  https://github.com/entirius/entirius-django-checkout-import-from-magento-api

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Development and agent instructions: https://github.com/entirius/entirius-django-accounts-export-to-magento-api/blob/develop/AGENTS.md

## License

Mozilla Public License 2.0 (MPL-2.0) — see https://github.com/entirius/entirius-django-accounts-export-to-magento-api/blob/develop/LICENSE.
