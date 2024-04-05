from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils
import re
from odoo.tools.misc import get_lang


class PricelistPublishingWizard(models.TransientModel):
    _name = 'pricelist.publishing.wizard'
    _description = 'Pricelist Publishing Wizard'

    @api.model
    def _selection_languages(self):
        return self.env['res.lang'].get_installed()


    lang = fields.Selection(_selection_languages,
        string="Lang",
        default=lambda self: self._default_language(),
    )

    which_quarter = fields.Selection([
        ('previous', 'Previous quarter'),
        ('this', 'This quarter'),
        ('next', 'Next quarter'),
    ], string='For Quarter', default='this')

    pricelist_id = fields.Many2one('product.pricelist', required=True, string='Pricelist')
    publication_id = fields.Many2one('pricelist.publication', required=True, string='Publication')

    publication_instance_code = fields.Char(compute='_compute_publication_instance_code', string='publication_instance_code')

    pricelist_date = fields.Date(compute='_compute_pricelist_date', string='Pricelist Date')

    quarter_number = fields.Integer(compute='_compute_quarter_number', string='Quarter Number')
    
    @api.depends('pricelist_date')
    def _compute_quarter_number(self):
        for rec in self:
            rec.quarter_number = date_utils.get_quarter_number(rec.pricelist_date)
    
    @api.depends('which_quarter')
    def _compute_pricelist_date(self):
        today = fields.Datetime.now()
        for rec in self:
            if rec.which_quarter == 'this':
                rec.pricelist_date = today
            elif rec.which_quarter == 'previous':
                rec.pricelist_date = date_utils.subtract(today, months=3)
            elif rec.which_quarter == 'next':
                rec.pricelist_date = date_utils.add(today, months=3)       


    @api.depends('publication_id', 'pricelist_id', 'lang', 'write_date')
    def _compute_publication_instance_code(self):
        for rec in self:            
            rec.publication_instance_code = 'P%s/L%s/%s/%sQ%s/%s' % (rec.publication_id.id, rec.pricelist_id.id, rec.lang[:2].upper(), rec.pricelist_date.year, rec.quarter_number, rec.write_date.strftime('%Y%m%d%H%M'))
            # rec.publication_instance_code = 'blah'

    def _default_language(self):
        return get_lang(self.env).code
    
    def action_print_report(self):
        data = {
            'publication_id': self.publication_id.id,
            'pricelist_id': self.pricelist_id.id,
            'pricelist_date': self.pricelist_date,
            'quarter_number': self.quarter_number,
            'publication_instance_code': self.publication_instance_code,
            'lang': self.lang,
        }
        return self.env.ref('jt_pricelist_publisher.action_report_pricelist_publication_wizard').with_context(publication_id=self.publication_id.id).report_action(self.id, data=data)        
    