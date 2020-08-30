# -*- coding: utf-8 -*-
# See Odoo OPL-1 LICENSE for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PoRefuseReason(models.TransientModel):
    _name = "po.refuse.reason"

    po_ref_id = fields.Many2one('purchase.order', string="Reference")
    refuse_reason = fields.Text(string='Refused Reason')

    # @api.multi
    def send_po_refuse_mail(self):
        email_template = self.env.ref(
            'po_three_levels_approval.po_refuse_email_template')
        mail_mail = email_template and email_template.send_mail(self.po_ref_id.id) or False
        mail_mail and self.env['mail.mail'].browse(mail_mail).send()

    # @api.multi
    def btn_refuse_reason(self):
        if not self.env.user.partner_id.email and \
                self.po_ref_id.partner_id.email:
            raise UserError(_("Please check the Email id."))
        if self.po_ref_id:
            self.send_po_refuse_mail()
            # template = self.env.ref(
            #     'po_three_levels_approval.po_refuse_email_template')
            # template.send_mail(self.po_ref_id.id)
            # self.env['mail.mail'].process_email_queue()
            self.po_ref_id.write({'state': "refuse",
                                  'refused_uid': self.env.user.id,
                                  'refused_date':
                                      fields.Date.context_today(self),
                                  'refused_reason': self.refuse_reason
                                  })
