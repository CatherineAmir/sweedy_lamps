# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_limit = fields.Integer(string="Discount Limit %", required=False, )

    @api.model
    def get_values(self):
        res = super(ResConfig, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            discount_limit=int(params.get_param('discount_limit',
                                               )),
        )
        return res

    def set_values(self):
        super(ResConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "discount_limit",
            self.discount_limit)