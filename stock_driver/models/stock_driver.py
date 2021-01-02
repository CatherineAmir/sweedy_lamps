# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class StockDriver(models.Model):
    _name = 'stock.driver'
    _rec_name = 'name'
    _description = 'Stock Driver'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name", required=True, )
