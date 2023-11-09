from odoo import fields, models, api


class InventoryReportView(models.TransientModel):
    _name='inventory.report.view'
    _description = "Inventory Report View"
    _order='date'
    #TODO all moves must be done
    line_type=fields.Selection(selection=[
        ('header',"header"),
        ('line','line')
    ],default='line')
    product_id=fields.Many2one(comodel_name = 'product.product')
    product_code=fields.Char()
    product_name=fields.Char()
    product_category=fields.Many2one(comodel_name = 'product.category',related='product_id.categ_id')

    move_id=fields.Many2one(comodel_name = 'stock.move')
    move_date = fields.Date()
    move_reference=fields.Char()
    move_display_name=fields.Char()
    picking_display_name=fields.Char()
    picking_type_id=fields.Many2one(comodel_name = 'stock.picking.type')
    picking_code=fields.Selection([
        ('incoming','Receipt'),
        ('outgoing','Delivery'),
        ('internal','Internal Transfer'),
        ('mrp_operation','Manufacturing')
    ])
    account_move_id=fields.Many2one(comodel_name = 'account.move')
    account_move_ref=fields.Char()
    product_uom=fields.Many2one(comodel_name='uom.uom')

    # stock_valuation_value sum of values and sum of
    opening_weighted_average=fields.Float()
    opening_quantity=fields.Float()
    opening_value=fields.Float()

    in_quantity=fields.Float()
    in_value=fields.Float()
    out_quantity=fields.Float()
    out_value=fields.Float()


    ending_weighted_average = fields.Float()
    ending_quantity = fields.Float()
    ending_value = fields.Float()







