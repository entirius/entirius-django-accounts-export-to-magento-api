# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from dataclasses import field
from enum import unique
from typing import ClassVar

import marshmallow.validate
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from marshmallow import Schema
from marshmallow_dataclass import add_schema, dataclass


@unique
class AddressType(TextChoices):
    SHIPPING = "shipping", _("Shipping address.")
    BILLING = "billing", _("Billing address.")


@add_schema
@dataclass
class IDParams:
    id: str | None = None
    Schema: ClassVar[type[Schema]] = Schema


@add_schema
@dataclass
class PatchIDParams:
    id: str
    make_default: str | None = field(metadata={"validate": marshmallow.validate.OneOf(AddressType.values)})
    Schema: ClassVar[type[Schema]] = Schema


@add_schema
@dataclass
class AddressDefaultParams:
    force_create: bool | None = None
    Schema: ClassVar[type[Schema]] = Schema
