from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval



class InventoryReport(models.TransientModel):
    _name = 'sita_customization.inventory_report_wizard'

    date_from=fields.Date(string="Date From",required=1)
    date_to=fields.Date(string="Date To",required=0)

    def button_export_html(self):
        """
      This function will call the report action direct
       """
        self.ensure_one()
        action=self.env.ref("sita_customization.action_all_inventory_report_html")
        vals=action.read()[0]
        # print("vals",vals)
        context=vals.get("context",{})
        if context:
            context=safe_eval(context)
        model = self.env["report.inventory.report"]
        report = model.create(self._prepare_inventory_report())
        context["active_id"]=report.id
        context["active_ids"]=report.ids

        print("vals after edit", vals)
        context["results"]=report._compute_results()
        vals["context"] = context
        # print("context_url",context)

        return vals


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
        # report._compute_results()
        # print('report',report)
        return report.print_report(report_type)