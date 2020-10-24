# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    # def _get_operation_line(self, routing, qty, level):
    #     operations = []
    #     total = 0.0
    #     for operation in routing.operation_ids:
    #         operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
    #         duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
    #         # New Change to add additional costs
    #         labour_costs = (duration_expected / 60.0) * operation.labour_cost_per_hour * operation.number_labours
    #         overhead_costs = (duration_expected / 60.0) * operation.overhead_cost_per_hour
    #
    #         total += (duration_expected / 60.0) * operation.workcenter_id.costs_hour + labour_costs + overhead_costs
    #         # total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
    #         # End Change
    #         operations.append({
    #             'level': level or 0,
    #             'operation': operation,
    #             'name': operation.name + ' - ' + operation.workcenter_id.name,
    #             'duration_expected': duration_expected,
    #             'total': self.env.company.currency_id.round(total),
    #         })
    #     return operations

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id)
        # Display bom components for current selected product variant
        if product_id:
            product = self.env['product.product'].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if product:
            attachments = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
            ('res_id', '=', product.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', product.product_tmpl_id.id)])
        else:
            product = bom.product_tmpl_id
            attachments = self.env['mrp.document'].search([('res_model', '=', 'product.template'), ('res_id', '=', product.id)])
        operations = []
        overhead_operations = []
        labour_operations = []
        if bom.product_qty > 0:
            operations = self._get_operation_line(bom.routing_id, float_round(bom_quantity / bom.product_qty, precision_rounding=1, rounding_method='UP'), 0)
            labour_operations = self._get_labour_operation_line(bom.routing_id, float_round(bom_quantity / bom.product_qty, precision_rounding=1, rounding_method='UP'), 0)
            overhead_operations = self._get_overhead_operation_line(bom.routing_id, float_round(bom_quantity / bom.product_qty, precision_rounding=1, rounding_method='UP'), 0)
        company = bom.company_id or self.env.company
        labour_cost = sum([op['total'] for op in labour_operations])
        overhead_cost = sum([op['total'] for op in overhead_operations])
        lines = {
            'bom': bom,
            'bom_qty': bom_quantity,
            'bom_prod_name': product.display_name,
            'currency': company.currency_id,
            'product': product,
            'code': bom and bom.display_name or '',
            'price': product.uom_id._compute_price(product.with_context(force_company=company.id).standard_price, bom.product_uom_id) * bom_quantity,
            'total': sum([op['total'] for op in operations]),
            'level': level or 0,
            'operations': operations,
            'labour_operations': labour_operations,
            'overhead_operations': overhead_operations,
            'operations_cost': sum([op['total'] for op in operations]),
            'labour_cost': labour_cost,
            'overhead_cost': overhead_cost,
            'attachments': attachments,
            'operations_time': sum([op['duration_expected'] for op in operations])
        }
        components, total = self._get_bom_lines(bom, bom_quantity, product, line_id, level)
        lines['components'] = components
        lines['total'] += total + labour_cost + overhead_cost
        return lines

    def _get_operation_line(self, routing, qty, level):
        operations = []
        total = 0.0
        for operation in routing.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
            total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + operation.workcenter_id.name,
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return operations

    def _get_labour_operation_line(self, routing, qty, level):
        labour_operations = []
        total = 0.0
        for operation in routing.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
            total = ((duration_expected / 60.0) * operation.labour_cost_per_hour * operation.number_labours )
            labour_operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + ' Labours Cost ',
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return labour_operations

    def _get_overhead_operation_line(self, routing, qty, level):
        overhead_operations = []
        total = 0.0
        for operation in routing.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
            total = ((duration_expected / 60.0) * operation.overhead_cost_per_hour)
            overhead_operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + ' Overhead Cost ',
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return overhead_operations

    def _get_price(self, bom, factor, product):
        price = 0
        if bom.routing_id:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in operations])

            labour_operations = self._get_labour_operation_line(bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in labour_operations])

            overhead_operations = self._get_overhead_operation_line(bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in overhead_operations])


        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * factor, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor
                company = bom.company_id or self.env.company
                not_rounded_price = line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).standard_price, line.product_uom_id) * prod_qty
                price += company.currency_id.round(not_rounded_price)
        return price

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id.id, line_qty=line_qty, line_id=line_id, level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:
                lines.append({
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code'],
                    'child_bom': bom_line['child_bom'],
                    'prod_id': bom_line['prod_id']
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    lines += (get_sub_lines(line.child_bom_id, line.product_id, bom_line['prod_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })

            if data['labour_operations']:
                lines.append({
                    'name': _('Labour Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['labour_operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })

            if data['overhead_operations']:
                lines.append({
                    'name': _('Labour Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['overhead_operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })

        bom = self.env['mrp.bom'].browse(bom_id)
        product = product_id or bom.product_id or bom.product_tmpl_id.product_variant_id
        data = self._get_bom(bom_id=bom_id, product_id=product.id, line_qty=qty)
        pdf_lines = get_sub_lines(bom, product, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data

    @api.model
    def get_labour_operations(self, bom_id=False, qty=0, level=0):
        bom = self.env['mrp.bom'].browse(bom_id)
        lines = self._get_labour_operation_line(bom.routing_id, float_round(qty / bom.product_qty, precision_rounding=1, rounding_method='UP'), level)
        values = {
            'bom_id': bom_id,
            'currency': self.env.company.currency_id,
            'operations': lines,
        }
        return self.env.ref('mrp_additional_costs.report_mrp_labour_operation_line').render({'data': values})

    @api.model
    def get_overhead_operations(self, bom_id=False, qty=0, level=0):
        bom = self.env['mrp.bom'].browse(bom_id)
        lines = self._get_overhead_operation_line(bom.routing_id, float_round(qty / bom.product_qty, precision_rounding=1, rounding_method='UP'), level)
        values = {
            'bom_id': bom_id,
            'currency': self.env.company.currency_id,
            'operations': lines,
        }
        return self.env.ref('mrp_additional_costs.report_mrp_overhead_operation_line').render({'data': values})
