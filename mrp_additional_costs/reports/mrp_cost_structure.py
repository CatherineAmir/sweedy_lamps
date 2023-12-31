# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class MrpCostStructure(models.AbstractModel):
    _inherit = 'report.mrp_account_enterprise.mrp_cost_structure'

    def get_lines(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0

            #get the cost of operations
            operations = []
            labour_operations = []
            overhead_operations = []
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                query_str = """SELECT w.operation_id, op.name, partner.name, sum(t.duration), wc.costs_hour
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder w ON (w.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id )
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (w.operation_id = op.id)
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY w.operation_id, op.name, partner.name, t.user_id, wc.costs_hour
                                ORDER BY op.name, partner.name
                            """
                self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
                for op_id, op_name, user, duration, cost_hour in self.env.cr.fetchall():
                    operations.append([user, op_id, op_name, duration / 60.0, cost_hour])

                query_str = """SELECT w.operation_id, op.name, partner.name, sum(t.duration), op.time_cycle_manual , op.labour_cost_per_hour, op.overhead_cost_per_hour, op.number_labours
                                , op.labour_cost_by, op.overhead_cost_by, op.labour_cost_by_unit, op.overhead_cost_by_unit
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder w ON (w.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id )
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (w.operation_id = op.id)
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY w.operation_id, op.name, partner.name, t.user_id, op.time_cycle_manual, op.labour_cost_per_hour, op.overhead_cost_per_hour, op.number_labours
                                , op.labour_cost_by, op.overhead_cost_by, op.labour_cost_by_unit, op.overhead_cost_by_unit
                                ORDER BY op.name, partner.name
                            """
                self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
                for op_id, op_name, user, duration, time_cycle_manual, labour_cost_per_hour, overhead_cost_per_hour,number_labours , labour_cost_by, overhead_cost_by, labour_cost_by_unit, overhead_cost_by_unit in self.env.cr.fetchall():
                    labour_operations.append([user, op_id, op_name, duration / 60.0,time_cycle_manual/60.0 or 0, labour_cost_per_hour or 0 ,number_labours, labour_cost_by, labour_cost_by_unit or 0 ])
                    overhead_operations.append([user, op_id, op_name, duration / 60.0,time_cycle_manual/60.0 or 0, overhead_cost_per_hour or 0, overhead_cost_by, overhead_cost_by_unit or 0])

            #get the cost of raw material effectively used
            raw_material_moves = []
            query_str = """SELECT sm.product_id, sm.bom_line_id, abs(SUM(svl.quantity)), abs(SUM(svl.value))
                             FROM stock_move AS sm
                       INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                            WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                         GROUP BY sm.bom_line_id, sm.product_id"""
            self.env.cr.execute(query_str, (tuple(mos.ids), ))
            for product_id, bom_line_id, qty, cost in self.env.cr.fetchall():
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                    'bom_line_id': bom_line_id
                })
                total_cost += cost

            #get the cost of scrapped materials
            scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])
            uom = mos and mos[0].product_uom_id
            mo_qty = 0
            if not all(m.product_uom_id.id == uom.id for m in mos):
                uom = product.uom_id
                for m in mos:
                    qty = sum(m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped('product_qty'))
                    if m.product_uom_id.id == uom.id:
                        mo_qty += qty
                    else:
                        mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            else:
                for m in mos:
                    mo_qty += sum(m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped('product_qty'))
            for m in mos:
                byproduct_moves = m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id != product)
            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'labour_operations': labour_operations,
                'overhead_operations': overhead_operations,
                'currency': self.env.company.currency_id,
                'raw_material_moves': raw_material_moves,
                'total_cost': total_cost,
                'scraps': scraps,
                'mocount': len(mos),
                'byproduct_moves': byproduct_moves
            })
        return res

