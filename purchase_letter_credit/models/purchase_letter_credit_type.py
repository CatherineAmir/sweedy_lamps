# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class PurchaseLetterCreditType(models.Model):
    _name = 'purchase.letter.credit.type'
    _rec_name = 'name'
    _description = 'Purchase Letter Credit Type'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name", required=True, )
    lc_journal_id = fields.Many2one(comodel_name="account.journal", string="LC Journal", required=True, )
    lc_bank_journal_id = fields.Many2one(comodel_name="account.journal", string="LC Bank Journal", required=True, )
    bank_fees = fields.Float(string="Bank fees (%)",  required=True, )
    bank_expense_account_id = fields.Many2one(comodel_name="account.account", string="", required=True, )
    intermediate_account_id = fields.Many2one(comodel_name="account.account", string="", required=True, )
    bank_account_number = fields.Char(string="", required=True, )
    is_bank_fees_from_lc = fields.Boolean(string="Bank Fees From LC",  )
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('active', 'Active'),('archived', 'Archived'), ], required=False,default='draft' )

    def action_active(self):
        self.write({'state':'active'})

    def action_archive(self):
        self.write({'state':'archive'})

    def action_draft(self):
        self.write({'state':'draft'})

    @api.constrains('bank_fees')
    def check_bank_fees(self):
        if not (0 < self.bank_fees < 100):
            raise ValidationError(_('Bank fees is a percentage less than 100%'))