class InventoryReportsModel(models.TransientModel):
    _name = 'report.inventory.report'
    _description = 'Report Inventory'
    date_from = fields.Date(string = "Date From", required = 1)
    date_to = fields.Date(string = "Date To", required = 0)

    # results = fields.Many2many(
    #     comodel_name="inventory.report.view",
    #     compute="_compute_results",
    #     help="Use compute fields, so there is nothing store in database",
    # )
    results=[]

    def _compute_results(self   ):

        self.ensure_one()
        date_from = self.date_from
        self.date_to=self.date_to or fields.Date.context_today(self)
        product_dicts={}
        product_ids=self.env['product.product'].search([])
        results=[]
        for p in product_ids.ids:
            # print('p',p)
            product_dicts.update({
                str(p):{
                    'header':{},
                    'lines':[],

                },
            })
            # inital
            # old
        #     self._cr.execute(
        #     """
        #     SELECT 'header' as type ,'' as move_id,'' as move_date,product.id,p_temp.name as product_name,
        #     product.default_code as product_code,p_cat.name as product_category,
        #     uom.name as product_uom ,
        #     '' as move_name,'' as move_reference,''
        #      as move_display_name,
        #      '' as picking_display_name,
        #     '' as picking_type_id,
        #     '' as picking_code,
        #
        #     True as is_initial,
        #
        #
        #     case
        #     when move.state='done' and  CAST(move.date as date)  < %s
        #     then  COALESCE(sum(st_val.quantity ),0.0)
        #     else 0.0
        #     end  as opening_quantity,
        #
        #     case
        #     when move.state='done' and  CAST(move.date as date)  < %s
        #     then  COALESCE(sum( st_val.value ),0.0)
        #     else 0.0
        #     end  as opening_value,
        #
        #     case
        #         when move.state='done' and  CAST(move.date as date)  < %s
        #     then
        #         sum(st_val.value::decimal )/
        #         Case
        #             when COALESCE(sum(st_val.quantity),0) >0
        #                 then sum(st_val.quantity) else 1
        #         end
        #
        #
        #     else 0.0
        #     end  as opening_weigthed_avg,
        #    /*
        #     0.0 as opening_quantity,
        #     0.0 as opening_value,
        #     0.0 as opening_weigthed_avg,
        #     */
        #     0.0 as in_quantity,
        #     0.0 as in_value,
        #     0.0 as out_quantity,
        #     0.0 as out_value,
        #     0.0 as ending_quantity,
        #     0.0 as ending_value,
        #     0.0 as ending_weigted_avg
        #
        #
        #
        #
        #
        #    From product_product product
        #
        #    FULL  join stock_move as move
        #    on product.id =move.product_id
        #
        #   Full outer join stock_valuation_layer as st_val
        #     on move.id=st_val.stock_move_id
        #
        #
        #     inner join product_template as p_temp
        #     on p_temp.id=product.product_tmpl_id
        #
        #     inner join product_category as p_cat
        #     on p_temp.categ_id=p_cat.id
        #
        #     inner join uom_uom as uom
        #     on p_temp.uom_id=uom.id
        #     where product.id = %s
        #
        #
        #      GROUP BY product.id,p_temp.name,p_cat.name, product.default_code,p_cat.name, uom.name,
        #       move.state,move.date
        #     ORDER BY product.id
        #    /* move.date,move.Reference*/
        #
        #
        #
        #
        #
        # """,(
        #         date_from,
        #         date_from,
        #         date_from,
        #         p,
        #
        #
        #     ),
        # )

            self._cr.execute("""
            SELECT  Distinct 'header' as type , '' as move_id,''as move_date,product.id,p_temp.name as product_name,
            product.default_code as product_code,p_cat.name as product_category,
            uom.name as product_uom ,
            '' as move_name,'' as move_reference,''
             as move_display_name,
             '' as picking_display_name,
            '' as picking_type_id,
            '' as picking_code,
            
            True as is_initial,
          
           
            case 
            when (select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date)  < %s limit 1) is not null 
            then  (select COALESCE(sum(st_val.quantity ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in
						  (select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date) 
												  < %s)))
            else 0.0 
            end  as opening_quantity, 
			 case 
            when (select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date)  < %s limit 1) is not null
            then  (select COALESCE(sum(st_val.value ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date) 
												  < %s)))
				

			
            else 0.0 
            end  as opening_value, 
			
			 case 
            when (select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date)  < %s limit 1) is not null 
																										  
			then  ((select COALESCE(sum(st_val.value ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date) 
												  < %s)))::decimal)/
				  (Case
				  when (select COALESCE(sum(st_val.quantity ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date) 
												  < %s))) !=0
				  then 
				    (select COALESCE(sum(st_val.quantity ),0.0) from stock_valuation_layer as st_val 
				   where (st_val.stock_move_id in(select move.id from stock_move move where product_id=%s and move.state='done' and  CAST(move.date as date) 
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
           
		   where product.id = %s 
            
           
             GROUP BY product.id,p_temp.name,p_cat.name, product.default_code,p_cat.name, uom.name

            ORDER BY product.id 
            """,(
                p,date_from,p,date_from,
                p,date_from,p,date_from,
                p,date_from,p,date_from,
                p,date_from,p,date_from,
                p

            ))
            initial_lines=self._cr.dictfetchall()
            # print("length of headers",len(initial_lines))
            # print('initial_line', initial_lines)

            # if len(initial_lines)

            product_dicts[str(p)]['header']=initial_lines[0]
            # print( 'initial_line',product_dicts)


            # multilines
            # TOdo query parameters

    #         query= """
    #             SELECT 'line' as type ,move.id as move_id,
    #
    #             move.date as move_date,move.product_id,p_temp.name as product_name,
    #             product.default_code as product_code,p_cat.name as product_category
    #             /*
    #             uom.name as product_uom,move.name,move.reference as move_reference,stock_picking.origin||'/'||product.default_code || ': ' ||stock_location_source.name
    #             || '>' || stock_location_dest.name
    #              as move_display_name
    #             ,case when picking_type.warehouse_id is not null then stock_warehouse.name || ': '|| picking_type.name else  picking_type.name end as picking_display_name,
    #             picking_type.id as picking_type_id,
    #             picking_type.code as picking_code,
    #             False as is_inial,
    #             case when st_val.quantity<0 then ABS(st_val.quantity) else 0 end  as out_quantity,
    #             case when st_val.quantity<0 then ABS(st_val.value) else 0 end  as out_value,
    #             case when st_val.quantity>0 then st_val.quantity else 0 end  as in_quantity,
    #             case when st_val.quantity>0 then st_val.value else 0 end as in_value
    #
    #             From stock_move move
    #             /*
    #             Inner Join stock_valuation_layer as st_val
    #             on move.id=st_val.stock_move_id
    #   */
    #             Inner Join product_product as product
    #             on move.product_id=product.id
    #               */
    #             inner join product_template as p_temp
    #             on p_temp.id=product.product_tmpl_id
    #             inner join product_category as p_cat
    #             on p_temp.categ_id=p_cat.id
    # /*
    #             inner join uom_uom as uom
    #             on move.product_uom=uom.id
    #             inner join stock_picking_type as picking_type
    #             on move.picking_type_id=picking_type.id
    #
    #             inner join stock_picking
    #             on move.picking_id=stock_picking.id
    #
    #             inner join stock_warehouse
    #             on picking_type.warehouse_id=stock_warehouse.id
    #
    #
    #             inner join stock_location as stock_location_source
    #             on stock_location_source.id= move.location_id
    #
    #             inner join stock_location as stock_location_dest
    #             on stock_location_dest.id= move.location_dest_id
    #             */
    #             where move.product_id = %s
    #
    #
    #            /*
    #             move.state='done' and
    #              and CAST(move.date as date)  >= %s;
    #              and move.product_id = %s
    #             >=%s and  CAST(move.date as date)<=%s and product.id=%s
    #             ORDER By move.date limit 5
    #         */
    #
    #
    #
    #
    #
    #
    #            /* move.date,move.Reference*/
    #        """
            query2="""
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
            0 as ending_quantity,
            0 as ending_value,
            0 as ending_weigted_avg,
            
              case when st_val.quantity<0 then ABS(st_val.quantity) else 0 end  as out_quantity,
             case when st_val.quantity<0 then ABS(st_val.value) else 0 end  as out_value,
                case when st_val.quantity>0 then st_val.quantity else 0 end  as in_quantity,
                case when st_val.quantity>0 then st_val.value else 0 end as in_value
             
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
            
             where move.state='done' and move.product_id=%s
              and CAST(move.date as date)  >= %s
              and  CAST(move.date as date)<=%s
              ORDER BY move.date
             
        
            """
            # print((p,))
            self._cr.execute(query2,(p,date_from,self.date_to))

            # self._cr.execute(query,(str(p),))



            product_stock_moves_lines=self._cr.dictfetchall()
            # print('product_stock_moves_lines',product_stock_moves_lines)

            # print("[ line ['in_quantity'] if line ['in_quantity']!=None else  0 for line in product_stock_moves_lines]",[ line ['in_quantity'] if line ['in_quantity']!=None else  0 for line in product_stock_moves_lines])
            # print(product_dicts[str(p)]['header'])
            if len(product_stock_moves_lines):
                try:
                    product_dicts[str(p)]['header']['in_quantity']=sum([ line ['in_quantity'] if line ['in_quantity']!=None else  0 for line in product_stock_moves_lines])
                except Exception as e:
                    print(" error",e)
                    # print("product_dicts[str(p)]['header']['in_quantity']",product_dicts[str(p)]['header']['in_quantity'])
                    # print("[ line ['in_quantity'] if line ['in_quantity']!=None else  0 for line in product_stock_moves_lines]",[ line ['in_quantity'] if line ['in_quantity']!=None else  0 for line in product_stock_moves_lines])

                product_dicts[str(p)]['header']['in_value']=sum([ line ['in_value']  if  line ['in_value'] else 0 for line in product_stock_moves_lines])
                product_dicts[str(p)]['header']['out_quantity']=sum([ line ['out_quantity'] if  line ['out_quantity'] else 0 for line in product_stock_moves_lines])
                product_dicts[str(p)]['header']['out_value']=sum([ line ['out_value']if line ['out_value'] else 0 for line in product_stock_moves_lines])
                product_dicts[str(p)]['header']['ending_quantity']=product_dicts[str(p)]['header']['opening_quantity']+product_dicts[str(p)]['header']['in_quantity']- product_dicts[str(p)]['header']['out_quantity']
                product_dicts[str(p)]['header']['ending_value']=product_dicts[str(p)]['header']['opening_value']+product_dicts[str(p)]['header']['in_value']- product_dicts[str(p)]['header']['out_value']
                product_dicts[str(p)]['header']['ending_weigted_avg']= product_dicts[str(p)]['header']['ending_value']/product_dicts[str(p)]['header']['ending_quantity'] if product_dicts[str(p)]['header']['ending_quantity'] else 1


                # print('lines',product_stock_moves_lines)
            product_dicts[str(p)]['lines']=product_stock_moves_lines
            results.append( product_dicts[str(p)]['header'])

            results=results+product_stock_moves_lines

        return results




    def print_report(self,report_type="qweb"):
        # report_type=qweb this is a default
        self.ensure_one()
        action=(
            report_type=="xlsx"
            and self.env.ref("sita_customization.inventory_report_xlsx")
            or self.env.ref("sita_customization.inventory_report_pdf")

        )
        data=self._compute_results()
        print("data",data)
        data={
            'lines':data
        }
        # todo one call for compute
        return action.report_action(self,config = False,data=data)


    def _get_html(self):
        """
        this function will render html template

        """
        result={}
        rcontext={}
        report=self.browse(self._context.get("active_id"))
        print(report)
        if report:
            rcontext["o"]=report
            print("rcontext",rcontext)
            result["html"]=self.env.ref("sita_customization.all_inventory_report_xml"
                                        ).render(rcontext)#template_id
            # todo


    @api.model

    def get_html(self,given_context=None):
        """
        this function is called by js

        """
        print("given context")
        return self.with_context(given_context)._get_html()