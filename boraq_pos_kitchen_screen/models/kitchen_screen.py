# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import logging
import psycopg2
import time
from odoo.tools import float_is_zero
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def load_order_details(self, order_id):
        order_obj = self.browse(int(order_id))
        lines = []
        if order_obj:
            for each in order_obj.lines:
                line = self.load_order_line_details(each.id)
                if line:
                    lines.append(line[0])
        return lines

    @api.model
    def load_order_line_details(self, line_id):
        data = {}
        line_obj = self.env['pos.order.line'].search_read([('id', '=', line_id)])
        if line_obj:
            order_obj = self.browse(line_obj[0].get('order_id')[0])
            data['id'] = line_obj[0].get('id')
            data['product_id'] = line_obj[0].get('product_id')
            data['uom_id'] = self.env['product.product'].browse(line_obj[0].get('product_id')[0]).uom_id.name
            data['company_id'] = line_obj[0].get('company_id')
            data['qty'] = line_obj[0].get('qty')
            data['order_line_note'] = line_obj[0].get('order_line_note')
            data['order_id'] = line_obj[0].get('order_id')
            data['state'] = line_obj[0].get('state')
            data['pos_reference'] = order_obj.pos_reference
            data['tabel_id'] = [order_obj.table_id.id, order_obj.table_id.name] if order_obj.table_id else False
            data[
                'floor_id'] = order_obj.table_id.floor_id.name if order_obj.table_id and order_obj.table_id.floor_id else False
        return [data]

    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'note': ui_order.get('order_note') or False
        })
        return res
    
    @api.model
    def _process_order(self, order, draft, existing_order):
        submitted_references = order['data']['name']
        draft_order_id = self.search([('pos_reference', '=', submitted_references)]).id

        if draft_order_id:
            to_invoice = order['to_invoice'] if not draft else False
            order = order['data']
            existing_order = self.browse([draft_order_id])

            pos_session = self.env['pos.session'].browse(order['pos_session_id'])
            if pos_session.state == 'closing_control' or pos_session.state == 'closed':
                order['pos_session_id'] = self._get_valid_session(order).id

            if  existing_order:
                existing_order.lines.unlink()
                order['user_id'] = existing_order.user_id.id
                order['name'] = existing_order.pos_reference
                existing_order.write(self._order_fields(order))

            self._process_payment_lines(order, existing_order, pos_session, draft)

            if not draft:
                try:
                    existing_order.action_pos_order_paid()
                except psycopg2.DatabaseError:
                    # do not hide transactional errors, the order(s) won't be saved!
                    raise
                except Exception as e:
                    _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                existing_order.action_pos_order_invoice()
                existing_order.account_move.sudo().with_context(force_company=self.env.user.company_id.id).post()

            self.broadcast_order_data(True)
            return existing_order.id

        if not draft_order_id:
            res = super(PosOrder, self)._process_order(order, draft, existing_order)
            self.broadcast_order_data(True)
            return res

    def write(self, vals):
        for order in self:
            if order.name == '/':
                vals['name'] = order.config_id.sequence_id._next()
        return super(PosOrder, self).write(vals)


    @api.model
    def broadcast_order_data(self, new_order):
        notifications = []
        vals = {}
        pos_order = self.search([('lines.state', 'not in', ['cancel', 'done']),
                                 ('amount_total', '>', 0.00)])
        manager_id = self.env['res.users'].search([('kitchen_screen_user', '=', 'manager')], limit=1)
        screen_table_data = []
        for order in pos_order:
            order_line_list = []
            for line in order.lines:
                order_line = {
                    'id': line.id,
                    'name': line.product_id.display_name,
                    'qty': line.qty,
                    'table': line.order_id.table_id.name,
                    'floor': line.order_id.table_id.floor_id.name,
                    'time': self.get_session_date(line),
                    'state': line.state,
                    'note': line.order_line_note,
                    'categ_id': line.product_id.product_tmpl_id.pos_categ_id.id,
                    'order': line.order_id.id,
                    'pos_cid': line.pos_cid,
                    'user': line.create_uid.id,
                    'route_id': lambda x: line.product_id.product_tmpl_id.route_ids[0].active
                                if line.product_id.product_tmpl_id.route_ids else '',
                }
                order_line_list.append(order_line)
            order_dict = {
                'order_id': order.id,
                'order_name': order.name,
                'order_time': self.get_order_date(order),
                'table': order.table_id.name,
                'floor': order.table_id.floor_id.name,
                'customer': order.partner_id.name,
                'order_lines': order_line_list,
                'total': order.amount_total,
                'note': order.note,
                'user_id': order.user_id.id,
            }
            screen_table_data.append(order_dict)
        kitchen_group_data = {}

        sort_group = sorted(screen_table_data, key=itemgetter('user_id'))
        for key, value in itertools.groupby(sort_group, key=itemgetter('user_id')):
            if key not in kitchen_group_data:
                kitchen_group_data.update({key: [x for x in value]})
            else:
                kitchen_group_data[key] = [x for x in value]
        if kitchen_group_data:
            for user_id in kitchen_group_data:
                user = self.env['res.users'].browse(user_id)
                if user and user.cook_user_ids:
                    for cook_user_id in user.cook_user_ids:
                        if len(vals) > 0:
                            d1 = kitchen_group_data[user_id]
                            for each_order in d1:
                                vals['orders'].append(each_order)
                        else:
                            vals = {
                                "orders": kitchen_group_data[user_id],
                            }
                        if new_order:
                            vals['new_order'] = new_order
                        notifications.append(
                            ((self._cr.dbname, 'pos.order.line', cook_user_id.id), {'screen_display_data': vals}))
                if user and user.kitchen_screen_user != 'cook':
                    notifications.append(
                        ((self._cr.dbname, 'pos.order.line', manager_id.id), {'screen_display_data': vals}))
        else:
            notifications.append(
                ((self._cr.dbname, 'pos.order.line', manager_id.id), {'screen_display_data': vals}))
            cook_user_ids = self.env['res.users'].search([('kitchen_screen_user', '=', 'cook')])
            if cook_user_ids:
                for each_cook_id in cook_user_ids:
                    notifications.append(
                        ((self._cr.dbname, 'pos.order.line', each_cook_id.id), {'screen_display_data': vals}))
        if notifications:
            self.env['bus.bus'].sendmany(notifications)
        return True

    def get_session_date(self, line):
        SQL = """SELECT create_date AT TIME ZONE 'GMT' as create_date  from pos_order_line where id = %d
                   """ % (line.id)
        self._cr.execute(SQL)
        data = self._cr.dictfetchall()
        time = data[0]['create_date']
        return str(time.hour) + ':' + str(time.minute) + ':' + str(time.second)

    def get_order_date(self, order):
        SQL = """SELECT date_order AT TIME ZONE 'GMT' as date_order  from pos_order where id = %d
                       """ % (order.id)
        self._cr.execute(SQL)
        data = self._cr.dictfetchall()
        time = data[0]['date_order']
        return str(time.hour) + ':' + str(time.minute) + ':' + str(time.second)


