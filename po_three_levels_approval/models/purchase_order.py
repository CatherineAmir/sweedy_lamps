# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_po_department_domain(self):
        po_manager_ids = self.env.ref(
            'po_three_levels_approval.group_department_approver').users.ids
        department_manager = [('id', 'in', po_manager_ids)]
        return department_manager

    def _get_po_finance_domain(self):
        # po_finance_ids = self.env.ref('account.group_account_manager').users.ids
        po_finance_ids = self.env.ref('approval_groups.group_cfo').users.ids
        finance_manager = [('id', 'in', po_finance_ids)]
        return finance_manager

    def _get_po_director_domain(self):
        director_manager_ids = self.env.ref(
            'po_three_levels_approval.group_po_director_approver').users.ids
        director_manager = [('id', 'in', director_manager_ids)]
        return director_manager

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False,
        default='draft', track_visibility='onchange')
    state = fields.Selection(selection_add=[('department_approve', 'Waiting For Department Approval'),
        ('finance_approve', 'Waiting For Finance Approval'),
        ('director_approve', 'Waiting For Director Approval'),
        ('refuse', 'Refuse'),],string='Status')

    depart_approval_id = fields.Many2one('res.users',
                                         string='Approval Department Manager', copy=False)
    finance_approval_id = fields.Many2one('res.users',
                                          string='Approval Finance Manager', copy=False)
    director_approval_id = fields.Many2one('res.users',
                                           string='Approval Director Manager', copy=False)
    department_id = fields.Many2one('res.users',
                                    string='Purchase/Department Manager',
                                    domain=_get_po_department_domain, )
    finance_id = fields.Many2one('res.users',
                                 string='Finance Manager',
                                 domain=_get_po_finance_domain,)
    director_id = fields.Many2one('res.users',
                                  string='Director Manager',
                                  domain=_get_po_director_domain,)
    department_approve_date = fields.Date('Department Manager Approval Date', copy=False)
    finance_approve_date = fields.Date('Finance Manager Approval Date', copy=False)
    director_approve_date = fields.Date('Director Manager Approval Date', copy=False)
    refused_uid = fields.Many2one('res.users', string='Refused By', copy=False)
    refused_date = fields.Date('Refused Date', copy=False)
    refused_reason = fields.Text('Refused Reason', copy=False)

    # @api.multi
    def send_po_aprroval_mail(self):
        mail_to = self._context.get('mail_to')
        partner_id = self._context.get('partner_id')
        partner_name = self._context.get('partner_name')
        email_template = self.env.ref(
            'po_three_levels_approval.po_approval_email_template')
        mail_mail = email_template and email_template.with_context(mail_to=mail_to,partner_id=partner_id,partner_name=partner_name).send_mail(
            self.id) or False
        mail_mail and self.env['mail.mail'].browse(mail_mail).send()

    # @api.multi
    def button_department_approve(self, force=False):
        if self.env.user != self.department_id:
            raise UserError("Only selected Approver can approve this.")
        if self.amount_total < self.env.user.company_id.currency_id._convert(self.company_id.finanace_validation_amt, self.currency_id, self.company_id, self.date_order or fields.Date.today()):
            self.write({
                'state': 'purchase',
                'depart_approval_id': self.env.uid,
                'department_approve_date': fields.Date.context_today(self)
            })
            self.filtered(
                lambda p: p.company_id.po_lock == 'lock').write(
                {'state': 'done'})
        else:
            finance_manager = self.finance_id.partner_id
            self.with_context(mail_to=finance_manager.email,partner_id=finance_manager.id,partner_name=finance_manager.name).send_po_aprroval_mail()
            self.write({'state': 'finance_approve',
                        'depart_approval_id': self.env.uid,
                        'department_approve_date':
                            fields.Date.context_today(self)
                        })
        return {}

    # @api.multi
    def btn_finance_approve(self, force=False):
        if self.env.user != self.finance_id:
            raise UserError("Only selected Approver can approve this PO.")
        if self.amount_total < self.env.user.company_id.currency_id._convert(
                self.company_id.ceo_validation_amt,
                self.currency_id, self.company_id, self.date_order or fields.Date.today()):
            self.write({'state': 'purchase',
                        'date_approve': fields.Date.context_today(self)})
            self.filtered(
                lambda p: p.company_id.po_lock == 'lock').write(
                {'state': 'done'})
        else:
            director_manager = self.director_id.partner_id
            self.with_context(mail_to=director_manager.email,partner_id=director_manager.id,partner_name=director_manager.name).send_po_aprroval_mail()
            self.write({'state': 'director_approve',
                        'finance_approval_id': self.env.uid,
                        'finance_approve_date':
                            fields.Date.context_today(self)
                        })
        return {}

    def btn_po_director_approve(self, force=False):
        if self.env.user != self.director_id:
            raise UserError("Only selected Approver can approve this PO.")
        po_managers = self.env.ref('purchase.group_purchase_manager').mapped('users.partner_id')
        for po_mng in po_managers:
            self.with_context(mail_to=po_mng.email,partner_id=po_mng.id,partner_name=po_mng.name).send_po_aprroval_mail()
        self.write({
                    'director_approval_id': self.env.uid,
                    'director_approve_date': fields.Date.context_today(self),
                    'date_approve': fields.Date.context_today(self)})
        self.button_approve()

        return {}

    def button_refused_reason(self):
        if self.env.user != self.department_id and \
                self.env.user != self.finance_id and \
                self.env.user != self.director_id:
            raise UserError("Only selected Approver can Refuse this PO.")
        return {
            'name': 'Refuse Purchase Order',
            'type': 'ir.actions.act_window',
            'res_model': 'po.refuse.reason',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_po_ref_id': self.id},
        }

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()

            # Deal with double validation process
            # if order.company_id.po_double_validation == 'one_step' or\
            #         (order.company_id.po_double_validation == 'two_step'
            #          and order.amount_total <
            #          self.env.user.company_id.currency_id.compute(
            #              order.company_id.po_double_validation_amount,
            #              order.currency_id)) or\
            #         order.user_has_groups('purchase.group_purchase_manager'):
            #     order.button_approve()

            # Deal with three level validation
            # if not order.company_id.is_three_steps == True or \
            #         order.amount_total < \
            #         self.env.user.company_id.currency_id._convert(order.company_id.double_validation_amt, order.currency_id, order.company_id, order.date_order or fields.Date.today()):
            #     order.button_approve()
            # else:
            #     order.write({'state': 'to approve'})
            department_manager = self.department_id.partner_id
            self.with_context(mail_to=department_manager.email,partner_id=department_manager.id,partner_name=department_manager.name)
            order.write({'state': 'department_approve'})
        return True
