from odoo import api, fields, models
from odoo.tools import date_utils
from datetime import datetime
from pytz import timezone, UTC
from odoo.exceptions import ValidationError
import math


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    description = fields.Html('Description', default='', translate=True, help="This description gets printed on the pricelist publications")

    description_internal = fields.Text('Description internal', help="This is for internal use only, describe for who this pricelist is intended, what discounts can be applied")


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    daterange_type = fields.Selection([
        ('default', 'Default'),
        ('quarter', 'Quarter'),
    ], string='Daterange type', default="default")

    def _get_default_q_year(self):
        value = fields.Datetime.now().year
        return int(value)

    def _get_default_q(self):
        value = fields.Datetime.now().month / 3
        value = math.ceil(value)
        return int(value)

    daterange_q = fields.Integer(string='Q', default=_get_default_q)
    daterange_q_year = fields.Integer('YYYY', default=_get_default_q_year)

    quarter = fields.Char(compute='_compute_quarter', string='Quarter')
    
    @api.depends('daterange_q', 'daterange_q_year', 'daterange_type')
    def _compute_quarter(self):
        for rec in self:
            if rec.daterange_type == 'quarter':
                rec.quarter = '%sQ%s' % (rec.daterange_q_year, rec.daterange_q)
            else:
                rec.quarter = None

    @api.constrains('daterange_q_year','daterange_q')
    def _check_value(self):
        if self.daterange_q_year > 3000 or self.daterange_q_year < 2000:
            raise ValidationError(_('Enter a valid year'))
        if self.daterange_q > 4 or self.daterange_q < 1:
            raise ValidationError(_('Enter a valid quarter'))            

    @api.onchange('daterange_q')
    def _onchange_daterange_q(self):
        self._calculate_daterange()


    @api.onchange('daterange_q_year')
    def _onchange_daterange_q_year(self):
        if self.daterange_q_year:
            self._calculate_daterange()

    @api.onchange('daterange_type')
    def _onchange_daterange_type(self):
        if self.daterange_type == 'quarter':
            self._calculate_daterange()            

    def _calculate_daterange(self):
        self._check_value()
        if self.daterange_type == 'quarter':        
            month = ((self.daterange_q - 1) * 3) + 1
            tz = timezone(self.env.user.tz or 'UTC')
            starter_date = datetime(year=self.daterange_q_year, month=month, day=1, hour=0, minute=0, second=0)
            ending_date = date_utils.end_of(starter_date, "quarter").replace(hour=23, minute=59, second=59)

            starter_date_utc = tz.localize(starter_date).astimezone(UTC)
            ending_date_utc = tz.localize(ending_date).astimezone(UTC)

            self.date_end = ending_date_utc.replace(tzinfo=None)
            self.date_start = starter_date_utc.replace(tzinfo=None)
        else:
            self.daterange_q = self._get_default_q()
            self.daterange_q_year = self._get_default_q_year()
