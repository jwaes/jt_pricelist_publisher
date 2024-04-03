from odoo import models, fields, api


class ReportPublicationPricelist(models.AbstractModel):
    _name = 'report.jt_pricelist_publisher.publication_report_wizard'
    _description = 'Report for pricelist publication'

    def _get_report_values(self, docids, data=None):

        data_pricelist_id = data.get('pricelist_id')
        pricelist_id = data_pricelist_id and int(data_pricelist_id)
        pricelist = self.env['product.pricelist'].browse(pricelist_id).exists()
        if not pricelist:
            pricelist = self.env['product.pricelist'].search([], limit=1)

        publication = self.env['pricelist.publication'].browse(
            data.get('publication_id'))

        # self.env.context.update({
        #     'pricelist_id': pricelist_id,
        # })

        return {
            'docs': publication,
            'publication': publication,
            'pricelist': pricelist,     
            'pricelist_date': data.get('pricelist_date'),
            'quarter_number': data.get('quarter_number'),          
            'lang': data.get('lang'),
            'publication_instance_code': data.get('publication_instance_code'),
        }
