# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class PurchaseLetterCredit(models.Model):
    _name = 'purchase.letter.credit'
    _rec_name = 'name'
    _description = 'Purchase Letter Credit'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name", required=False, )
    date = fields.Date(string="", required=True, )
    expiration_date = fields.Date(string="", required=True, )
    delivery_date = fields.Date(string="", required=True, )
    vendor_id = fields.Many2one(comodel_name="res.partner", string="", required=True, )
    lc_type_id = fields.Many2one(comodel_name="purchase.letter.credit.type", string="", required=True, )
    lc_amount = fields.Float(string="",  required=False, )
    lc_remaining_amount = fields.Float(string="",  compute='compute_remaining_amount' )
    currency_id = fields.Many2one(comodel_name="res.currency", string="", required=True, )
    currency_rate = fields.Float(string="",  required=False, )

    customs_clearance_no = fields.Char(string="", required=False, )
    customs_release_no = fields.Char(string="", required=False, )
    lc_number = fields.Char(string="LC Number", required=False, )
    purchase_order_ids = fields.Many2many(comodel_name="purchase.order", string="Add Purchase Orders", )
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('open', 'Open'),('closed', 'Closed'), ('cancel', 'Cancel'), ],default='draft' )
    period_extend_history_ids = fields.One2many(comodel_name="lc.period.extend", inverse_name="purchase_lc_id", string="", required=False, )
    amount_extend_history_ids = fields.One2many(comodel_name="lc.amount.extend", inverse_name="purchase_lc_id", string="", required=False, )
    account_move_ids = fields.One2many(comodel_name="account.move", inverse_name="purchase_lc_id", string="", required=False, )
    payment_ids = fields.One2many(comodel_name="account.payment", inverse_name="purchase_lc_id", string="", required=False, )
    bank_fees_amount = fields.Float(string="",  required=False, )
    move_count = fields.Integer(compute='compute_move_count' )
    period_extend_count = fields.Integer(compute='compute_period_extend_count')
    amount_extend_count = fields.Integer(compute='compute_amount_extend_count' )

    def compute_move_count(self):
        for rec in self:
            rec.move_count = len(rec.account_move_ids)

    def compute_period_extend_count(self):
        for rec in self:
            rec.period_extend_count = len(rec.period_extend_history_ids)

    def compute_amount_extend_count(self):
        for rec in self:
            rec.amount_extend_count = len(rec.amount_extend_history_ids)

    @api.depends('lc_amount','bank_fees_amount','payment_ids','period_extend_history_ids','amount_extend_history_ids')
    def compute_remaining_amount(self):
        for rec in self:
            payment_amount = sum(rec.payment_ids.mapped('amount'))
            rec.lc_remaining_amount = rec.lc_amount - payment_amount - rec.bank_fees_amount

    def open_account_move(self):
        domain = [('id','in',self.account_move_ids.ids)]
        view_tree = {
            'name': _(' Journal Entries '),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return view_tree

    def open_period_extend(self):
        domain = [('id','in',self.period_extend_history_ids.ids)]
        view_tree = {
            'name': _(' Period Extend History '),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.period.extend',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return view_tree

    def open_amount_extend(self):
        domain = [('id','in',self.amount_extend_history_ids.ids)]
        view_tree = {
            'name': _(' Amount Extend History '),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.amount.extend',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return view_tree

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.letter.credit')
        res = super(PurchaseLetterCredit,self).create(vals)
        return res

    def action_open(self):
        self.create_start_journal_entries(self.lc_amount)
        if self.lc_type_id.is_bank_fees_from_lc:
            self.add_bank_fees(self.lc_amount)
        self.write({'state':'open'})

    def add_bank_fees(self,lc_amount):
        bank_ratio = self.lc_type_id.bank_fees / 100.0
        current_bank_fees = self.bank_fees_amount
        new_bank_fees = current_bank_fees + bank_ratio * lc_amount
        self.write({'bank_fees_amount': new_bank_fees})

    def create_start_journal_entries(self,lc_amount):
        if lc_amount:
            company_amount = self.currency_rate * lc_amount
            move_vals_1 = {
                'type': 'entry',
                'date': self.date,
                'journal_id': self.lc_type_id.lc_bank_journal_id.id,
                'currency_id': self.currency_id.id,
                'purchase_lc_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': 'line_debit',
                        'account_id': self.lc_type_id.intermediate_account_id.id ,
                        'partner_id': self.vendor_id.id,
                        'debit': company_amount,
                        'credit': 0,
                        'currency_id': self.currency_id.id,
                        'amount_currency': lc_amount,
                    }),
                    (0, 0, {
                        'name': 'line_credit',
                        'account_id': self.lc_type_id.lc_bank_journal_id.default_credit_account_id.id,
                        'partner_id': self.vendor_id.id,
                        'debit': 0,
                        'credit': company_amount,
                        'currency_id': self.currency_id.id,
                        'amount_currency': -1* lc_amount,
                    }),
                ],
            }
            self.env['account.move'].create(move_vals_1)
            move_vals_2 = {
                'type': 'entry',
                'date': self.date,
                'journal_id': self.lc_type_id.lc_journal_id.id,
                'currency_id': self.currency_id.id,
                'purchase_lc_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': 'line_debit',
                        'account_id': self.lc_type_id.lc_journal_id.default_debit_account_id.id,
                        'partner_id': self.vendor_id.id,
                        'debit': company_amount,
                        'credit': 0,
                        'currency_id': self.currency_id.id,
                        'amount_currency': lc_amount,
                    }),
                    (0, 0, {
                        'name': 'line_credit',
                        'account_id': self.lc_type_id.intermediate_account_id.id ,
                        'partner_id': self.vendor_id.id,
                        'debit': 0,
                        'credit': company_amount,
                        'currency_id': self.currency_id.id,
                        'amount_currency': -1* lc_amount,
                    }),

                ],
            }
            self.env['account.move'].create(move_vals_2)
            if self.lc_type_id.is_bank_fees_from_lc:
                expense_account = self.lc_type_id.lc_journal_id.default_debit_account_id.id
                expense_journal =  self.lc_type_id.lc_journal_id.id
            else:
                expense_account = self.lc_type_id.lc_bank_journal_id.default_debit_account_id.id
                expense_journal = self.lc_type_id.lc_bank_journal_id.id

            bank_ratio = self.lc_type_id.bank_fees / 100.0
            move_vals_3 = {
                'type': 'entry',
                'date': self.date,
                'journal_id': expense_journal,
                'currency_id': self.currency_id.id,
                'purchase_lc_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': 'line_debit',
                        'account_id': self.lc_type_id.bank_expense_account_id.id,
                        # 'partner_id': self.vendor_id.id,
                        'debit': company_amount * bank_ratio,
                        'credit': 0,
                        'currency_id': self.currency_id.id,
                        'amount_currency': lc_amount * bank_ratio,
                    }),
                    (0, 0, {
                        'name': 'line_credit',
                        'account_id': expense_account ,
                        # 'partner_id': self.vendor_id.id,
                        'debit': 0,
                        'credit': company_amount * bank_ratio,
                        'currency_id': self.currency_id.id,
                        'amount_currency': -1 * lc_amount * bank_ratio,
                    }),

                ],
            }
            self.env['account.move'].create(move_vals_3)

    def action_close(self):
        self.create_end_journal_entries(self.lc_remaining_amount)
        self.write({'state':'closed'})

    def create_end_journal_entries(self,lc_amount):
        if lc_amount:
            company_amount = self.currency_rate * lc_amount
            move_vals_1 = {
                'type': 'entry',
                'date': self.date,
                'journal_id': self.lc_type_id.lc_bank_journal_id.id,
                'currency_id': self.currency_id.id,
                'purchase_lc_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': 'line_credit',
                        'account_id': self.lc_type_id.intermediate_account_id.id ,
                        'partner_id': self.vendor_id.id,
                        'debit': 0,
                        'credit': company_amount,
                        'currency_id': self.currency_id.id,
                        'amount_currency': -1 * lc_amount,
                    }),
                    (0, 0, {
                        'name': 'line_debit',
                        'account_id': self.lc_type_id.lc_bank_journal_id.default_credit_account_id.id,
                        'partner_id': self.vendor_id.id,
                        'debit': company_amount,
                        'credit': 0,
                        'currency_id': self.currency_id.id,
                        'amount_currency': lc_amount,
                    }),
                ],
            }
            self.env['account.move'].create(move_vals_1)
            move_vals_2 = {
                'type': 'entry',
                'date': self.date,
                'journal_id': self.lc_type_id.lc_journal_id.id,
                'currency_id': self.currency_id.id,
                'purchase_lc_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': 'line_credit',
                        'account_id': self.lc_type_id.lc_journal_id.default_debit_account_id.id,
                        'partner_id': self.vendor_id.id,
                        'debit': 0,
                        'credit': company_amount,
                        'currency_id': self.currency_id.id,
                        'amount_currency': -1 * lc_amount,
                    }),
                    (0, 0, {
                        'name': 'line_debit',
                        'account_id': self.lc_type_id.intermediate_account_id.id ,
                        'partner_id': self.vendor_id.id,
                        'debit': company_amount,
                        'credit': 0,
                        'currency_id': self.currency_id.id,
                        'amount_currency': lc_amount,
                    }),

                ],
            }
            self.env['account.move'].create(move_vals_2)

    @api.onchange('currency_id','date')
    def onchange_currency(self):
        if self.currency_id:
            self.currency_rate = self.currency_id.with_context(date=self.date).rate


class LcPeriodExtend(models.Model):
    _name = 'lc.period.extend'
    _rec_name = 'name'
    _description = 'Lc Period Extend'
    _order = 'name asc, id desc'

    name = fields.Text(string="Description", required=True, )
    expiration_date = fields.Date(string="Expiration Date", required=True, )
    amount = fields.Float(string="",  required=False, )
    purchase_lc_id = fields.Many2one(comodel_name="purchase.letter.credit", string="", required=False, )


class LcAmountExtend(models.Model):
    _name = 'lc.amount.extend'
    _rec_name = 'name'
    _description = 'Lc Amount Extend'
    _order = 'name asc, id desc'

    name = fields.Text(string="Description", required=True, )
    amount = fields.Float(string="",  required=False, )
    purchase_lc_id = fields.Many2one(comodel_name="purchase.letter.credit", string="", required=False, )

