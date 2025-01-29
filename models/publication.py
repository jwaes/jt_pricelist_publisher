# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PricelistPublication(models.Model):
    _name = 'pricelist.publication'
    _description = 'Pricelist Publication'

    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Char('Description')
    sequence = fields.Integer(string="Sequence", help="Define the display order")
    
    section_ids = fields.One2many('pricelist.publication.section', 'publication_id', string='Sections')

    pdf_background = fields.Binary("Background")
    pdf_background_pages =  fields.Char("Background page numbers")

    # def copy_data(self, default=None):
    #     if default is None:
    #         default = {}
    #     if 'name' not in default:
    #         default['name'] = _("(copy of) %s", self.name)
    #     if 'section_ids' not in default:
    #         default['section_ids'] = [(0, 0, section.copy_data()[0]) for section in self.section_ids]
    #     return super(PricelistPublication, self).copy_data(default)


    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        if 'name' not in default:
            for pub, vals in zip(self, vals_list):
                vals['name'] = _("(copy of) %s", pub.name)
        if 'section_ids' not in default:
            for pub, vals in zip(self, vals_list):
                vals['section_ids'] = [(0, 0, section_vals) for section_vals in pub.section_ids.copy_data()]                
        return vals_list

class PricelistPublicationSection(models.Model):
    _name = 'pricelist.publication.section'
    _description = 'Pricelist Publication Section'
    _order = 'sequence asc, id desc'

    sequence = fields.Integer(string="Sequence", help="Define the display order", default=10)
    publication_id = fields.Many2one('pricelist.publication', string='Publication')
    block_id = fields.Many2one('pricelist.publication.block', string='Block')
    name = fields.Char('name', related="block_id.name")
    
    