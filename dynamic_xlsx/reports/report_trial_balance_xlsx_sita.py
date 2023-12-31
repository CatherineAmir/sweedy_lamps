# _*_ coding: utf-8
from odoo import models, fields, api,_

from datetime import datetime
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}

class InsTrialBalanceXlsx(models.AbstractModel):
    _name = 'report.dynamic_xlsx.ins_trial_balance_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            #'border': True
        })
        self.format_merged_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'right': True,
            'left': True,
            'font': 'Arial',
        })
        self.format_merged_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            # 'right': False,
            'left': True,
            'font': 'Arial',
        })
        self.format_merged_header_right = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'right': True,
            # 'left': False,
            'font': 'Arial',
        })
        self.format_merged_header_without_border = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        self.content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'font': 'Arial',
        })
        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        self.line_header_total = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        self.line_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })
        self.line_header_left_total = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        self.line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        self.line_header_light_total = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        self.line_header_light_left = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })
        self.line_header_highlight = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        self.line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })

    def prepare_report_filters(self, data, filter):
        """It is writing under second page"""
        self.row_pos_2 += 2
        if filter:
            # Date from
            self.sheet_2.write_string(self.row_pos_2, 0, _('Date from'),
                                    self.format_header)
            self.sheet_2.write_datetime(self.row_pos_2, 1, self.convert_to_date(str(filter['date_from']) or ''),
                                    self.line_header_light_date)
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Date to'),
                                    self.format_header)
            self.sheet_2.write_datetime(self.row_pos_2, 1, self.convert_to_date(str(filter['date_to']) or ''),
                                    self.line_header_light_date)

            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Display accounts'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, filter['display_accounts'],
                                    self.content_header)

            # Journals
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Journals'),
                                    self.format_header)
            j_list = ', '.join([lt or '' for lt in filter.get('journals')])
            self.sheet_2.write_string(self.row_pos_2, 1, j_list,
                                      self.content_header)

            # Accounts
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Analytic Accounts'),
                                      self.format_header)
            a_list = ', '.join([lt or '' for lt in filter.get('analytics')])
            self.sheet_2.write_string(self.row_pos_2, 1, a_list,
                                      self.content_header)



    def prepare_report_contents(self, acc_lines, retained, subtotal, filter,date_range):
        print('prepare_report_contents trail balance xlsx Cathy')
        self.row_pos += 3
        self.sheet.merge_range(self.row_pos, 2, self.row_pos, 4, 'Initial Balance', self.format_merged_header)
        for d in range(0 ,len(date_range)):


            self.sheet.write_datetime(self.row_pos, 5+(d*3), self.convert_to_date(date_range[d][0]),
                                      self.format_merged_header_left)
            self.sheet.write_string(self.row_pos, 6+(d*3), _(' To '),
                                      self.format_merged_header_without_border)
            self.sheet.write_datetime(self.row_pos, 7+(d*3), self.convert_to_date(date_range[d][1]),
                                      self.format_merged_header_without_border)


        d=d+1
        self.sheet.merge_range(self.row_pos, 5+(d*3), self.row_pos, 7+(d*3), 'Ending Balance', self.format_merged_header)

        self.row_pos += 1

        self.sheet.write_string(self.row_pos, 0, _('Account Code'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 1, _('Account Name'),
                                self.format_header)

        self.sheet.write_string(self.row_pos, 2, _('Debit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 3, _('Credit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 4, _('Balance'),
                                self.format_header)
        for d in range(0, len(date_range)):

            self.sheet.write_string(self.row_pos, 5+(d*3), _('Debit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 6+(d*3), _('Credit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 7+(d*3), _('Balance'),
                                self.format_header)
        d = d + 1
        self.sheet.write_string(self.row_pos, 5+(d*3), _('Debit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 6+(d*3), _('Credit'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 7+(d*3), _('Balance'),
                                self.format_header)

        if acc_lines:
            if not filter.get('show_hierarchy'):
                for line in acc_lines: # Normal lines
                    self.row_pos += 1
                    # before
                    self.sheet.write_string(self.row_pos, 0,  acc_lines[line].get('code') + ' ' +acc_lines[line].get('name'), self.line_header_light_left)

                    # after

                    self.sheet.write_string(self.row_pos, 0,  acc_lines[line].get('code') , self.line_header_light_left)
                    self.sheet.write_string(self.row_pos, 1, acc_lines[line].get('name'), self.line_header_light_left)

                    self.sheet.write_number(self.row_pos, 2, float(acc_lines[line].get('initial_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 3, float(acc_lines[line].get('initial_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 4, float(acc_lines[line].get('initial_balance')), self.line_header_highlight)


                    for i in range(0,len(acc_lines[line].get('debit'))):
                        self.sheet.write_number(self.row_pos, 5+(i*3), float(acc_lines[line].get('debit')[i]), self.line_header_light)
                        self.sheet.write_number(self.row_pos, 6+(i*3), float(acc_lines[line].get('credit')[i]), self.line_header_light)
                        self.sheet.write_number(self.row_pos, 7+(i*3), float(acc_lines[line].get('balance')[i]), self.line_header_highlight)

                    i=i+1
                    self.sheet.write_number(self.row_pos, 5+(i*3), float(acc_lines[line].get('ending_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 6+(i*3), float(acc_lines[line].get('ending_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos,7+(i*3) , float(acc_lines[line].get('ending_balance')), self.line_header_highlight)
            else:
                for line in acc_lines: # Normal lines
                    self.row_pos += 1
                    blank_space = '   ' * len(line.get('indent_list'))
                    if line.get('dummy'):
                        self.sheet.write_string(self.row_pos, 0,  blank_space + line.get('code'),
                                                self.line_header_light_left)
                        self.sheet.write_string(self.row_pos, 1,  blank_space + line.get('name'),
                                                self.line_header_light_left)
                    else:
                        self.sheet.write_string(self.row_pos, 0, blank_space + line.get('code') ,
                                                self.line_header_light_left)
                        self.sheet.write_string(self.row_pos, 1, blank_space +  line.get('name'),
                                                self.line_header_light_left)
                    self.sheet.write_number(self.row_pos, 2, float(line.get('initial_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 3, float(line.get('initial_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 4, float(line.get('initial_balance')), self.line_header_highlight)

                    for i in range(0, len(line.get('debit'))):

                        self.sheet.write_number(self.row_pos, 5+(i*3), float(line.get('debit')[i]), self.line_header_light)
                        self.sheet.write_number(self.row_pos, 6+(i*3), float(line.get('credit')[i]), self.line_header_light)
                        self.sheet.write_number(self.row_pos, 7+(i*3), float(line.get('balance')[i]), self.line_header_highlight)


                    i=i+1
                    self.sheet.write_number(self.row_pos, 5+(i*3), float(line.get('ending_debit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 6+(i*3), float(line.get('ending_credit')), self.line_header_light)
                    self.sheet.write_number(self.row_pos, 7+(i*3), float(line.get('ending_balance')), self.line_header_highlight)


            if filter.get('strict_range'):
                # Retained Earnings line
                self.row_pos += 1
                self.sheet.write_string(self.row_pos, 0, '        ' + retained['RETAINED'].get('code'), self.line_header_light_left)

                self.sheet.write_string(self.row_pos, 1, '        ' + retained['RETAINED'].get('name'), self.line_header_light_left)

                self.sheet.write_number(self.row_pos, 2, float(retained['RETAINED'].get('initial_debit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 3, float(retained['RETAINED'].get('initial_credit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 4, float(retained['RETAINED'].get('initial_balance')), self.line_header_highlight)

                self.sheet.write_number(self.row_pos, 5, float(retained['RETAINED'].get('debit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 6, float(retained['RETAINED'].get('credit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 7, float(retained['RETAINED'].get('balance')), self.line_header_highlight)


                self.sheet.write_number(self.row_pos, 8, float(retained['RETAINED'].get('ending_debit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 9, float(retained['RETAINED'].get('ending_credit')), self.line_header_light)
                self.sheet.write_number(self.row_pos, 10, float(retained['RETAINED'].get('ending_balance')), self.line_header_highlight)
            # Sub total line
            self.row_pos += 2
            # before
            self.sheet.write_string(self.row_pos, 0,  subtotal['SUBTOTAL'].get('code') + ' ' + subtotal['SUBTOTAL'].get('name'), self.line_header_left_total)
            # after

            print('subtotal',subtotal)
            # TODO subtotal
            self.sheet.write_string(self.row_pos, 0,  subtotal['SUBTOTAL'].get('code') , self.line_header_left_total)
            self.sheet.write_string(self.row_pos, 1,  subtotal['SUBTOTAL'].get('name'), self.line_header_left_total)
            self.sheet.write_number(self.row_pos, 2,float(subtotal['SUBTOTAL'].get('initial_debit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 3, float(subtotal['SUBTOTAL'].get('initial_credit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 4, float(subtotal['SUBTOTAL'].get('initial_balance')), self.line_header_total)
            for i in range(0, len(subtotal['SUBTOTAL'].get('debit'))):
                self.sheet.write_number(self.row_pos, 5+(i*3), float(subtotal['SUBTOTAL'].get('debit')[i]), self.line_header_light_total)
                self.sheet.write_number(self.row_pos, 6+(i*3), float(subtotal['SUBTOTAL'].get('credit')[i]), self.line_header_light_total)
                self.sheet.write_number(self.row_pos, 7+(i*3), float(subtotal['SUBTOTAL'].get('balance')[i]), self.line_header_total)
            i=i+1
            self.sheet.write_number(self.row_pos, 5+(i*3), float(subtotal['SUBTOTAL'].get('ending_debit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 6+(i*3), float(subtotal['SUBTOTAL'].get('ending_credit')), self.line_header_light_total)
            self.sheet.write_number(self.row_pos, 7+(i*3), float(subtotal['SUBTOTAL'].get('ending_balance')), self.line_header_total)

    def _format_float_and_dates(self, currency_id, lang_id):

        self.line_header.num_format = currency_id.excel_format

        self.line_header_light.num_format = currency_id.excel_format

        self.line_header_highlight.num_format = currency_id.excel_format

        self.line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        self.format_merged_header_without_border.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        self.format_merged_header_left.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        self.format_merged_header_right.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

    def convert_to_date(self, datestring=False):
        if datestring:
            datestring = fields.Date.from_string(datestring).strftime(self.language_id.date_format)
            return datetime.strptime(datestring, self.language_id.date_format)
        else:
            return False

    def generate_xlsx_report(self, workbook, data, record):
        self._define_formats(workbook)
        self.row_pos = 0
        self.row_pos_2 = 0
        self.sheet = workbook.add_worksheet('General Ledger')
        self.sheet_2 = workbook.add_worksheet('Filters')


        self.sheet_2.set_column(0, 0, 35)
        self.sheet_2.set_column(1, 1, 25)
        self.sheet_2.set_column(2, 2, 25)
        self.sheet_2.set_column(3, 3, 25)
        self.sheet_2.set_column(4, 4, 25)
        self.sheet_2.set_column(5, 5, 25)
        self.sheet_2.set_column(6, 6, 25)

        self.sheet.freeze_panes(5, 0)

        self.sheet.set_zoom(80)

        self.sheet.screen_gridlines = False
        self.sheet_2.screen_gridlines = False
        self.sheet_2.protect()
        # For Formating purpose
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            data = record.read()
            self.sheet.merge_range(0, 0, 0, 10, 'Trial Balance'+' - '+data[0]['company_id'][1], self.format_title)
            self.dateformat = self.env.user.lang
            filters, account_lines, retained, subtotal,date_range = record.get_report_datas()
            self.sheet.set_column(0, 0, 20)
            self.sheet.set_column(1, 1, 30)
            self.sheet.set_column(2, 2, 15)
            self.sheet.set_column(3, 3, 15)
            self.sheet.set_column(4, 4, 15)
            self.sheet.set_column(5, 5, 15)
            self.sheet.set_column(6, 6, 15)
            self.sheet.set_column(7, 7, 15)
            for d in range(0,len(date_range)):
                self.sheet.set_column(8+(d*3), 8+(d*3), 15)
                self.sheet.set_column(9+(d*3), 9+(d*3), 15)
                self.sheet.set_column(10+d, 10+(d*3), 15)


            print('account_lines')
            # Filter section
            self.prepare_report_filters(data, filters)
            # Content section
            self.prepare_report_contents(account_lines, retained, subtotal, filters,date_range)
