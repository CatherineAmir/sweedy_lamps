# -*- coding: utf-8 -*-
from odoo import models, fields


class MrpBomInherit(models.Model):
    _inherit = 'mrp.bom'

    product_cost = fields.Float(related='product_tmpl_id.standard_price')
