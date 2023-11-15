from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval



class MrpOrderReport(models.TransientModel):
    _name = 'sita_customization.mrp_order_report_wizard'

    date_from=fields.Date(string="Date From",required=1)
    date_to=fields.Date(string="Date To",required=0)
    state=fields.Selection([
        ("draft","Draft"),
        ("confirmed","Confirmed"),
        ("planned","Planned"),
        ("progress","In Progress"),
        ("to_close","To Close"),
        ("done","Done"),
        ("all","All"),
    ],required=1,default="all")

    def button_export_html(self):
        pass
        # todo
        """
      This function will call the report action direct
       """
        # self.ensure_one()
        # action=self.env.ref("sita_customization.action_all_inventory_report_html")
        # vals=action.read()[0]
        # # print("vals",vals)
        # context=vals.get("context",{})
        # if context:
        #     context=safe_eval(context)
        # model = self.env["report.inventory.report"]
        # report = model.create(self._prepare_inventory_report())
        # context["active_id"]=report.id
        # context["active_ids"]=report.ids
        #
        #
        # context["results"]=report._compute_results()
        # vals["context"] = context
        #
        # return vals


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
            "state":self.state,

        }

    def _export(self, report_type):
        # todo
        pass
        model = self.env["report.production_order.report"]
        report = model.create(self._prepare_inventory_report())
        #
        return report.print_report(report_type)