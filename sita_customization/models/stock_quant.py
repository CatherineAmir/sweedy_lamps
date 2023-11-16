from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit='stock.quant'
    product_name=fields.Char(related='product_id.product_tmpl_id.name',string='Name')
    default_code=fields.Char(related='product_id.default_code',string='Internal Code')
class StockValuationLayer(models.Model):
    _inherit='stock.valuation.layer'
    product_name=fields.Char(related='product_id.product_tmpl_id.name',string='Name')
    default_code=fields.Char(related='product_id.default_code',string='Internal Code')
class StockMove(models.Model):
    _inherit='stock.move'
    product_name=fields.Char(related='product_id.product_tmpl_id.name',string='Name')
    default_code=fields.Char(related='product_id.default_code',string='Internal Code')
    picking_code=fields.Selection(store=1)
    # display_name=fields.Char(store=1)
class StockMoveLine(models.Model):
    _inherit='stock.move.line'
    product_name=fields.Char(related='product_id.product_tmpl_id.name',string='Name')
    default_code=fields.Char(related='product_id.default_code',string='Internal Code')





