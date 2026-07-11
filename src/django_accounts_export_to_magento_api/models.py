# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django_accounts.models import Customer
from idx_normalizator import normalize_idx, validate_idx


class CustomerInMagento(models.Model):
    customer: "Customer" = models.ForeignKey(
        "django_accounts.Customer", related_name="customer_in_magento_exporter", null=True, on_delete=models.SET_NULL
    )
    magento_url = models.CharField(max_length=255)
    data_hash = models.CharField(max_length=255)
    success = models.BooleanField(default=False)
    bulk_uuid = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        verbose_name = "Customer in Magento"
        verbose_name_plural = "Customers in Magento"


class Channel(models.Model):
    idx = models.CharField(max_length=128, blank=False, null=False, unique=True)
    label = models.CharField(max_length=128, blank=False, null=False, default="", unique=True)
    default_magento_store_id = models.CharField(max_length=128, blank=False, null=False, unique=True)
    lang_channel_to_magento_store = models.JSONField(null=True)
    objects = models.Manager()

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        self.idx = normalize_idx(self.idx)
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_idx(idx):
        return normalize_idx(idx)

    @staticmethod
    def validate_idx(idx):
        validate_idx(idx)
