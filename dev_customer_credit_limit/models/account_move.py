# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        domain="[('partner_state','=','financial_approval'),'|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string='Partner', change_default=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', domain="[('partner_state','=','financial_approval')]")