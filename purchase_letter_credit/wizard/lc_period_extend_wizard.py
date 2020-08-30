# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class LcPeriodExtendWizard(models.TransientModel):
    _name = 'lc.period.extend.wizard'
    _description = 'Lc Period Extend Wizard'

    def default_lc_id(self):
        active_id = self._context.get('active_id')
        return active_id

    name = fields.Text(string="Description", required=True, )
    amount = fields.Float(string="",  required=False, )
    purchase_lc_id = fields.Many2one(comodel_name="purchase.letter.credit", default= lambda self:self.default_lc_id())
    expiration_date = fields.Date(string="New Expiration Date", required=True, )

    def action_confirm(self):
        lc_amount = self.purchase_lc_id.lc_amount
        self.env['lc.period.extend'].create({
            'name': self.name,
            'amount': self.amount,
            'expiration_date': self.expiration_date,
            'purchase_lc_id': self.purchase_lc_id.id,
        })
        self.purchase_lc_id.write({
            'lc_amount': lc_amount + self.amount,
            'expiration_date': self.expiration_date,
        })
        if self.purchase_lc_id.lc_type_id.is_bank_fees_from_lc:
            self.purchase_lc_id.add_bank_fees(self.amount)
        self.purchase_lc_id.create_start_journal_entries(self.amount)
