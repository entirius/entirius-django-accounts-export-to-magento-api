# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin

from .models import Channel, CustomerInMagento


@admin.register(CustomerInMagento)
class CustomerInMagentoAdmin(admin.ModelAdmin):
    readonly_fields = ["customer", "magento_url", "data_hash", "success", "created_at"]
    list_display = ["customer", "success", "created_at"]
    search_fields = ["customer__user__email", "data_hash", "success", "bulk_uuid"]


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ["idx", "label", "default_magento_store_id", "lang_channel_to_magento_store"]
    search_fields = ["idx", "label", "default_magento_store_id"]
    ordering = ["idx"]
