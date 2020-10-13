# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
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
                labour_costs = (duration / 60.0) * work_order.operation_id.labour_cost_per_hour
                overhead_costs = (duration / 60.0) * work_order.operation_id.overhead_cost_per_hour

                work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour + labour_costs + overhead_costs
                # work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
                # End Change

            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done, finished_move.product_id.uom_id)
                extra_cost = self.extra_cost * qty_done
                finished_move.price_unit = (sum([-m.stock_valuation_layer_ids.value for m in consumed_moves.sudo()]) + work_center_cost + extra_cost) / qty_done
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
