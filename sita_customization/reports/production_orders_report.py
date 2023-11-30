from odoo import fields, models, api
import logging
_logger=logging.getLogger(__name__)
import time

class ProductionOrderReportsModel(models.TransientModel):
    _name = 'report.production_order.report'
    _description = 'Production Order Inventory'
    date_from = fields.Date(string = "Date From", required = 1)
    date_to = fields.Date(string = "Date To", required = 0)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("planned", "Planned"),
        ("progress", "In Progress"),
        ("to_close", "To Close"),
        ("done", "Done"),
        ("all", "All"),
    ])


    results=[]

    def _compute_results(self   ):

        self.ensure_one()
        date_from = self.date_from
        self.date_to=self.date_to or fields.Date.context_today(self)
        domain=[('date_planned_finished','>=',date_from),
                 ('date_planned_finished','<=',self.date_to)]
        if self.state!='all':
            domain+=[("state",'=',self.state)]

        order_ids=self.env['mrp.production'].search(domain,order="date_planned_finished,name")
        o=tuple(order_ids.ids)
        query="""
        
			select 'header' as type,mrp_order.date_planned_finished,mrp_order.name,product.default_code as product_code ,
            p_temp.name as product_name,'' as components_barcode,'' as components_name,
            0 as components_qty_bom, product_qty as quantity_done, 
            0  as unit_cost, 0 as total_cost,
            mrp_order.state
        
            from mrp_production as mrp_order  
        
            inner join  product_product as product
            on mrp_order.product_id=product.id
        
            inner join product_template as p_temp
            on p_temp.id=product.product_tmpl_id
            where mrp_order.id in %s
            union all
            select  'line' as type,st.date,prod.name,'' as product_code,'' as product_name,product.default_code as components_barcode,p_temp.name as components_name,
             
        
        
         (select mrp_bom_line.product_qty from mrp_bom_line where st.product_id=mrp_bom_line.product_id and 
          mrp_bom_line.bom_id=prod.bom_id limit 1) /(select bom.product_qty from mrp_bom as bom where prod.bom_id=bom.id)
              as components_bom,
              
              
         (select mrp_bom_line.product_qty from mrp_bom_line where st.product_id=mrp_bom_line.product_id and 
          mrp_bom_line.bom_id=prod.bom_id limit 1) /(select bom.product_qty from mrp_bom as bom where prod.bom_id=bom.id) *prod.product_qty
          as components_quantity_done,
          
          sv.unit_cost as unit_cost,
          
          sv.unit_cost*((select mrp_bom_line.product_qty from mrp_bom_line where st.product_id=mrp_bom_line.product_id and 
          mrp_bom_line.bom_id=prod.bom_id limit 1) /(select bom.product_qty from mrp_bom as bom where prod.bom_id=bom.id) *prod.product_qty)  
          as total_cost,
          prod.state
          
        from stock_move as st 
        inner join  product_product as product
        on st.product_id=product.id
        inner join stock_valuation_layer as sv
        on sv.stock_move_id=st.id
        
        
        inner join product_template as p_temp
        on p_temp.id=product.product_tmpl_id
        
        inner join mrp_production as prod
        on prod.id=st.raw_material_production_id
        
        inner join mrp_bom as bom
        on  prod.bom_id =bom.id
        
        inner join mrp_bom_line as bom_line
        on bom.id=bom_line.bom_id
        and bom_line.product_id=st.product_id
        
        where raw_material_production_id in  %s
		
		union 
        
        
        
        select 'value_cost' as type,
        mrp_order.date_planned_finished,
        mrp_order.name,
        
        
        '' as product_barcode,
        '' as product_name,
        'Operation To Consume/Labour Cost By Unit' as
        components_barcode,
        
        
         
        mrp_workcenter.name as components_name,
        
        1 as components_bom,
        
        mrp_workorder.qty_produced,
        mrp_workcenter.labour_cost_by_unit,
        
        
        mrp_workcenter.labour_cost_by_unit * mrp_workorder.qty_produced as labour_cost,
        mrp_order.state
        from mrp_workorder 
        
        right  join  mrp_routing_workcenter as mrp_workcenter
        on mrp_workcenter.id=mrp_workorder.operation_id
        
        inner join mrp_production as mrp_order
        on mrp_order.id=production_id
        
        where production_id in %s
		and mrp_workcenter.labour_cost_by_unit>0
-- 		order by production_id
        
        union 
        select 
        'value_cost' as type,
        mrp_order.date_planned_finished,
        mrp_order.name,
        '' as product_barcode,
        '' as product_name,
        'Operation To Consume/Overhead Cost By Unit' as
        components_barcode,
        
        
         
        mrp_workcenter.name as components_name,
        
        1 as components_bom,
        mrp_workorder.qty_produced,
        
        mrp_workcenter.overhead_cost_by_unit,
        
        
        
        
        mrp_workcenter.overhead_cost_by_unit * mrp_workorder.qty_produced as 
        overhead_cost,mrp_order.state
        
        from mrp_workorder 
        
        full outer join  mrp_routing_workcenter as mrp_workcenter
        on mrp_workcenter.id=mrp_workorder.operation_id
        inner join mrp_production as mrp_order
        on mrp_order.id=production_id
        
        where production_id in %s
								and mrp_workcenter.overhead_cost_by_unit>0
		
								
     
	 order by name, type
	 
    
       

            """
        start = time.time()
        self._cr.execute(query, (o, o,o,o))
        all_order_details = self._cr.dictfetchall()
        end_query = time.time() - start
        _logger.info("query_done number of rows %s", len(all_order_details))
        _logger.info("query_done in %s sec", end_query)
        start_handling = time.time()
        # print("order_dicts",all_order_details[:21])
        all_order_details[0]['total_cost'] = sum(
            [line['total_cost'] if line['total_cost'] else 0 for line in all_order_details[1:]])
        all_order_details[0]['unit_cost'] = round(all_order_details[0]['total_cost']/all_order_details[0]['quantity_done'],3)
        for i in range(0,len(all_order_details)):
            if all_order_details[i]['type']=="header":
                name=all_order_details[i]['name']
                all_order_details[i]['total_cost']=0
                j=i
            else:
                if all_order_details[i]['name']==name and  all_order_details[i]['type'] in ['line','value_cost']:
                    all_order_details[j]['total_cost']+=all_order_details[i]['total_cost']
                    all_order_details[j]['unit_cost']=round(all_order_details[j]['total_cost']/all_order_details[j]['quantity_done'],3)

        return all_order_details


    def print_report(self,report_type="qweb-pdf"):

        self.ensure_one()
        action=(
            report_type=="xlsx"
            and self.env.ref("sita_customization.production_orders_report_xlsx")
            or self.env.ref("sita_customization.production_orders_report_pdf")

        )


        data={
            'report': self.id,
            "date_from":self.date_from,
            "date_to":self.date_to,
            "state":self.state.upper()
        }
        if report_type == "qweb-pdf":
            data["lines"] = self._compute_results()

        return action.report_action(self,config = False,data=data)


    def _get_html(self):
        """
        # this function will render html template

        """
        result={}
        rcontext={}
        report=self.browse(self._context.get("active_id"))

        if report:
            rcontext["o"]=report
            rcontext["results"]=report._compute_results()

            result["html"]=self.env.ref("sita_customization.all_inventory_report_html"
                                        ).render(rcontext)#template_id

            return result


    @api.model

    def get_html(self,given_context=None):
        """
        this function is called by js

        """

        return self.with_context(given_context)._get_html()