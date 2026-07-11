# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django_accounts.models import Customer
from magento2_sdk2.dto.customer import CustomerData, MainCustomerData
from magento2_sdk2.services.client import Magento2Client
from magento2_sdk2.services.worker import batch_customer_post
from process_logger import ProcessLoggerMixin
from tqdm import tqdm

from django_accounts_export_to_magento_api import settings
from django_accounts_export_to_magento_api.models import Channel as ExportChannel
from django_accounts_export_to_magento_api.models import CustomerInMagento


class AccountsToMagentoExporter(ProcessLoggerMixin):
    def get_and_save_customers(self, force_all_accounts: bool = False, bulk_size: int = 200):
        if None in [settings.MAGENTO2_URL_FOR_CHECKOUT_EXPORT, settings.MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT]:
            self.logger.set_code(4005)
            self.logger.info("MAGENTO2_URL_FOR_CHECKOUT_EXPORT or MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT is not set")
            raise Exception("MAGENTO2_URL_FOR_CHECKOUT_EXPORT or MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT is not set")

        magento_client = Magento2Client(
            base_url=settings.MAGENTO2_URL_FOR_CHECKOUT_EXPORT, access_token=settings.MAGENTO2_TOKEN_FOR_CHECKOUT_EXPORT
        )

        customers = Customer.objects.all()
        all_channels_used = customers.values_list("source_channel__idx", flat=True).distinct()
        channels = ExportChannel.objects.filter(idx__in=all_channels_used).values_list("idx", flat=True)
        leak_channels = set(all_channels_used) - set(channels)
        leak_channels = [each for each in leak_channels if each]

        if leak_channels:
            self.logger.set_code(4006)
            self.logger.info(f"Channel not found for all customers. Need to configure: {leak_channels}")
            raise Exception(f"Channel not found for all customers. Need to configure: {leak_channels}")

        if not force_all_accounts:
            customers = customers.exclude(customer_in_magento_exporter__customer__in=customers)

        if customers.count() == 0:
            self.logger.set_code(2001)
            self.logger.info("No accounts to export to magento.")
            return []

        main_customer_datas = []
        already_done = 0

        for idx, customer in enumerate(tqdm(customers, total=customers.count())):
            try:
                source_channel = customer.source_channel.idx if customer.source_channel else None
                store_id = None
                if source_channel:
                    channel = ExportChannel.objects.filter(idx=source_channel).first()
                    if not channel:
                        self.logger.set_code(4002)
                        self.logger.info(f"Channel {source_channel} not found.")
                        continue

                    if customer.language:
                        store_id = channel.lang_channel_to_magento_store.get(
                            customer.language.iso2, channel.default_magento_store_id
                        )
                additional_data = {}
                if store_id:
                    additional_data["store_id"] = store_id

                main_customer_datas.append(
                    MainCustomerData(
                        customer=CustomerData(
                            email=customer.user.email,
                            firstname=customer.user.first_name
                            if customer.user.first_name
                            else customer.user.email.split("@")[0],
                            lastname=customer.user.last_name
                            if customer.user.last_name
                            else customer.user.email.split("@")[0],
                            addresses=[],
                            **additional_data,
                        )
                    )
                )

                if len(main_customer_datas) >= bulk_size or idx == customers.count() - 1:
                    response, request = batch_customer_post(magento_client, main_customer_datas)
                    request_items = response.get("request_items", [])
                    success = True
                    if not request_items:
                        success = False
                        self.logger.set_code(4002)
                        self.logger.info("Magento return empty response. Accounts not created.")
                    if response.get("errors", True):
                        success = False

                    customer_in_magento = []
                    for idx, each in enumerate(response.get("request_items", [])):
                        customer_in_magento.append(
                            CustomerInMagento(
                                customer=customers[already_done + each.get("id")],
                                magento_url=request.url,
                                data_hash=each.get("data_hash", None),
                                success=success,
                                bulk_uuid=response.get("bulk_uuid", None),
                            )
                        )
                    already_done += len(customer_in_magento) if customer_in_magento else len(main_customer_datas)
                    try:
                        self.logger.set_db_operation("CREATE", "django_accounts", "CustomerInMagento")
                        CustomerInMagento.objects.bulk_create(customer_in_magento)
                        self.logger.set_code(2002)
                        self.logger.info("CustomerInMagento created with success.")
                    except Exception as ex:
                        self.logger.set_code(4003)
                        self.logger.exception(ex)
                        main_customer_datas = []
                        continue
                    main_customer_datas = []

            except Exception as ex:
                self.logger.set_code(4004)
                self.logger.exception(ex)
                main_customer_datas = []
                continue
