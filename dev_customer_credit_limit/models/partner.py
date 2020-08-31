# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class res_partner(models.Model):
    _inherit= 'res.partner'
    
    check_credit = fields.Boolean('Check Credit',track_visibility='onchange')
    credit_limit_on_hold  = fields.Boolean('Credit limit on hold',track_visibility='onchange')
    credit_limit = fields.Float('Credit Limit',track_visibility='onchange')
    # partner_state = fields.Selection(default="draft", selection=[('draft', 'Draft'), ('sale_approval', 'Sales Manager Approval'), ('financial_approval', 'Financial Manager Approval'), ], track_visibility='onchange' )
    #
    # def action_sale_manager_approve(self):
    #     self.write({'partner_state': 'sale_approval'})
    #
    # def action_financial_manager_approval(self):
    #     self.write({'partner_state': 'financial_approval'})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: