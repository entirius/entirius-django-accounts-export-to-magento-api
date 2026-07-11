# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from celery import shared_task
from celery_once import QueueOnce
from process_logger import ProcessLogger

from .domain.export_accounts import AccountsToMagentoExporter


@shared_task(base=QueueOnce, queue="accounts_pull")
def export_accounts_to_magento(runned_at: str, force_all_accounts: bool = False, bulk_size: int = 200):
    logger = ProcessLogger("EXPORT_ACCOUNTS_TO_MAGENTO")
    logger.add_log_param("runned_at", runned_at)
    logger.add_log_param("force_all_accounts", force_all_accounts)
    logger.add_log_param("bulk_size", bulk_size)

    try:
        magento_exporter = AccountsToMagentoExporter()
        magento_exporter.set_logger(logger)
        customers = magento_exporter.get_and_save_customers(force_all_accounts=force_all_accounts, bulk_size=bulk_size)
    except Exception as e:
        logger.set_code(4001)
        logger.exception(e)
