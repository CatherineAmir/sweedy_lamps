from odoo import fields, models, api
from datetime import datetime
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
class SalesAccountReport(models.AbstractModel):
    _name = 'report.sita_customization.sales_account_report_xlsx'
    _inherit='report.report_xlsx.abstract'
    _description = 'Cogs and Profitability Report'

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
            'border': False
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            'align': 'center',
            #'border': True
        })
        self.content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'border': True,
            'text_wrap': True,
        })
        self.content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'bottom': True,
            'bg_color': '#BDBDBD',
            'border': 1,
            'text_wrap':True,
        })
        self.line_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'top': True,
            'font': 'Arial',
            'bottom': True,
            'text_wrap': True,
        })
        self.line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top',
            'border': True,
        })
        self.line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            # 'bg_color': '#BDBDBD',
            'top': True,
            'bottom': True,
            'font': 'Arial',
            'align': 'center',
            'border': True,
        })
        self.line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'bottom': True,
            'text_wrap': True,
            'valign': 'top'
        })
        self.line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
    def _format_float_and_dates(self, currency_id, lang_id):
        self.line_header.num_format = currency_id.excel_format
        self.line_header_light.num_format = currency_id.excel_format
        self.line_header_light_initial.num_format = currency_id.excel_format
        self.line_header_light_ending.num_format = currency_id.excel_format

        self.line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        self.content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
    def generate_xlsx_report(self, workbook, data, record):

        self._define_formats(workbook)
        self.row_pos = 0
        self.record = record  # Wizard object
        self.sheet = workbook.add_worksheet('Production Orders')
        for i in range(0,20):
            # if i in [0,1,6]:
            #     self.sheet.set_column(i, i, 40)
            if i in [x for x in range(3,7)]:
                self.sheet.set_column(i, i, 45)

            else:
                self.sheet.set_column(i, i, 20)
        # todo check this
        self.sheet.freeze_panes(4, 0)
        self.sheet.screen_gridlines = True
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            report_id = data["report"]
            report = self.env['report.sales_account.report'].browse(int(report_id))

            data = report._compute_results()

            # print("in report dataaa",data)


            self.sheet.merge_range(0, 0, 0, 8, 'COGS & Profitability Analysis      ' + 'From {}   To {}'.format(datetime.strptime(str(self.convert_to_date(record.date_from)),"%Y-%m-%d  %H:%M:%S").strftime("%d/%m/%Y"),datetime.strptime(str(self.convert_to_date(record.date_to)),"%Y-%m-%d  %H:%M:%S").strftime("%d/%m/%Y")), self.format_title)
            self.dateformat = self.env.user.lang
            self.prepare_report_contents(data)
    def convert_to_date(self, datestring=False):
        if datestring:
            datestring = fields.Date.from_string(datestring).strftime(self.language_id.date_format)
            return datetime.strptime(datestring, self.language_id.date_format)
        else:
            return False
    def prepare_report_contents(self,data):
        self.row_pos += 3
        headers=[
            "Invoice Number",
            "Invoice Date",
            "Invoice State",
            "Account Code",
            "Account Description",
            "Product Code",
            "Product Name",
            "Partner Name",
            "Partner Tax ID",
            "Sales Peron",
            "Partner PriceList",
            "Product Cost",
            "COGS Per Unit",
            "Invoice Line Unit Price",
            "Invoice Line Quantity",
            "Invoice Line Subtotal",
            "Invoice Line Discount",
            "Invoice Line Total",
            "COGS Total Amount",
            "Profitability",

        ]
        for h in range(0,len(headers)):
            self.sheet.write_string(self.row_pos, h, headers[h],
                                self.format_header)


        for line in data:

            self.row_pos = self.row_pos + 1

            format=self.line_header_light


            self.sheet.write_string(self.row_pos,0,line['move_name']or '',format)
            self.sheet.write_datetime(self.row_pos, 1, self.convert_to_date(line['date']),
                                      self.content_header_date)
            self.sheet.write_string(self.row_pos,2,line['state'].upper() if line['state'] else '',format)
            # todo state
            self.sheet.write_string(self.row_pos,3,line['code'] or '',format)

            self.sheet.write_string(self.row_pos, 4, line['name'] or '', format)
            self.sheet.write_string(self.row_pos, 5, line['default_code'] or '', format)
            self.sheet.write_string(self.row_pos, 6, line['product_name'] or '', format)
            self.sheet.write_string(self.row_pos, 7, line['partner_name'] or '', format)

            self.sheet.write_string(self.row_pos, 8, line['partner_tax_id'] or '', format)
            self.sheet.write_string(self.row_pos, 9, line['sales_person'] or '', format)
            self.sheet.write_string(self.row_pos, 10, line['customer_price_list'] or 0, format)
            self.sheet.write_number(self.row_pos, 11, line['product_cost'] or 0, format)
            self.sheet.write_number(self.row_pos, 12, line['cogs_unit_price'] or 0, format)
            self.sheet.write_number(self.row_pos, 13, line['invoice_line_unit_price'] or 0, format)
            self.sheet.write_number(self.row_pos, 14, line['invoice_line_quantity'] or 0, format)
            self.sheet.write_number(self.row_pos, 15, line['invoice_line_subtotal'] or 0, format)
            self.sheet.write_number(self.row_pos, 16, line['invoice_line_discount'] or 0, format)
            self.sheet.write_number(self.row_pos, 17, line['invoice_line_total'] or 0, format)
            self.sheet.write_number(self.row_pos, 18, line['cogs_total_amount'] or 0, format)
            self.sheet.write_number(self.row_pos, 19, line['profitability'] or 0, format)




            # self.sheet.write_string(self.row_pos, 5, line['components_barcode'] or '', format)
            # self.sheet.write_string(self.row_pos, 6, line['components_name'] or '', format)
            # self.sheet.write_number(self.row_pos, 7, line['components_qty_bom'] , format)
            # self.sheet.write_number(self.row_pos, 8, line['quantity_done'] , format)
            # self.sheet.write_number(self.row_pos, 9, line['unit_cost'], format)
            # self.sheet.write_number(self.row_pos, 10, line['total_cost'], format)
            # self.sheet.write_string(self.row_pos, 11, line['type'], format)


