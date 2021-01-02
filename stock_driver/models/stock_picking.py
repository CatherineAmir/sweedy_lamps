# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one(comodel_name="stock.driver", )
    sale_person_id = fields.Many2one(related='sale_id.user_id',readonly=True)
