import logging
from odoo import api, fields, models
from odoo.tools import date_utils
from datetime import datetime
from pytz import timezone, UTC
from odoo.exceptions import ValidationError
import math

_logger = logging.getLogger(__name__)
class Pricelist(models.Model):
    _inherit = "product.pricelist"

    description = fields.Html('Description', default='', translate=True, help="This description gets printed on the pricelist publications")

    description_internal = fields.Text('Description internal', help="This is for internal use only, describe for who this pricelist is intended, what discounts can be applied")

    def write(self, vals):
        res =  super().write(vals)
        _logger.info("writing ... ")
        _logger.info(vals)
        _logger.info("====")
        for item in self.item_ids:
            item._calculate_daterange()
        return res


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
