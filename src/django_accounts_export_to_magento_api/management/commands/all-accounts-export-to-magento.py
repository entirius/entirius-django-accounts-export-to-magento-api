# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime

from celery_once.tasks import AlreadyQueued
from django.core.management.base import BaseCommand

from ...tasks import export_accounts_to_magento


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--force_all_accounts",
            type=bool,
            help="Force push all accounts to magento (instead of excluding already pushed, marked as success in CustomerInMagento table). Default: False",
            default=False,
        )
        parser.add_argument(
            "--bulk_size",
            type=bool,
            help="Define how many accounts will be pushed in one request, Default: 200",
            default=200,
        )
        parser.add_argument(
            "--celery", type=bool, help="Set to True to run inside Celery tasks. Default: False", default=False
        )

    def handle(self, *args, **options):
        force_all_accounts = options["force_all_accounts"]
        bulk_size = options["bulk_size"]
        celery = options["celery"]

        # Datetime when process was started
        runned_at = datetime.now().isoformat()

        if celery:
            try:
                export_accounts_to_magento.delay(
                    runned_at=runned_at, force_all_accounts=force_all_accounts, bulk_size=bulk_size
                )
                self.stdout.write(
                    f"Task for [params:force_all_accounts={force_all_accounts}, bulk_size={bulk_size}] has been created "
                )
            except AlreadyQueued:
                self.stdout.write(
                    f"Task for [params:force_all_accounts={force_all_accounts}, bulk_size={bulk_size}] was already queued"
                )
        else:
            self.stdout.write(
                f"Running task [params:force_all_accounts={force_all_accounts}, bulk_size={bulk_size}] without celery"
            )
            export_accounts_to_magento(runned_at=runned_at, force_all_accounts=force_all_accounts, bulk_size=bulk_size)

        self.stdout.write(self.style.SUCCESS("DONE"))
