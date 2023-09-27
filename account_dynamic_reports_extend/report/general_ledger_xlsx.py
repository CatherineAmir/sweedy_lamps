# _*_ coding: utf-8
from odoo import models, fields, api, _

from datetime import datetime


class InsGeneralLedgerXlsx(models.AbstractModel):
    _inherit = 'report.dynamic_xlsx.ins_general_ledger_xlsx'

    def prepare_report_contents(self, data, acc_lines, filter):
        # print("in prepare_report_contents account_dynamic_reports_extend gl")
        data = data[0]
        self.row_pos += 3

        if filter.get('include_details', False):
            self.sheet.write_string(self.row_pos, 0, _('Date'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('JRNL'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Partner'),
                                    self.format_header)
            # self.sheet.write_string(self.row_pos, 3, _('Ref'),
            #                         self.format_header)
            self.sheet.write_string(self.row_pos, 3, _('Move'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 4, _('Reference'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 5, _('Entry Label'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 6, _('Debit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 7, _('Credit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 8, _('Balance'),
                                    self.format_header)
        else:
            self.sheet.merge_range(self.row_pos, 0, self.row_pos, 1, _('Code'), self.format_header)
            self.sheet.merge_range(self.row_pos, 2, self.row_pos, 4, _('Account'), self.format_header)
            self.sheet.write_string(self.row_pos, 5, _('Debit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 6, _('Credit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 7, _('Balance'),
                                    self.format_header)

        if acc_lines:
            for line in acc_lines:
                self.row_pos += 1
                self.sheet.merge_range(self.row_pos, 0, self.row_pos, 5,
                                       '            ' + acc_lines[line].get('code') + ' - ' + acc_lines[line].get(
                                           'name'), self.line_header_left)
                self.sheet.write_number(self.row_pos, 6, float(acc_lines[line].get('debit')), self.line_header)
                self.sheet.write_number(self.row_pos, 7, float(acc_lines[line].get('credit')), self.line_header)
                self.sheet.write_number(self.row_pos, 8, float(acc_lines[line].get('balance')), self.line_header)

                if filter.get('include_details', False):
                    account_id = acc_lines[line].get('id')
                    count, offset, sub_lines = self.record.build_detailed_move_lines(offset=0, account=account_id,
                                                                                     fetch_range=1000000)

                    for sub_line in sub_lines:
                        if sub_line.get('move_name') == 'Initial Balance':
                            self.row_pos += 1
                            self.sheet.write_string(self.row_pos, 5, sub_line.get('move_name'),
                                                    self.line_header_light_initial)
                            self.sheet.write_number(self.row_pos, 6, float(acc_lines[line].get('debit')),
                                                    self.line_header_light_initial)
                            self.sheet.write_number(self.row_pos, 7, float(acc_lines[line].get('credit')),
                                                    self.line_header_light_initial)
                            self.sheet.write_number(self.row_pos, 8, float(acc_lines[line].get('balance')),
                                                    self.line_header_light_initial)
                        elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
                            self.row_pos += 1
                            self.sheet.write_datetime(self.row_pos, 0, self.convert_to_date(sub_line.get('ldate')),
                                                      self.line_header_light_date)
                            self.sheet.write_string(self.row_pos, 1, sub_line.get('lcode'),
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 2, sub_line.get('partner_name') or '',
                                                    self.line_header_light)
                            # self.sheet.write_string(self.row_pos, 3, sub_line.get('lref') or '',
                            #                         self.line_header_light)
                            self.sheet.write_string(self.row_pos, 3, sub_line.get('move_name'),
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 4, sub_line.get('move_ref') or '',
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 5, sub_line.get('lname') or '',
                                                    self.line_header_light)
                            self.sheet.write_number(self.row_pos, 6,
                                                    float(sub_line.get('debit')), self.line_header_light)
                            self.sheet.write_number(self.row_pos, 7,
                                                    float(sub_line.get('credit')), self.line_header_light)
                            self.sheet.write_number(self.row_pos, 8,
                                                    float(sub_line.get('balance')), self.line_header_light)
                        else:  # Ending Balance
                            self.row_pos += 1
                            self.sheet.write_string(self.row_pos, 5, sub_line.get('move_name'),
                                                    self.line_header_light_ending)
                            self.sheet.write_number(self.row_pos, 6, float(acc_lines[line].get('debit')),
                                                    self.line_header_light_ending)
                            self.sheet.write_number(self.row_pos, 7, float(acc_lines[line].get('credit')),
                                                    self.line_header_light_ending)
                            self.sheet.write_number(self.row_pos, 8, float(acc_lines[line].get('balance')),
                                                    self.line_header_light_ending)
