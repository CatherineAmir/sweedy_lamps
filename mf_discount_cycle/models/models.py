# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


class discount_cycle(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id','discount','price_subtotal')
    def subtotal_comparison(self):
        for rec in self:
            if rec.price_subtotal:
                if rec.product_uom_qty > 1:
                    if rec.price_subtotal < rec.product_id.standard_price * rec.product_uom_qty:
                        raise ValidationError(_("سعر البيع لايمكن ان يكن اقل من التكلفة"))
                else:
                    if rec.price_subtotal < rec.product_id.standard_price:
                        raise ValidationError(_("سعر البيع لايمكن ان يكن اقل من التكلفة"))
                    pass

    discount_mount = fields.Float(string="",  required=False , compute='discount_calculation')


    @api.depends('product_uom_qty','discount','price_unit')
    def discount_calculation(self):
        for rec in self:
            if rec.discount:
                if rec.product_uom_qty > 1:
                    rec.discount_mount = ((rec.price_unit * rec.product_uom_qty) * (rec.discount / 100))
                else:
                    rec.discount_mount = (rec.price_unit * (rec.discount / 100))
            else:
                rec.discount_mount = 0.0
            pass


class discount_cycle_sale_order(models.Model):
    _inherit = 'sale.order'


    total_discount = fields.Float(string="",  compute="tot_disc", required=False, )
    discount_role = fields.Selection(string="", selection=[('quarter', 'quarter'), ('annual', 'annual'), ], required=False, )

    @api.model
    @api.depends('order_line','partner_id')
    def tot_disc(self):
        for rec in self:
            rec.total_discount = sum(rec.order_line.mapped('discount_mount'))
        pass

    @api.onchange('total_discount','order_line','partner_id','discount_role')
    def check_disconut(self):
        for rec in self:
            if rec.discount_role:
                if rec.discount_role == 'quarter':
                    if rec.total_discount > rec.partner_id.disc_available_quar:
                        raise ValidationError(_("الخصم اكبر من المتاح للعميل"))
                elif rec.discount_role == 'annual':
                    if rec.total_discount > rec.partner_id.disc_available_annu:
                        raise ValidationError(_("الخصم اكبر من المتاح للعميل"))



    def action_confirm(self):
        res = super(discount_cycle_sale_order, self).action_confirm()
        # for rec in self:
        if self.discount_role:
            if self.discount_role == 'quarter':
                self.partner_id.disc_available_quar -= self.total_discount
            elif self.discount_role == 'annual':
                print('im hereeeeeeeeee')
                self.partner_id.disc_available_annu -= self.total_discount
        return res
