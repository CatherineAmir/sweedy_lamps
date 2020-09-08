# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _expected_date(self):
        expected_date = self.get_expected_date()
        if expected_date:
            return expected_date
        return fields.Datetime.from_string(self.order_id.date_order) + timedelta(days=self.customer_lead or 0.0)

    def get_expected_date(self):
        self.ensure_one()
        # order_date = fields.Datetime.from_string(self.order_id.date_order if self.order_id.state in ['sale', 'done'] else fields.Datetime.now())
        # return order_date + timedelta(days=self.customer_lead or 0.0)
        order = self.order_id
        line_qty = self.product_uom_qty
        available_qty = self.product_id.with_context(to_date=order.date_order).free_qty
        if line_qty <= available_qty:
            return fields.Datetime.from_string(self.order_id.date_order)
        else:
            production_schedule = self.env['mrp.production.schedule'].search([
                ('product_id','=',self.product_id.id),
                ('warehouse_id','=',order.warehouse_id.id),
            ],limit=1)
            # forecasts = production_schedule.forecast_ids.filtered(lambda f: f.date >= order.date_order).sorted(key= lambda f: f.date)
            production_schedule_states = production_schedule.get_production_schedule_view_state()
            production_schedule_data = {}
            for d in production_schedule_states:
                if d['id'] == production_schedule.id:
                    production_schedule_data = d
                    break

            if production_schedule_data:
                forecast_ids = production_schedule_data['forecast_ids']
                for forecast in forecast_ids:
                    if order.date_order.date() <= forecast['date_start']:
                        promise_qty = forecast['starting_inventory_qty'] + forecast['replenish_qty'] - forecast['outgoing_qty']
                        # forecast_qty = forecast['safety_stock_qty']
                        if line_qty <= promise_qty:
                            return datetime.combine(forecast['date_stop'] , datetime.min.time())

    @api.onchange('product_id','product_uom_qty')
    def onchange_product_id_exp(self):
        if self.product_id:
            expected_date = self.get_expected_date()
            if not expected_date:
                return {'warning': {
                    'title': _("Warning"),
                    'message': ('Please check the qty available and manufacturing planning for product %s' % self.product_id.display_name )}}

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        for line in self.filtered("order_id.expected_date"):
            date_planned = fields.Datetime.from_string(line.order_id.expected_date)
            values.update({
                'date_planned': fields.Datetime.to_string(date_planned),
            })
        return values


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.model
    def default_get(self, fields):
        defaults = super(SaleOrder, self).default_get(fields)
        defaults['picking_policy'] = 'one'
        return defaults






