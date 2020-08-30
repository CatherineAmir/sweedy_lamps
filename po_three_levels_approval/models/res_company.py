# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    is_three_steps = fields.Boolean(string='PO Three Steps Approval',
                                    default=False,
                                    help='Three Steps Approval field allows '
                                         'you to allows settings for '
                                         'PO approval.')
    po_approval_mail_temp = fields.Many2one('mail.template',
                                            string='PO Approval Email Template')
    po_refuse_mail_temp = fields.Many2one('mail.template',
                                          string='PO Refuse Email Template')
    double_validation_amt = fields.Float(string='Double Validation Amount')
    finanace_validation_amt = fields.Float(string='Finance Validation Amount')
    ceo_validation_amt = fields.Float(string='CEO Validation Amount')

    @api.onchange('is_three_steps')
    def _set_template_and_amt(self):
        if self.is_three_steps == True:
            self.po_approval_mail_temp = self.env.ref(
                'po_three_levels_approval.po_approval_email_template').id
            self.po_refuse_mail_temp = self.env.ref(
                'po_three_levels_approval.po_refuse_email_template').id
        else:
            self.po_approval_mail_temp = False
            self.po_refuse_mail_temp = False
            self.double_validation_amt = 0.00
            self.finanace_validation_amt = 0.00
            self.ceo_validation_amt = 0.00
