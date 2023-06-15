# _*_ coding: utf-8
from odoo import models, fields, api, _

from datetime import datetime


class InsPartnerAgeingXlsx(models.AbstractModel):
    _inherit = 'report.dynamic_xlsx.ins_partner_ageing_xlsx'

    def prepare_report_contents(self, data, period_dict, period_list, ageing_lines, filter):
        data = data[0]
        self.row_pos += 3

        if self.record.include_details:
            self.sheet.write_string(self.row_pos, 0, _('Entry #'), self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('Partner Ref'), self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Due Date'), self.format_header)
            self.sheet.write_string(self.row_pos, 3, _('Journal'), self.format_header)
            self.sheet.write_string(self.row_pos, 4, _('Account'), self.format_header)
        else:
            self.sheet.merge_range(self.row_pos, 0, self.row_pos, 4, _('Partner'),
                                   self.format_header)
        k = 5
        for period in period_list:
            self.sheet.write_string(self.row_pos, k, str(period),
                                    self.format_header_period)
            k += 1
        self.sheet.write_string(self.row_pos, k, _('Total'),
                                self.format_header_period)

        if ageing_lines:
            for line in ageing_lines:

                # Dummy vacant lines
                self.row_pos += 1
                self.sheet.write_string(self.row_pos, 5, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 6, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 7, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 8, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 9, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 10, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 11, '', self.line_header_light_period)
                self.sheet.write_string(self.row_pos, 12, '', self.line_header_light_period)

                self.row_pos += 1
                if line != 'Total':
                    self.sheet.merge_range(self.row_pos, 0, self.row_pos, 4, ageing_lines[line].get('partner_name'),
                                           self.line_header)
                else:
                    self.sheet.merge_range(self.row_pos, 0, self.row_pos, 4, _('Total'), self.line_header_total)
                k = 5
                for period in period_list:
                    if line != 'Total':
                        self.sheet.write_number(self.row_pos, k, ageing_lines[line][period], self.line_header)
                    else:
                        self.sheet.write_number(self.row_pos, k, ageing_lines[line][period], self.line_header_total)
                    k += 1
                if line != 'Total':
                    self.sheet.write_number(self.row_pos, k, ageing_lines[line]['total'], self.line_header)
                else:
                    self.sheet.write_number(self.row_pos, k, ageing_lines[line]['total'], self.line_header_total)

                if self.record.include_details:
                    if line != 'Total':
                        count, offset, sub_lines, period_list = self.record.process_detailed_data(partner=line,
                                                                                                  fetch_range=1000000)
                        for sub_line in sub_lines:
                            self.row_pos += 1
                            self.sheet.write_string(self.row_pos, 0, sub_line.get('move_name') or '',
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 1, sub_line.get('partner_ref') or '',
                                                    self.line_header_light)
                            date = self.convert_to_date(sub_line.get('date_maturity') or sub_line.get('date'))
                            self.sheet.write_datetime(self.row_pos, 2, date,
                                                      self.line_header_light_date)
                            self.sheet.write_string(self.row_pos, 3, sub_line.get('journal_name'),
                                                    self.line_header_light)
                            self.sheet.write_string(self.row_pos, 4, sub_line.get('account_name') or '',
                                                    self.line_header_light)

                            self.sheet.write_number(self.row_pos, 5,
                                                    float(sub_line.get('range_0')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 6,
                                                    float(sub_line.get('range_1')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 7,
                                                    float(sub_line.get('range_2')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 8,
                                                    float(sub_line.get('range_3')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 9,
                                                    float(sub_line.get('range_4')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 10,
                                                    float(sub_line.get('range_5')), self.line_header_light_period)
                            self.sheet.write_number(self.row_pos, 11,
                                                    float(sub_line.get('range_6')), self.line_header_light_period)
                            self.sheet.write_string(self.row_pos, 12,
                                                    '', self.line_header_light_period)

            self.row_pos += 1
            k = 5
