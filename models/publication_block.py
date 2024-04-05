# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import xml_translate, TRANSLATED_ATTRS
from odoo.tools import safe_eval
import datetime
import re


XML_ID_PREFIX = 'pricelist_publisher.block'

class PricelistPublicationBlock(models.Model):
    _name = 'pricelist.publication.block'
    _description = 'Pricelist Publication Block'

    sequence = fields.Integer(string="Sequence", help="Define the display order")
    name = fields.Char('Name', required=True, translate=True)
    block_type = fields.Selection([
        ('html', 'html'),
        ('pdf', 'pdf'),
        ('template', 'model template'),
        ('template_dimension', 'model template - dimensioned'),
        ('view', 'simple template')
    ], string='Type', default='html')

    html_content = fields.Html(string='content', translate=True)

    # template_arch = fields.Text('template_arch', translate=xml_translate)

    view_id = fields.Many2one('ir.ui.view', string='View', ondelete="cascade", copy=False)
    model_id = fields.Many2one(
        "ir.model", string="Model", ondelete="cascade", help="Model passed on to the template"
    )
    model_name = fields.Char(related="model_id.model", string="Model Name", readonly=True, inverse="_inverse_model_name")    
    filter_domain = fields.Char(string='Apply on', help="If present, this condition must be satisfied before executing the action rule.")

    dimension_attribute_id = fields.Many2one('product.attribute', string='Dimension Attribute')

    @api.onchange('block_type')
    def _onchange_block_type(self):
        for rec in self:
            if rec.block_type == 'template_dimension':
                rec.model_id = self.env['ir.model']._get('product.template')

    def _inverse_model_name(self):
        for rec in self:
            rec.model_id = self.env["ir.model"]._get(rec.model_name)

    def _render_template(self, lang=None):
        if not lang:
            lang = self.env.context.get('lang')
        html = self.env['ir.qweb']._render(self.view_id.id, self._collect_vals(), lang=lang)
        return html

    def _collect_vals(self):

        pricelist = None
        ctx_pricelist_id = self.env.context.get('pricelist_id')
        if ctx_pricelist_id:
            pricelist_id = ctx_pricelist_id and int(ctx_pricelist_id)
            pricelist = self.env['product.pricelist'].browse(pricelist_id).exists()
        if not pricelist:
            pricelist = self.env['product.pricelist'].search([], limit=1)

        pricelist_date = None
        ctx_pricelist_date = self.env.context.get('pricelist_date')
        if ctx_pricelist_date:
            pricelist_date =   fields.Date.from_string(ctx_pricelist_date)
       
        quarter_number = None
        ctx_quarter_number = self.env.context.get('quarter_number')
        if ctx_quarter_number:
            quarter_number = ctx_quarter_number and int(ctx_quarter_number)

        publication = None
        ctx_publication_id = self.env.context.get('publication_id')
        if ctx_publication_id:
            publication_id = ctx_publication_id and int(ctx_publication_id)
            publication = self.env['pricelist.publication'].browse(publication_id).exists()

        company = None
        ctx_company_id = self.env.context.get('company_id')
        if ctx_company_id:
            company_id = ctx_company_id and int(ctx_company_id)
            company = self.env['res.company'].browse(company_id).exists()
        if not company:
            company = self.env.company

        records = None

        self_sudo = self.sudo()
        if self.filter_domain:
            domain = safe_eval.safe_eval(self_sudo.filter_domain, self._get_eval_context())
            records = self.env[self.model_name].search(domain)       


        vals = {
            'records': records,
            'pricelist': pricelist,
            'publication': publication,
            'quarter_number': quarter_number,
            'pricelist_date': pricelist_date,
            'company': company,
        }

        if self.block_type == 'template_dimension':
            dimensioned_products = []
            for template in records:
                if self.dimension_attribute_id not in template.attribute_line_ids.attribute_id:
                    raise UserError(_("Product template '%s' does not have the required product attribute: %s", template.name, self.dimension_attribute_id.name))

                attribute_values = template.product_variant_ids.mapped('product_template_attribute_value_ids').filtered(lambda r: r.attribute_id == self.dimension_attribute_id)
                dim = attribute_values.mapped(lambda r: (r.ptav_product_variant_ids, int(r.name.split("x")[0]), int(re.sub("[^0-9]","",r.name.split("x")[1]))))
                # dim2 = sorted(dim, key=lambda r: (r[1], r[2]))                
                dxs = sorted(set(map(lambda x: x[1], dim)))
                dys = sorted(set(map(lambda x: x[2], dim)))
                
                matrix = [[None]*len(dys)]*len(dxs)

                rows = []
                for dx in dxs:
                    cols = []
                    for dy in dys:
                        found = [item for item in dim if item[1] == dx and item[2] == dy]
                        if found:
                            cols.append(found[0][0][0])
                        else:
                            cols.append(None)
                    rows.append(cols)
                dimensioned_products.append((template, dxs, dys, rows))
            vals['dimensioned_products'] = dimensioned_products
                

        return vals


    def _get_eval_context(self):
        """ Prepare the context used when evaluating python code
            :returns: dict -- evaluation context given to safe_eval
        """
        return {
            'datetime': safe_eval.datetime,
            'dateutil': safe_eval.dateutil,
            'time': safe_eval.time,
            'uid': self.env.uid,
            'user': self.env.user,
        }        

    def _ensure_view(self):
        if self.block_type in ['template','template_dimension','view'] and not self.view_id:

            view_vals = {
            'name': '%s (%s)' % (self._description, self.name),
            'type': 'qweb',
            'priority': 32,
            'xml_id': '%s_%s' % (XML_ID_PREFIX ,self.id),
            'mode': 'primary',
            'arch_db': """
<span>%s</span>
            """ % (self.name)            
            }
            view = self.env['ir.ui.view'].create(view_vals)
            self.view_id = view            


    def write(self, vals):
        res = super(PricelistPublicationBlock, self).write(vals)
        self._ensure_view()
        return res

    @api.model_create_multi
    def create(self, vals):
        block = super(PricelistPublicationBlock, self).create(vals)
        block._ensure_view()
        return block