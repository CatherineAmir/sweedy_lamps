odoo.define("sita_customization.all_inventory_report",function (require){
    "use strict"; // don't use variable before decalaration
    console.log("in the js file");
    // to load models
    var AbstractAction=require('web.AbstractAction');
    var core=require('web.core');
    var ReportWidget=require('web.Widget');
    console.log("loading required modules");
    // extend used for inheritance
    var report_backend=AbstractAction.extend({
        hasControlPanel:true,
        events:{
            'click .o_all_inventory_report_print':'print',
            'click .o_all_inventory_report_export':'export',
        },



        init: function (parent,action) {
            console.log("init  of action called");
            console.log("parent arg",parent);
            console.log("action arg",action);
            // console.log("init  of action called")
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
            console.log("this in the end of init",this)
        },

        willStart: function(){
            console.log("calling get_html in js declared down in willStart");
            // promise.all return a promise when all promises success
            return Promise.all([this._super.apply(this,arguments),this.get_html()])
        },

        set_html:function(){
            console.log("in set html");
            var self=this;
            // check what this mean todo
            var def=Promise.resolve();
            console.log('this',this);
            if(!this.report_widget){
                this.report_widget=new ReportWidget(
                    this,this.given_context
                );
                def=this.report_widget.appendTo(this.$('.o_content'));
                console.log("def >>>",def);
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
            console.log("in get_html_js");
            var self = this;
            var defs = [];
            return this._rpc({
                model: this.given_context.model,
                method: 'get_html',// method name in python
                args: [self.given_context],
                context: self.odoo_context,
            }).then(function (result) {
                console.log("result in this._rpc function".result);
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
                console.log(" in update_cp",status);
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
                console.log("in print do action result",result);
                self.do_action(result);
            });
        },
        // export button js method will print excel report
        export:function(){
            var self=this;
            this._rpc({
                model: this.given_context.model,
                method: 'print_report',
                agrs: [this.given_context.active_id, 'xlsx'],
                context: self.odoo_context,
            }).then(function (result){
                self.do_action(result);
            });



        },

        canBeRemoved:function(){
            return Promise.resolve();
        },


    });

    console.log("report_backend extended")

    core.action_registry.add(
        "all_inventory_report",
        report_backend
    );
    console.log("all_inventory_report_added to backend");
    return report_backend;



});