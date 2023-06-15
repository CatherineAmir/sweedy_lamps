from odoo import api, fields, models

class STOCK_PICKING(models.Model):
    _inherit = 'stock.picking'

    recipient_name_id = fields.Many2one(comodel_name="reci.reci", string="Recipient Name",)
    security_id = fields.Many2one(comodel_name="sec.sec", string="Security", )
    store_keeper_id = fields.Many2one(comodel_name="store.keeper", string="Store Keepers",)

class RECIPIENT(models.Model):
    _name = 'reci.reci'
    _rec_name = 'name'

    name = fields.Char('Name')

class SECURITY_(models.Model):
    _name = 'sec.sec'
    _rec_name = 'name'

    name = fields.Char('Name')

class STORE_KEEPER(models.Model):
    _name = 'store.keeper'
    _rec_name = 'name'

    name = fields.Char('Name')
