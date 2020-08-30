# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    purchase_lc_id = fields.Many2one(comodel_name="purchase.letter.credit",domain=[('state','=','open')])

    @api.onchange('purchase_lc_id')
    def onchange_purchase_lc_id(self):
        if self.purchase_lc_id:
            self.update({
                'partner_id': self.purchase_lc_id.vendor_id.id,
                'journal_id': self.purchase_lc_id.lc_type_id.lc_journal_id.id,
                'amount': self.purchase_lc_id.lc_remaining_amount,
                'currency_id': self.purchase_lc_id.currency_id.id,
            })

    def post(self):
        res = super(AccountPayment,self).post()
        if self.purchase_lc_id:
            move_lines = self.move_line_ids
            account_moves = move_lines.mapped('move_id')
            account_moves.write({'purchase_lc_id': self.purchase_lc_id.id})
        return res
