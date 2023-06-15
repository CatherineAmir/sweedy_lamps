# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import fields, models


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"

    account_ids = fields.Many2many('account.account', string='Accounts')

    def _print_report(self, data):
        res = super(AccountReportGeneralLedger, self)._print_report(data)
        data['form'].update(self.read(['account_ids'])[0])
        return res
