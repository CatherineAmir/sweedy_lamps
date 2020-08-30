# -*- coding: utf-8 -*-
# from odoo import http


# class WorkorderView(http.Controller):
#     @http.route('/workorder_view/workorder_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/workorder_view/workorder_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('workorder_view.listing', {
#             'root': '/workorder_view/workorder_view',
#             'objects': http.request.env['workorder_view.workorder_view'].search([]),
#         })

#     @http.route('/workorder_view/workorder_view/objects/<model("workorder_view.workorder_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('workorder_view.object', {
#             'object': obj
#         })
