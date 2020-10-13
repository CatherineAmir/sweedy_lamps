# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_operation_line(self, routing, qty, level):
        operations = []
        total = 0.0
        for operation in routing.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
            # New Change to add additional costs
            labour_costs = (duration_expected / 60.0) * operation.labour_cost_per_hour
            overhead_costs = (duration_expected / 60.0) * operation.overhead_cost_per_hour

            total += (duration_expected / 60.0) * operation.costs_hour + labour_costs + overhead_costs
            # total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            # End Change
            operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + operation.workcenter_id.name,
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return operations
