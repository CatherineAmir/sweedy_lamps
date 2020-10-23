# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class MRPRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    number_labours = fields.Integer(default=1, required=True, )

    labour_cost_per_hour = fields.Float(default=0)
    overhead_cost_per_hour = fields.Float(default=0)

    labour_account_id = fields.Many2one(comodel_name="account.account", required=True, )
    overhead_account_id = fields.Many2one(comodel_name="account.account", required=True, )

    labour_analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", required=True, )
    overhead_analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", required=True, )
    
    
