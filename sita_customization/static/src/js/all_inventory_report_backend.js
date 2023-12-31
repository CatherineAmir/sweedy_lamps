odoo.define("sita_customization.all_inventory_report",function (require){
    "use strict"; // don't use variable before decalaration

    // to load models
    var AbstractAction=require('web.AbstractAction');
    var core=require('web.core');
    var ReportWidget=require('web.Widget');

    // extend used for inheritance
    var report_backend=AbstractAction.extend({
        hasControlPanel:true,
        events:{
            'click .o_all_inventory_report_print':'print',
            'click .o_all_inventory_report_export':'export',
        },



        init: function (parent,action) {

            this._super.apply(this,arguments); //  super  call the constructor class
            this.actionManager=parent;
            this.given_context={}
            this.odoo_context=action.context;
            this.controller_url=action.context.url;

            if(action.context.context){
                this.given_context=action.context.context;
            }

            this.given_context.active_id=action.context.active_id ||
                action.params.active_id;

            this.given_context.model=action.context.active_model ||false;
            this.given_context.ttype=action.context.ttype ||false;

        },

        willStart: function(){

            // promise.all return a promise when all promises success
            return Promise.all([this._super.apply(this,arguments),this.get_html()])
        },

        set_html:function(){

            var self=this;
            // check what this mean todo
            var def=Promise.resolve();

            if(!this.report_widget){
                this.report_widget=new ReportWidget(
                    this,this.given_context
                );
                def=this.report_widget.appendTo(this.$('.o_content'));

            }
            def.then(function(){
                self.report_widget.$el.html(self.html);
            });

        },
        start:function(){
            this.set_html();
            return this._super();
        },
        // Fetches the html and is perivious report.context if any
        // else create it

        get_html:function() {

            var self = this;
            var defs = [];
            return this._rpc({
                model: this.given_context.model,
                method: 'get_html',// method name in python
                args: [self.given_context],
                context: self.odoo_context,
            }).then(function (result) {

                self.html = result.html;
                defs.push(self.update_cp()); // cp results for control panel
                return $.when.apply($.defs);
            });
        },

    //     update the control pannel
        update_cp:function (){
            if(this.$buttons){
                var status={
                    breadcrumbs:this.actionManager._getBreadcrumbs(),
                    cp_content:{$buttons:this.$button},

                };

                return this._update_control_panel(status);
            }
        },

        do_show:function(){
            this._super();
            this.update_cp();

        },
         // print button js method will print pdf report
        print: function(){
            var self=this;
            this._rpc({
                model:this.given_context.model,
                method:'print_report',
                args:[this.given_context.active_id,'qweb-pdf'],
                context:self.odoo_context,
            }).then(function(result){

                self.do_action(result);
            });
        },
        // export button js method will print excel report
        export:function(){
            var self=this;
            this._rpc({
                model: this.given_context.model,
                method: 'print_report',
                args: [this.given_context.active_id, 'xlsx'],
                context: self.odoo_context,
            }).then(function (result){
                self.do_action(result);
            });



        },

        canBeRemoved:function(){
            return Promise.resolve();
        },


    });



    core.action_registry.add(
        "all_inventory_report",
        report_backend
    );

    return report_backend;



});