class PosOrderLines(models.Model):
    _inherit = "pos.order.line"

    @api.model
    def update_orderline_state(self, vals):
        order_line = self.browse(vals['order_line_id'])
        res = order_line.sudo().write({
            'state': vals['state']
        })
        vals['pos_reference'] = order_line.order_id.pos_reference
        vals['pos_cid'] = order_line.pos_cid
        notifications = []
        notifications.append(
            ((self._cr.dbname, 'pos.order.line', order_line.create_uid.id), {'order_line_state': vals}))
        self.env['bus.bus'].sendmany(notifications)
        return res

    @api.model
    def update_all_orderline_state(self, vals):
        notifications = []
        if vals:
            for val in vals:
                state = False
                if val.get('route'):
                    if val.get('state') == 'waiting':
                        state = 'preparing'
                    elif val.get('state') == 'preparing':
                        state = 'delivering'
                    elif val.get('state') == 'delivering':
                        state = 'done'
                    elif val.get('state') == 'cancel':
                        state = 'cancel'
                else:
                    if val.get('state') == 'waiting':
                        state = 'delivering'
                    elif val.get('state') == 'delivering':
                        state = 'done'
                    elif val.get('state') == 'cancel':
                        state = 'cancel'
                if state:
                    order_line = self.browse(val['order_line_id'])
                    order_line.sudo().write({'state': state})
                    val['pos_reference'] = order_line.order_id.pos_reference
                    val['pos_cid'] = order_line.pos_cid
                    val['state'] = state
                    notifications.append(
                        [(self._cr.dbname, 'pos.order.line', order_line.create_uid.id), {'order_line_state': val}])
            if len(notifications) > 0:
                self.env['bus.bus'].sendmany(notifications)
        return True

    state = fields.Selection(
        selection=[("waiting", "Waiting"), ("preparing", "Preparing"), ("delivering", "Waiting/deliver"),
                   ("done", "Done"), ("cancel", "Cancel")], default="waiting")
    order_line_note = fields.Text("Order Line Notes")
    pos_cid = fields.Char("pos cid")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    send_to_kitchen = fields.Boolean(string="Send To Kitchen", default=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
