from odoo import api, fields, models
import re


class ProductTemplate(models.Model):
    _inherit = "product.template"

    internal_ref_common = fields.Char(compute='_compute_internal_ref_common', string='internal_ref_common')

    dimensions_string = fields.Char(compute='_compute_dimensions_string', string='dimensions_string')
    
    @api.depends('uom_id')
    def _compute_dimensions_string(self):
        pattern = '^.*\s([0-9x]*)$'
        for template in self:
            match = re.match(pattern, template.uom_id.name)
            if match:
                template.dimensions_string = match.group(1)
                if template.thickness:
                    template.dimensions_string += 'x' + template.thickness
                else:
                    thicknesses = template.product_variant_ids.mapped('thickness')
                    low = int(min(thicknesses))
                    high = int(max(thicknesses))
                    # for i, variant in template.product_variant_ids:
                    #     if variant.thickness:
                    #         if variant.thickness >= high:
                    #             high = variant.thickness
                    #         elif variant.thickness <= low:
                    #             low = variant.thickness
                    if low == high:
                        if low != 0.0:
                            template.dimensions_string += 'x' + str(low)
                    else:
                        template.dimensions_string += 'x(' + str(low) + '-' + str(high) + ')'
            else:
                template.dimensions_string = template.uom_id.name

    def _get_product_template_proporties(self, property_key_code):
        result = self.tmpl_all_kvs.filtered(lambda o: o.code == property_key_code)
        return result

    
    @api.depends('default_code','product_variant_ids','product_variant_ids.default_code')
    def _compute_internal_ref_common(self):
        for template in self:
            if template.product_variant_count > 1:
                codes = template.product_variant_ids.filtered(lambda r: r.default_code).mapped('default_code')
                ans=""
                if codes:
                    codes = sorted(codes)
                    first=codes[0]
                    last=codes[-1]
                    for i in range(min(len(first),len(last))):
                        if(first[i]!=last[i]):
                            template.internal_ref_common = ans.rstrip('/')
                            break
                        ans+=first[i]
                template.internal_ref_common = ans.rstrip('/')
            else:
                template.internal_ref_common = template.default_code