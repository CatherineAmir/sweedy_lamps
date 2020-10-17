# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import groupby

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

    discount_mount = fields.Float(string="Discount Amount",  required=False , compute='discount_calculation')
    direct_discount = fields.Integer(string="Direct Disc. %",  required=False , )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','direct_discount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - ((line.discount + line.direct_discount) or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def _prepare_invoice_line(self):
        invoice_line = super(discount_cycle, self)._prepare_invoice_line()
        invoice_line['discount_mount'] = self.discount_mount
        invoice_line['discount'] = self.discount + self.direct_discount
        return invoice_line

    @api.depends('product_uom_qty','discount','price_unit','direct_discount')
    def discount_calculation(self):
        for rec in self:
            if rec.discount or rec.direct_discount:
                if rec.product_uom_qty > 1:
                    rec.discount_mount = ((rec.price_unit * rec.product_uom_qty) * (rec.discount / 100))
                    if rec.direct_discount:
                        rec.discount_mount += ((rec.price_unit * rec.product_uom_qty) * (rec.direct_discount / 100))
                else:
                    rec.discount_mount = (rec.price_unit * (rec.discount / 100))
                    if rec.direct_discount:
                        rec.discount_mount += (rec.price_unit * (rec.direct_discount / 100))
            else:
                rec.discount_mount = 0.0
            pass


class discount_cycle_sale_order(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line')
    def _compute_has_discount(self):
        self.has_discount = False
        for line in self.order_line:
            if line.discount:
                self.has_discount = True
        pass

    has_discount = fields.Boolean(string="", compute='_compute_has_discount'  )
    total_discount = fields.Float(string="",  compute="tot_disc", required=False, )
    discount_role = fields.Selection(string="", selection=[('quarter', 'quarter'), ('annual', 'annual'), ], required=False, )
    before_discount = fields.Float(string="",  required=False, compute='_compute_before_discount' )

    @api.depends('order_line.price_subtotal')
    def _compute_before_discount(self):
        self.before_discount = 0
        for line in self.order_line:
            self.before_discount += line.price_subtotal + line.discount_mount
        pass

    def _prepare_invoice(self):
        invoice_line = super(discount_cycle_sale_order, self)._prepare_invoice()
        invoice_line['before_discount'] = self.before_discount
        return invoice_line

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
        ir_config = self.env['ir.config_parameter'].sudo()
        dis_limit = int(ir_config.get_param('discount_limit'))
        for rec in self.order_line:
            if dis_limit >= 0:
                if rec.direct_discount > dis_limit and not self.env.user.has_group('mf_discount_cycle.group_direct_discount') :
                    raise ValidationError(_("لا يمكنك اعطاء خصم مباشر بتلك القيمة يرجى ابلاغ المسؤل للتأكيد"))
        if self.discount_role == 'quarter':
            self.partner_id.disc_available_quar -= self.total_discount
        elif self.discount_role == 'annual':
            self.partner_id.disc_available_annu -= self.total_discount
        return res

class discount_cycle_account_total(models.Model):
    _inherit = 'account.move'

    before_discount = fields.Float(string="Before Discount", required=False, )

class discount_cycle_account_move(models.Model):
    _inherit = 'account.move.line'

    discount_mount = fields.Float(string="Discount Amount",  required=False, )
