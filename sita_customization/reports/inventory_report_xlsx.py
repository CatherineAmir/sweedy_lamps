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
class InventoryReport(models.AbstractModel):
    _name = 'report.sita_customization.report_inventory_report_xlsx'
    _inherit='report.report_xlsx.abstract'
    _description = 'ALL Inventory Report'

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
            #'top': True,
            #'bottom': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        self.line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            #'top': True,
            #'bottom': True,
            'font': 'Arial',
            'align': 'center',
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

        self.sheet = workbook.add_worksheet('Inventory Report')
        for i in range(0,20):
            if i in [0,1,6]:
                self.sheet.set_column(i, i, 40)
            elif i in [x for x in range(9,18)]:
                self.sheet.set_column(i, i, 10)

            else:
                self.sheet.set_column(i, i, 25)
        # todo check this
        self.sheet.freeze_panes(4, 0)
        self.sheet.screen_gridlines = True
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            data = record._compute_results()


            self.sheet.merge_range(0, 0, 0, 8, 'Total Inventory      ' + 'From {}   To {}'.format(datetime.strptime(str(self.convert_to_date(record.date_from)),"%Y-%m-%d  %H:%M:%S").strftime("%d/%m/%Y"),datetime.strptime(str(self.convert_to_date(record.date_to)),"%Y-%m-%d  %H:%M:%S").strftime("%d/%m/%Y")), self.format_title)
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
            "Product Code",
            "Product Description",
            "Product Category",
            "Product Unit of Measure",
            "Stock Move Date",
            "stock Move Type",
            "stock Move Name",
            "Stock Move Reference",
            "Stock Move Operation type",
            "Opening Quantity",
            "Opening Value",
            "Opening Weighed Average",
            "In Quantity",
            "In Value",
            "Out Quantity",
            "Out Value",
            "Ending Quantity",
            "Ending Value",
            "Ending Weighed Average",
            "type",
        ]
        for h in range(0,len(headers)):
            self.sheet.write_string(self.row_pos, h, headers[h],
                                self.format_header)

        for line in data:
            self.row_pos = self.row_pos + 1
            if line['type']=='header':
                format= self.line_header
                self.sheet.write_string(self.row_pos, 4,'', format)
            else:
                format=self.line_header_light
                self.sheet.write_datetime(self.row_pos, 4, self.convert_to_date(line['move_date']),
                                          self.line_header_light_date)
            self.sheet.write_string(self.row_pos,0,line['product_code'] or '',format)
            self.sheet.write_string(self.row_pos,1,line['product_name']or '',format)
            self.sheet.write_string(self.row_pos,2,line['product_category']or '',format)
            self.sheet.write_string(self.row_pos,3,line['product_uom'] or '',format)



            self.sheet.write_string(self.row_pos, 5, line['picking_code'] or '', format)
            self.sheet.write_string(self.row_pos, 6, line['move_name'] or '', format)
            self.sheet.write_string(self.row_pos, 7, line['move_reference'] or '', format)
            self.sheet.write_string(self.row_pos, 8, line['picking_display_name'] or '', format)
            self.sheet.write_number(self.row_pos, 9, line['opening_quantity'], format)
            self.sheet.write_number(self.row_pos, 10, line['opening_value'], format)
            self.sheet.write_number(self.row_pos, 11, line['opening_weigthed_avg'] or 0, format)
            self.sheet.write_number(self.row_pos, 12, line['in_quantity'], format)
            self.sheet.write_number(self.row_pos, 13, line['in_value'], format)
            self.sheet.write_number(self.row_pos, 14, line['out_quantity'], format)
            self.sheet.write_number(self.row_pos, 15, line['out_value'], format)

            self.sheet.write_number(self.row_pos, 16, line['ending_quantity'], format)
            self.sheet.write_number(self.row_pos, 17, line['ending_value'], format)
            self.sheet.write_number(self.row_pos, 18, line['ending_weigted_avg'], format)
            self.sheet.write_string(self.row_pos, 19, line['type'], format)


