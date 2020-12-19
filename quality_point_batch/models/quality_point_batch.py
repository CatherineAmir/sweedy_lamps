# -*- coding: utf-8 -*-
from itertools import product
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class QualityPointBatch(models.Model):
    _name = 'quality.point.batch'
    _rec_name = 'name'
    _description = 'quality point batch'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name", required=True, )

    product_category_ids = fields.Many2many(comodel_name="product.category", )
    stock_picking_type_ids = fields.Many2many(comodel_name="stock.picking.type", )

    def update_action(self):
        # products = self.env['product.product'].search([('categ_id', 'in', self.product_category_ids.ids)])
        points_list = []
        templates = self.env['product.template'].search([('categ_id', 'in', self.product_category_ids.ids)])
        quality_points = self.env['quality.point'].search([
            ('product_tmpl_id', 'in', templates.ids),
            ('picking_type_id', 'in', self.stock_picking_type_ids.ids),
        ])

        for qp in quality_points:
            points_list.append((qp.product_tmpl_id.id, qp.picking_type_id.id))

        all_qp = [k for k in product(templates.ids, self.stock_picking_type_ids.ids)]
        to_be_created = list(set(all_qp) - set(points_list))
        for qp in to_be_created:
            self.env['quality.point'].create({
                'product_tmpl_id': qp[0],
                'picking_type_id': qp[1],
            })

    def view_quality_points(self):
        quality_points = self.env['quality.point'].search([
            ('product_tmpl_id.categ_id', 'in', self.product_category_ids.ids),
            ('picking_type_id', 'in', self.stock_picking_type_ids.ids),
        ])

        domain = [('id', 'in', quality_points.ids)]
        view_tree = {
            'name': _(' Quality Points '),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'quality.point',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }

        return view_tree




