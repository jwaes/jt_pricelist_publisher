# -*- coding: utf-8 -*-
# from odoo import http


# class JtPricelistPublisher(http.Controller):
#     @http.route('/jt_pricelist_publisher/jt_pricelist_publisher', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jt_pricelist_publisher/jt_pricelist_publisher/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jt_pricelist_publisher.listing', {
#             'root': '/jt_pricelist_publisher/jt_pricelist_publisher',
#             'objects': http.request.env['jt_pricelist_publisher.jt_pricelist_publisher'].search([]),
#         })

#     @http.route('/jt_pricelist_publisher/jt_pricelist_publisher/objects/<model("jt_pricelist_publisher.jt_pricelist_publisher"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jt_pricelist_publisher.object', {
#             'object': obj
#         })
