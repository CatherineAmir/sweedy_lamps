# -*- coding: utf-8 -*-
# from odoo import http


# class SitaCustomization(http.Controller):
#     @http.route('/sita_customization/sita_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sita_customization/sita_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sita_customization.listing', {
#             'root': '/sita_customization/sita_customization',
#             'objects': http.request.env['sita_customization.sita_customization'].search([]),
#         })

#     @http.route('/sita_customization/sita_customization/objects/<model("sita_customization.sita_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sita_customization.object', {
#             'object': obj
#         })
