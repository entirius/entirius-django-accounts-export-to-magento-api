# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Smoke test: every public submodule imports cleanly under a configured Django."""

import importlib

import pytest

MODULES = [
    "django_accounts_export_to_magento_api.apps",
    "django_accounts_export_to_magento_api.settings",
    "django_accounts_export_to_magento_api.models",
    "django_accounts_export_to_magento_api.admin",
    "django_accounts_export_to_magento_api.tasks",
    "django_accounts_export_to_magento_api.domain.export_accounts",
    "django_accounts_export_to_magento_api.utils.address",
    "django_accounts_export_to_magento_api.utils.change_password",
    "django_accounts_export_to_magento_api.utils.params",
    "django_accounts_export_to_magento_api.management.commands.all-accounts-export-to-magento",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module):
    importlib.import_module(module)
