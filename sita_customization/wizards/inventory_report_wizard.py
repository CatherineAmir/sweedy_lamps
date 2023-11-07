from odoo import fields, models, api



class InventoryReport(models.TransientModel):
    _name = 'sita_customization.inventory_report_wizard'

    date_from=fields.Date(string="Date From",required=1)
    date_to=fields.Date(string="Date To",required=0)

    def button_export_html(self):
        # TODO
        pass

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)


    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)


    def _prepare_inventory_report(self):
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to or fields.Date.context_today(self),


        }

    def _export(self, report_type):
        # todo
        pass
        model = self.env["report.inventory.report"]
        report = model.create(self._prepare_inventory_report())
        report._compute_results()
        print('report',report)
        # return report.print_report(report_type)