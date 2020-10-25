# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    def _cal_price(self, consumed_moves):

        work_center_cost = 0
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                time_lines.write({'cost_already_recorded': True})
                # New Change to add additional costs
                labour_costs = (duration / 60.0) * work_order.operation_id.labour_cost_per_hour * work_order.operation_id.number_labours
                overhead_costs = (duration / 60.0) * work_order.operation_id.overhead_cost_per_hour

                work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour + labour_costs + overhead_costs
                # work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
                # End Change

            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done, finished_move.product_id.uom_id)
                extra_cost = self.extra_cost * qty_done
                finished_move.price_unit = (sum([-m.stock_valuation_layer_ids.value for m in consumed_moves.sudo()]) + work_center_cost + extra_cost) / qty_done
        return True

    def post_inventory(self):
        for order in self:
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish = moves_to_finish.with_context(mo_id=order.id)._action_done()
            order.workorder_ids.mapped('raw_workorder_line_ids').unlink()
            order.workorder_ids.mapped('finished_workorder_line_ids').unlink()
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('move_line_ids')
            for moveline in moves_to_finish.mapped('move_line_ids'):
                if moveline.move_id.has_tracking != 'none' and moveline.product_id == order.product_id or moveline.lot_id in consume_move_lines.mapped('lot_produced_ids'):
                    if any([not ml.lot_produced_ids for ml in consume_move_lines]):
                        raise UserError(_('You can not consume without telling for which lot you consumed it'))
                    # Link all movelines in the consumed with same lot_produced_ids false or the correct lot_produced_ids
                    filtered_lines = consume_move_lines.filtered(lambda ml: moveline.lot_id in ml.lot_produced_ids)
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                else:
                    # Link with everything
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})
        return True

    # def _prepare_wc_analytic_line(self, wc_line):
    #     wc = wc_line.workcenter_id
    #     hours = wc_line.duration / 60.0
    #     value = hours * wc.costs_hour
    #     account = wc.costs_hour_account_id.id
    #     return {
    #         'name': wc_line.name + ' (H)',
    #         'amount': -value,
    #         'account_id': account,
    #         'ref': wc.code,
    #         'unit_amount': hours,
    #         'company_id': self.company_id.id,
    #     }

    # def _costs_generate(self):
    #     """ Calculates total costs at the end of the production.
    #     """
    #     self.ensure_one()
    #     AccountAnalyticLine = self.env['account.analytic.line'].sudo()
    #     for wc_line in self.workorder_ids.filtered('workcenter_id.costs_hour_account_id'):
    #         vals = self._prepare_wc_analytic_line(wc_line)
    #         precision_rounding = wc_line.workcenter_id.costs_hour_account_id.currency_id.rounding
    #         if not float_is_zero(vals.get('amount', 0.0), precision_rounding=precision_rounding):
    #             # we use SUPERUSER_ID as we do not guarantee an mrp user
    #             # has access to account analytic lines but still should be
    #             # able to produce orders
    #             AccountAnalyticLine.create(vals)
