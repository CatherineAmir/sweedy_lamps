# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_bom_price(self, bom, boms_to_recompute=False):
        self.ensure_one()
        if not bom:
            return 0
        if not boms_to_recompute:
            boms_to_recompute = []
        total = 0
        for opt in bom.routing_id.operation_ids:
            duration_expected = (
                opt.workcenter_id.time_start +
                opt.workcenter_id.time_stop +
                opt.time_cycle)
            # New Change to add additional costs
            labour_costs = 0
            overhead_costs = 0
            if opt.labour_cost_by == 'time':
                labour_costs = (duration_expected / 60.0) * opt.labour_cost_per_hour * opt.number_labours
            elif opt.labour_cost_by == 'qty':
                labour_costs = 1 * opt.labour_cost_by_unit * opt.number_labours

            if opt.overhead_cost_by == 'time':
                overhead_costs = (duration_expected / 60.0) * opt.overhead_cost_per_hour
            elif opt.overhead_cost_by == 'qty':
                overhead_costs = 1 * opt.overhead_cost_by_unit

            total += (duration_expected / 60) * opt.workcenter_id.costs_hour + labour_costs + overhead_costs
            # total += (duration_expected / 60) * opt.workcenter_id.costs_hour
            # End Change
        for line in bom.bom_line_ids:
            if line._skip_bom_line(self):
                continue

            # Compute recursive if line has `child_line_ids`
            if line.child_bom_id and line.child_bom_id in boms_to_recompute:
                child_total = line.product_id._compute_bom_price(line.child_bom_id, boms_to_recompute=boms_to_recompute)
                total += line.product_id.uom_id._compute_price(child_total, line.product_uom_id) * line.product_qty
            else:
                total += line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * line.product_qty
        return bom.product_uom_id._compute_price(total / bom.product_qty, self.uom_id)
