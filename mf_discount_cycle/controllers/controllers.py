# -*- coding: utf-8 -*-
from odoo import http

# class MfDiscountCycle(http.Controller):
#     @http.route('/mf_discount_cycle/mf_discount_cycle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mf_discount_cycle/mf_discount_cycle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mf_discount_cycle.listing', {
#             'root': '/mf_discount_cycle/mf_discount_cycle',
#             'objects': http.request.env['mf_discount_cycle.mf_discount_cycle'].search([]),
#         })

#     @http.route('/mf_discount_cycle/mf_discount_cycle/objects/<model("mf_discount_cycle.mf_discount_cycle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mf_discount_cycle.object', {
#             'object': obj
#         })