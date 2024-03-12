from odoo import fields, models, api
import logging
_logger=logging.getLogger(__name__)
import time
class InventoryReportView(models.TransientModel):
    _name='inventory.report.view'
    _description = "Inventory Report View"
    _order='date'
    #TODO all moves must be done
    type=fields.Selection(selection=[
        ('header',"header"),
        ('line','line')
    ],default='line')
    product_id=fields.Many2one(comodel_name = 'product.product')
    product_code=fields.Char()
    product_name=fields.Char()
    # product_category=fields.Many2one(comodel_name = 'product.category',related='product_id.categ_id')
    product_category=fields.Char()
    product_uom=fields.Char()

    move_id=fields.Many2one(comodel_name = 'stock.move')
    move_date = fields.Date()
    move_reference=fields.Char()
    move_display_name=fields.Char()
    move_name = fields.Char()
    picking_display_name=fields.Char()
    picking_type_id=fields.Many2one(comodel_name = 'stock.picking.type')
    picking_code=fields.Selection([
        ('incoming','Receipt'),
        ('outgoing','Delivery'),
        ('internal','Internal Transfer'),
        ('mrp_operation','Manufacturing')
    ])

    # product_uom=fields.Many2one(comodel_name='uom.uom')

    # stock_valuation_value sum of values and sum of
    opening_weigthed_avg=fields.Float()
    opening_quantity=fields.Float()
    opening_value=fields.Float()
    is_initial=fields.Boolean()
    in_quantity=fields.Float()
    in_value=fields.Float()
    out_quantity=fields.Float()
    out_value=fields.Float()


    ending_weigted_avg = fields.Float()
    ending_quantity = fields.Float()
    ending_value = fields.Float()







