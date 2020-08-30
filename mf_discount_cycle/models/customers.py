# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import time
import numpy as np
import datetime as dt

class discount_cycle_customer(models.Model):
    _inherit = 'res.partner'

    disc_valu_quar = fields.Integer(string="percentage", required=False, )
    disc_valu_annu = fields.Integer(string="percentage", required=False, )
    disc_available_quar = fields.Float(string="Discount Value",  required=False, )
    disc_available_annu= fields.Float(string="Discount Value",  required=False, )

    partner_balance = fields.Float(string="",  required=False,)
    quarter_balance = fields.Float(string="",  required=False,)


    def get_quarter(self):
        now = datetime.now()
        quarter_of_the_year = str((now.month - 1) // 3 + 1)
        print(quarter_of_the_year)
        print(date(date.today().year,date.today().month, 6))

    def get_quareter_balance(self):
        now = datetime.now()
        quarter_of_the_year = str((now.month - 1) // 3 + 1)
        daterange_list = []
        if quarter_of_the_year == '2':
            a = date(date.today().year, 1, 1)
            b = date(date.today().year, 3, 30)
            daterange = [a + timedelta(days=x) for x in range(0, (b - a).days +1)]
            for da in daterange:
                daterange_list.append(date.strftime(da,"%Y-%m-%d"))
        elif quarter_of_the_year == '3':
            a = date(date.today().year, 4, 1)
            b = date(date.today().year, 6, 30)
            daterange = [a + timedelta(days=x) for x in range(0, (b - a).days + 1)]
            for da in daterange:
                daterange_list.append(date.strftime(da, "%Y-%m-%d"))
        elif quarter_of_the_year == '4':
            a = date(date.today().year, 7, 1)
            b = date(date.today().year, 9, 30)
            daterange = [a + timedelta(days=x) for x in range(0, (b - a).days + 1)]
            for da in daterange:
                daterange_list.append(date.strftime(da, "%Y-%m-%d"))
        elif quarter_of_the_year == '1':
            a = date(date.today().year, 10, 1)
            b = date(date.today().year, 12, 31)
            daterange = [a + timedelta(days=x) for x in range(0, (b - a).days +1)]
            daterange_list = []
            for da in daterange:
                daterange_list.append(date.strftime(da, "%Y-%m-%d"))
        print(daterange_list ,'\n**********************')
        anuu = self.env['res.partner'].search([])
        for rec in anuu:
            accounts = [rec.property_account_payable_id.id,rec.property_account_receivable_id.id]
            entries_by_partner_date = rec.env['account.move.line'].search([('partner_id', '=', rec.id),('move_id.state', '=','posted'),('account_id', 'in', accounts),
                                                  ('date','in', daterange_list)])
            credits_notes_by_partner_date = rec.env['account.move.line'].search([('partner_id', '=', rec.id),('move_id.state','=','posted'),
                                                  ('date','in', daterange_list),('move_id.type','=','entry')])
            total_credit = sum(entries_by_partner_date.mapped('credit'))
            total_debit = sum(entries_by_partner_date.mapped('debit'))
            total_credit_notes = sum(credits_notes_by_partner_date.mapped('credit'))
            total_debit_notes = sum(credits_notes_by_partner_date.mapped('debit'))
            balance = total_debit - total_credit
            balance_notes = total_debit_notes
            rec.quarter_balance = balance + balance_notes
        return

    def get_balance(self):
        anuu = self.env['res.partner'].search([])
        for rec in anuu:
            accounts = [rec.property_account_payable_id.id,rec.property_account_receivable_id.id]
            a = date(date.today().year, 1, 1)
            b = date(date.today().year, 12, 31)
            # listOfDates = [date for date in np.arange(a, b, dt.timedelta(days=x))]
            daterange = [a + timedelta(days=x) for x in range(0, (b - a).days + 1)]
            daterange_list=[]
            for da in daterange:
                daterange_list.append(date.strftime(da,"%Y-%m-%d"))
            entries_by_partner_date = rec.env['account.move.line'].search([('partner_id', '=', rec.id),('move_id.state', '=','posted'),('account_id', 'in', accounts),
                                                  ('date','in', daterange_list)])
            credits_notes_by_partner_date = rec.env['account.move.line'].search([('partner_id', '=', rec.id),('move_id.state','=','posted'),
                                                  ('date','in', daterange_list),('move_id.type','=','entry')])
            print(entries_by_partner_date, '***********')
            print(credits_notes_by_partner_date, '*********** credits_notes_by_partner_date')
            total_credit = sum(entries_by_partner_date.mapped('credit'))
            total_debit = sum(entries_by_partner_date.mapped('debit'))
            total_credit_notes = sum(credits_notes_by_partner_date.mapped('credit'))
            total_debit_notes = sum(credits_notes_by_partner_date.mapped('debit'))
            balance = total_debit - total_credit
            print(balance, '******************* balance')
            balance_notes = total_debit_notes
            rec.partner_balance = balance + balance_notes
        return

    def set_annu_discount(self):
        anuu = self.env['res.partner'].search([])
        for rec in anuu:
            if rec.disc_valu_annu:
                if rec.partner_balance > 0:
                    rec.disc_available_annu = rec.partner_balance * (rec.disc_valu_annu / 100)
        pass

    def set_quar_discount(self):
        anuu = self.env['res.partner'].search([])
        for rec in anuu:
            if rec.disc_valu_quar:
                if rec.quarter_balance > 0:
                    rec.disc_available_quar = rec.quarter_balance * (rec.disc_valu_quar / 100)
        pass

    def compute_annu_discount(self):
        anuu = self.env['res.partner'].search([])
        self.get_balance()
        print('compute_annu_discount')
        for rec in anuu:
            current_discount = rec.disc_available_annu
            if rec.disc_valu_annu:
                if rec.partner_balance > 0:
                    rec.disc_available_annu = rec.partner_balance * (rec.disc_valu_annu / 100) + current_discount
        pass

    def compute_quar_discount(self):
        anuu = self.env['res.partner'].search([])
        self.get_quareter_balance()
        print('compute_quar_discount')
        for rec in anuu:
            current_discount = rec.disc_available_quar
            print(current_discount, 'current_discount')
            if rec.disc_valu_quar:
                if rec.quarter_balance > 0:
                    rec.disc_available_quar = rec.quarter_balance * (rec.disc_valu_quar / 100) + current_discount
                    print(rec.disc_available_quar)
        pass

