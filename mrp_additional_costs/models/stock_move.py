# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        if self._context.get('mo_id'):
            operation_costs = 0
            mo = self.env['mrp.production'].browse( self._context.get('mo_id') )
            new_debit_value = self.product_id.standard_price
            debit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'debit': new_debit_value if new_debit_value > 0 else 0,
                'credit': -new_debit_value if new_debit_value < 0 else 0,
                'account_id': debit_account_id,
            }
            rslt = {'debit_line_vals': debit_line_vals}
            count = 1
            for work_order in mo.workorder_ids:
                time_lines = work_order.time_ids.filtered(lambda x: x.date_end and x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                labour_costs = (duration / 60.0) * work_order.operation_id.labour_cost_per_hour * work_order.operation_id.number_labours
                labour_costs = round(labour_costs , self.company_id.currency_id.decimal_places )
                overhead_costs = (duration / 60.0) * work_order.operation_id.overhead_cost_per_hour
                overhead_costs = round( overhead_costs, self.company_id.currency_id.decimal_places )
                rslt['labour_line_vals-' + str(count)] = {
                    'name': mo.name + '-' + work_order.operation_id.name + '- labour',
                    'ref': description,
                    'partner_id': partner_id,
                    'credit': labour_costs if labour_costs > 0 else 0,
                    'debit': -labour_costs if labour_costs < 0 else 0,
                    'account_id': work_order.operation_id.labour_account_id.id,
                    'analytic_account_id':  work_order.operation_id.labour_analytic_account_id.id,
                }
                rslt['overhead_line_vals-' + str(count)] = {
                    'name': mo.name + '-' + work_order.operation_id.name + '- overhead',
                    'ref': description,
                    'partner_id': partner_id,
                    'credit': overhead_costs if overhead_costs > 0 else 0,
                    'debit': -overhead_costs if overhead_costs < 0 else 0,
                    'account_id': work_order.operation_id.overhead_account_id.id,
                    'analytic_account_id': work_order.operation_id.overhead_analytic_account_id.id,
                }

                operation_costs += labour_costs + overhead_costs
                count += 1

            new_credit_value = credit_value - operation_costs
            credit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': new_credit_value if new_credit_value > 0 else 0,
                'debit': -new_credit_value if new_credit_value < 0 else 0,
                'account_id': credit_account_id,
            }

            rslt['credit_line_vals'] = credit_line_vals

            # if credit_value != debit_value:
            if credit_value != new_debit_value:
                # for supplier returns of product in average costing method, in anglo saxon mode
                diff_amount = debit_value - credit_value
                diff_amount = new_debit_value - credit_value
                price_diff_account = self.product_id.property_account_creditor_price_difference

                if not price_diff_account:
                    price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
                if not price_diff_account:
                    raise UserError(_(
                        'Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

                rslt['price_diff_line_vals'] = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': description,
                    'partner_id': partner_id,
                    'credit': diff_amount > 0 and diff_amount or 0,
                    'debit': diff_amount < 0 and -diff_amount or 0,
                    'account_id': price_diff_account.id,
                }
            return rslt
        else:
            return super(StockMove,self)._generate_valuation_lines_data( partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)