class InventoryReportsModel(models.TransientModel):
    _name = 'report.inventory.report'
    _description = 'Report Inventory'
    date_from = fields.Date(string = "Date From", required = 1)
    date_to = fields.Date(string = "Date To", required = 0)
    product_ids = fields.Many2many('product.product')
    category_ids = fields.Many2many('product.category')

    results = fields.Many2many(
        comodel_name="inventory.report.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )
    # results=[]

    def _compute_results(self   ):
        start=time.time()

        self.ensure_one()
        date_from = self.date_from
        self.date_to=self.date_to or fields.Date.context_today(self)
        product_ids=self.product_ids
        categ_ids=self.category_ids
        if product_ids and not categ_ids:
            p_ids=product_ids

        elif  categ_ids and not product_ids:
            p_ids =self.env['product.product'].search([('categ_id','in',categ_ids.ids)])
        elif product_ids and categ_ids :
            p_ids=self.env['product.product'].search(['|',('categ_id','in',categ_ids.ids),('id','in',product_ids.ids)])
        else:
            p_ids=self.env['product.product'].search([])



        self._cr.execute("""
            SELECT  Distinct 'header' as type , null::integer as move_id,null::timestamp as move_date,product.id,p_temp.name as product_name,
            product.default_code as product_code,p_cat.name as product_category,
            uom.name as product_uom ,
            '' as move_name,'' as move_reference,''
             as move_display_name,
             '' as picking_display_name,
            null::integer as picking_type_id,
            '' as picking_code,
            
            True as is_initial,
          
           
            case 
            when (select move.id from stock_move move where product_id =product.id and move.state='done' and  CAST(move.date as date)  < %s limit 1) is not null 
            then  (select COALESCE(sum(st_val.quantity ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in
						  (select move.id from stock_move move where product_id =product.id  and move.state='done' and  CAST(move.date as date) 
												  < %s)))
            else 0.0 
            end  as opening_quantity, 
			 case 
            when (select move.id from stock_move move where product_id =product.id and move.state='done' and  CAST(move.date as date)  < %s limit 1) is not null
            then  (select COALESCE(sum(st_val.value ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id =product.id and move.state='done' and  CAST(move.date as date) 
												  < %s)))
				

			
            else 0.0 
            end  as opening_value, 
			
			 case 
            when (select move.id from stock_move move where product_id  =product.id and move.state='done' and  CAST(move.date as date)  < %s limit 1) is not null 
																										  
			then  ((select COALESCE(sum(st_val.value ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id  =product.id and move.state='done' and  CAST(move.date as date) 
												  < %s)))::decimal)/
				  (Case
				  when (select COALESCE(sum(st_val.quantity ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id =product.id and move.state='done' and  CAST(move.date as date) 
												  < %s))) !=0
				  then 
				    (select COALESCE(sum(st_val.quantity ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where  product_id =product.id and move.state='done' and  CAST(move.date as date) 
												  < %s))) 
				  else 1
				  end)
			
			else 1
			end as opening_weigthed_avg,
				  
--           
--             
            0.0 as in_quantity,
            0.0 as in_value,
            0.0 as out_quantity,
            0.0 as out_value,
            0.0 as ending_quantity,
            0.0 as ending_value,
            0.0 as ending_weigted_avg
            
            
            
            
            
           From product_product product 
     
            inner join product_template as p_temp
            on p_temp.id=product.product_tmpl_id
          
            inner join product_category as p_cat
            on p_temp.categ_id=p_cat.id
            inner join uom_uom as uom
            on p_temp.uom_id=uom.id
		   where product.id in (select id from product_product where id in %s)  
            
        
             union all
              SELECT 'line' as type ,move.id as move_id ,move.date as move_date,move.product_id ,
             p_temp.name as product_name,product.default_code as product_code,p_cat.name as product_category,
             uom.name as product_uom ,
            move.name as move_name,move.reference as move_reference,stock_picking.origin||'/'||product.default_code || ': ' ||stock_location_source.name
            || '>' || stock_location_dest.name
             as move_display_name,
              case when picking_type.warehouse_id is not null then stock_warehouse.name || ': '|| picking_type.name else  picking_type.name end as picking_display_name,
            picking_type.id as picking_type_id,
            picking_type.code as picking_code,
            False  as is_initial,
            0 as opening_quantity,
            0 as opening_value,
            0 as opening_weigthed_avg,
             case when st_val.quantity<0 then ABS(st_val.quantity) else 0 end  as out_quantity,
             case when st_val.quantity<0 then ABS(st_val.value) else 0 end  as out_value,
                case when st_val.quantity>0 then st_val.quantity else 0 end  as in_quantity,
                case when st_val.quantity>0 then st_val.value else 0 end as in_value,
            
            0 as ending_quantity,
            0 as ending_value,
            0 as ending_weigted_avg
            
             
             
             from stock_move as move
             Inner Join product_product as product
            on move.product_id=product.id
            inner join product_template as p_temp
            on p_temp.id=product.product_tmpl_id
            inner join product_category as p_cat
            on p_temp.categ_id=p_cat.id
    
            inner join uom_uom as uom
            on move.product_uom=uom.id
              full outer join stock_picking_type as picking_type
            on move.picking_type_id=picking_type.id
            
            full outer join stock_picking
            on move.picking_id=stock_picking.id
            
            full outer join stock_warehouse
            on picking_type.warehouse_id=stock_warehouse.id
            
            
            full outer join stock_location as stock_location_source 
            on stock_location_source.id= move.location_id
            
            full outer join stock_location as stock_location_dest 
            on stock_location_dest.id= move.location_dest_id
            
            full outer Join stock_valuation_layer as st_val
            on move.id=st_val.stock_move_id
            
             where move.state='done' and move.product_id in  (select id from product_product where id in %s) 
              and CAST(move.date as date)  >= %s
              and  CAST(move.date as date)<=%s
               
           GROUP BY product.id,p_temp.name,p_cat.name, product.default_code,p_cat.name, uom.name,move.id,stock_picking.origin,
           stock_location_source.name,stock_location_dest.name,picking_type.warehouse_id,stock_warehouse.name,picking_type.name,picking_type.id,st_val.quantity,
           st_val.value
           order by id,is_initial desc
         
               
            
        """,(
            date_from,date_from,
            date_from,date_from,
            date_from,date_from,

            date_from,date_from,
            tuple(p_ids.ids),
            tuple(p_ids.ids),
            date_from,self.date_to,

        ))
        all_lines=self._cr.dictfetchall()
        end_query=time.time()-start
        _logger.info("query_done number of rows %s",len(all_lines))
        _logger.info("query_done in %s sec",end_query)
        start_handling=time.time()
        print('all_lines[0]',all_lines[0])



        for i in range(0, len(all_lines)):
            if all_lines[i]['type'] == "header":

                id = all_lines[i]['id']
                all_lines[i]['in_value'] =0
                all_lines[i]['out_quantity'] =0
                all_lines[i]['out_value'] = 0
                all_lines[i]['ending_quantity'] = 0
                all_lines[i]['ending_value'] =0
                all_lines[i]['ending_weigted_avg'] = 0

                j = i
            else:
                if all_lines[i]['id'] == id and all_lines[i]['type'] in ['line']:

                    all_lines[j]['in_value'] += all_lines[i]['in_value']
                    all_lines[j]['in_quantity'] += all_lines[i]['in_quantity']

                    all_lines[j]['out_quantity']  += all_lines[i]['out_quantity']
                    all_lines[j]['out_value']  += all_lines[i]['out_value']
                    all_lines[j]['ending_quantity'] = all_lines[j]['opening_quantity'] + \
                                                      all_lines[j]['in_quantity'] - \
                                                      all_lines[j]['out_quantity']
                    all_lines[j]['ending_value'] = all_lines[j]['opening_value'] + \
                                                   all_lines[j]['in_value'] - \
                                                   all_lines[j]['out_value']
                    all_lines[j]['ending_weigted_avg'] = all_lines[j]['ending_value'] / \
                                                         all_lines[j]['ending_quantity'] if all_lines[j][
                        'ending_quantity'] else 1

        end_handling = time.time() - start_handling
        _logger.info("handling done in %s", end_handling)

        ReportLine = self.env["inventory.report.view"]
        self.results = [ReportLine.new(line).id for line in all_lines]
        # print("results",self.results)
        # return all_lines




    def print_report(self,report_type="qweb-pdf"):

        self.ensure_one()
        action=(
            report_type=="xlsx"
            and self.env.ref("sita_customization.inventory_report_xlsx")
            or self.env.ref("sita_customization.inventory_report_pdf")

        )
        # data=self._compute_results()

        data={
            'report':self.id,
            "date_from":self.date_from,
            "date_to":self.date_to,

        }
        # if report_type=="qweb-pdf":
        #     data["lines"]=self._compute_results()
        # print("data",data)

        return action.report_action(self,config = False,data=data)


    def _get_html(self):
        """
        this function will render html template

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