# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_lc_id = fields.Many2one(comodel_name="purchase.letter.credit", string="", required=False, )

    def action_register_payment_lc(self):
        return {
            'name': _('Pay From LC'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('purchase_letter_credit.view_account_payment_invoice_form').id,
            # 'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



