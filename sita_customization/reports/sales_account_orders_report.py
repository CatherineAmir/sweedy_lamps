from odoo import fields, models, api
import logging
_logger=logging.getLogger(__name__)
import time
class salesOrderAccpuntView(models.TransientModel):
    _name='cogs.report.view'
    _description = "Cogs Report View"
    _order='date'

    move_name=fields.Char()
    date=fields.Datetime()
    code=fields.Char()
    name=fields.Char()
    default_code=fields.Char()
    product_name=fields.Char()
    partner_name=fields.Char()
    partner_tax_id=fields.Char()
    sales_person=fields.Char()
    customer_price_list=fields.Char()
    product_cost=fields.Float()
    cogs_unit_price=fields.Float()
    invoice_line_unit_price=fields.Float()
    invoice_line_quantity=fields.Float()
    invoice_line_subtotal=fields.Float()
    invoice_line_discount=fields.Float()
    invoice_line_total=fields.Float()
    cogs_total_amount=fields.Float()
    profitability=fields.Float()
    state=fields.Selection([('draft','Draft'),('posted','Posted'),('cancelled','cancelled')],'State')






class SalesAccountReportsModel(models.TransientModel):
    _name = 'report.sales_account.report'
    _description = 'Sales Account Inventory'
    date_from = fields.Date(string = "Date From", required = 1)
    date_to = fields.Date(string = "Date To", required = 0)
    income_account = fields.Many2many("account.account", string = "Accounts", required = 1,
                                      domain = [('internal_group', '=', 'income')],
                                      default = lambda x: x.id == 8279)



    results=fields.Many2many(comodel_name = 'cogs.report.view',compute='_compute_results', string="Results",help="USe Compute fields in order that nothing is stored in database")
    # left join account_move_line as journal_items
    # on journal_items.move_id=line.move_id and journal_items.account_id in
    #  (select id from  account_account where id in %s)
    #  and journal_items.product_id=line.product_id
    # and journal_items.quantity=line.quantity
    def _compute_results(self   ):

        self.ensure_one()
        date_from = self.date_from
        self.date_to=self.date_to or fields.Date.context_today(self)

        query="""
        select  line.move_name,line.date,account.code,account.name,product.default_code,p_temp.name as product_name,
partner.name as partner_name,partner.vat as partner_tax_id,
user_partner.name as sales_person, product_pricelist.name || '(' || list_currency.name || ')' as customer_price_list,

prop.value_float as product_cost,
(select cASE  WHEN journal_items.DEBIT >0 THEN journal_items.debit ELSE journal_items.CREDIT END/line.quantity  as cogs_unit_price
 from account_move_line  journal_items  where journal_items.move_id=line.move_id and journal_items.account_id =8279

     and journal_items.product_id=line.product_id
     and journal_items.quantity=line.quantity  limit 1 ),

line.price_unit as invoice_line_unit_price,line.quantity as invoice_line_quantity,line.price_subtotal as invoice_line_subtotal,
line.discount as invoice_line_discount,
line.price_total as invoice_line_total ,
(select CASE  WHEN journal_items.DEBIT >0 THEN journal_items.debit ELSE journal_items.CREDIT END  as Cogs_total_amount
 from account_move_line  journal_items  where journal_items.move_id=line.move_id and journal_items.account_id =8279
 
     and journal_items.product_id=line.product_id
     and journal_items.quantity=line.quantity  limit 1 ),


(line.price_subtotal - (select CASE  WHEN journal_items.debit >0 THEN journal_items.debit ELSE journal_items.CREDIT END  
 from account_move_line  journal_items   where journal_items.move_id=line.move_id and journal_items.account_id =8279

     and journal_items.product_id=line.product_id
     and journal_items.quantity=line.quantity  limit 1 )
 )as profitabilitY,


move.state 

from account_move_line as line
inner join account_account as account
on account.id=line.account_id

inner join product_product as product
on
product.id=line.product_id

inner join  product_template as p_temp
on 
product.product_tmpl_id=p_temp.id

right join res_partner as partner
on partner.id=line.partner_id
inner join account_move as move
on line.move_id=move.id

inner join res_users as user_id
on move.invoice_user_id=user_id.id
inner join res_partner as user_partner
on user_id.partner_id=user_partner.id

full outer  join sale_order_line_invoice_rel 
on line.id=sale_order_line_invoice_rel.invoice_line_id

full outer join sale_order_line
on sale_order_line.id=sale_order_line_invoice_rel.order_line_id


full outer join sale_order 
on sale_order_line.order_id=sale_order.id





full outer join  product_pricelist

on 
sale_order.pricelist_id=product_pricelist.id

full outer join res_currency as list_currency
on product_pricelist.currency_id =list_currency.id

full outer join ir_property prop on 
prop.res_id = 'product.product,' || product.id and prop.name='standard_price'

 
where line.account_id in %s and line.quantity!=0 and line.date>=%s and line.date<=%s and move.state='posted'
order by line.date,line.move_name
        
        """
        start=time.time()
        self._cr.execute(query,(tuple(self.income_account.ids),date_from,self.date_to))
        lines = self._cr.dictfetchall()
        end_query = time.time() - start
        _logger.info("query_done number of rows %s", len(lines))
        _logger.info("query_done in %s sec", end_query)
        ReportLine=self.env['cogs.report.view']

        self.results=[ReportLine.new(line).id for line in lines]






    def print_report(self,report_type="qweb-pdf"):

        self.ensure_one()
        action=(
            report_type=="xlsx"
            and self.env.ref("sita_customization.sales_account_report_xlsx")
            or self.env.ref("sita_customization.profitability_report_pdf")

        )

        data={
            'report': self.id,
            "date_from":self.date_from,
            "date_to":self.date_to,
        }
        # if report_type == "qweb-pdf":
            # data["lines"] = self._compute_results()

        return action.report_action(self,config = False,data=data)


    # def _get_html(self):
    #     """
    #     # this function will render html template
    #
    #     """
    #     result={}
    #     rcontext={}
    #     report=self.browse(self._context.get("active_id"))
    #
    #     if report:
    #         rcontext["o"]=report
    #         rcontext["results"]=report._compute_results()
    #
    #         result["html"]=self.env.ref("sita_customization.all_inventory_report_html"
    #                                     ).render(rcontext)#template_id
    #
    #         return result


    # @api.model
    #
    # def get_html(self,given_context=None):
    #     """
    #     this function is called by js
    #
    #     """
    #
    #     return self.with_context(given_context)._get_html()