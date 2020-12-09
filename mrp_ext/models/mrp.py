# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    operation_type_id = fields.Many2one('stock.picking.type','Operation Type')
    location_id = fields.Many2one('stock.location','Source Location')



class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    # def action_assign(self):
    #     res = super(MrpProduction, self).action_assign()
    #     for production in self:
    #         if not self.env['stock.picking'].search([('origin', '=', production.name), ('state', '!=', 'cancel')]):
    #             picking = False
    #             for move in production.move_raw_ids:
    #                 if move.product_uom_qty > move.reserved_availability:
    #                         product_operation = production.bom_id.bom_line_ids.filtered(lambda x: (x.product_id.id == move.product_id.id ))
    #                         product_operation_id = product_operation and product_operation[0].operation_id or False
    #                         if product_operation_id and product_operation_id.operation_type_id and product_operation_id.location_id:
    #                             if not picking:
    #                                 picking = self.env['stock.picking'].create({
    #                                     'location_id': product_operation_id.location_id.id,
    #                                     'location_dest_id': product_operation_id.operation_type_id.default_location_dest_id.id,
    #                                     'picking_type_id': product_operation_id.operation_type_id.id,
    #                                     'origin': production.name,
    #                                 })
    #                             picking_move = self.env['stock.move'].create({
    #                                 'name': production.name,
    #                                 'location_id': product_operation_id.location_id.id,
    #                                 'location_dest_id': product_operation_id.operation_type_id.default_location_dest_id.id,
    #                                 'product_id': move.product_id.id,
    #                                 'product_uom': move.product_uom.id,
    #                                 'product_uom_qty': move.product_uom_qty - move.reserved_availability,
    #                                 'picking_id': picking.id,
    #                             })
    #             if picking:
    #                 picking.action_confirm()
    #                 picking.action_assign()
    #     return res

    def action_assign(self):
        res = super(MrpProduction, self).action_assign()
        for production in self:
            if not self.env['stock.picking'].search([('origin', '=', production.name), ('state', '!=', 'cancel')]):
                picking_operations = {}
                for move in production.move_raw_ids:
                    if move.product_uom_qty > move.reserved_availability:
                            product_operation = production.bom_id.bom_line_ids.filtered(lambda x: (x.product_id.id == move.product_id.id ))
                            product_operation_id = product_operation and product_operation[0].operation_id or False
                            if product_operation_id and product_operation_id.operation_type_id and product_operation_id.location_id:
                                picking = picking_operations.get(product_operation_id.operation_type_id,False)
                                if not picking:
                                    picking = self.env['stock.picking'].create({
                                        'location_id': product_operation_id.location_id.id,
                                        'location_dest_id': product_operation_id.operation_type_id.default_location_dest_id.id,
                                        'picking_type_id': product_operation_id.operation_type_id.id,
                                        'origin': production.name,
                                    })
                                    picking_operations[product_operation_id.operation_type_id] = picking

                                picking_move = self.env['stock.move'].create({
                                    'name': production.name,
                                    'location_id': product_operation_id.location_id.id,
                                    'location_dest_id': product_operation_id.operation_type_id.default_location_dest_id.id,
                                    'product_id': move.product_id.id,
                                    'product_uom': move.product_uom.id,
                                    'product_uom_qty': move.product_uom_qty - move.reserved_availability,
                                    'picking_id': picking.id,
                                })
                if picking_operations:
                    pickings = picking_operations.values()
                    for picking in pickings:
                        picking.action_confirm()
                        picking.action_assign()
        return res

    def check_reserved_qty(self):
        for move in self.move_raw_ids:
            if float_compare( move.quantity_done, move.reserved_availability, precision_rounding=move.product_uom.rounding) != 0:
                raise ValidationError(_('Some raw materials is not reserved. \n please complete stock transfers to complete the supply of materials. \n after that make check availability'))

    def button_mark_done(self):
        for rec in self:
            rec.check_reserved_qty()
        return super(MrpProduction,self).button_mark_done()