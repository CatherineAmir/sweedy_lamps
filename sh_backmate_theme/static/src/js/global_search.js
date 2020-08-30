$(document).ready(function()
{	
	
	$('body').keydown(function(e) {
		if($("body").hasClass("sh_sidebar_background_enterprise")){
			$(".sh_search_container").css("display","block");
			 $(".usermenu_search_input").focus();
			 $(".sh_backmate_theme_appmenu_div").css("opacity","0")
		}
	});
	
});
odoo.define('sh_backmate_theme.GlobalSearch', function (require) {
    "use strict";


    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');    
    var SystrayMenu = require('web.SystrayMenu');
    
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var show_company = false;
    
    
    
    
    session.user_has_group('base.group_multi_company').then(function(has_group) {
    	show_company = has_group
    });

    var GlobalSearch = Widget.extend({
        template: "GlobalSearch",
        events: {
        	 "keydown .sh_search_input input.usermenu_search_input": "_onSearchResultsNavigate",
        	 "click #topbar_search_icon": "_onclick_search_top_bar"
        },
        init: function () {
        	this._search_def = $.Deferred();
            this._super.apply(this, arguments);
            this.show_company = show_company
        },
        _onclick_search_top_bar: function(event){
        	$(".usermenu_search_input").css("display","block");
        },
        _linkInfo: function (key) {
            var original = this._searchableMenus[key];
            return original;
        },
        _getFieldInfo: function (key) {
            key = key.split('|')[1]
            return key;
        },
        _getcompanyInfo: function (key) {
            key = key.split('|')[0]
            return key;
        },
        _checkIsMenu: function (key) {
            key = key.split('|')[0]
            if(key == 'menu'){
            	return true;
            }else{
            	return false;
            }
            
        },
        _searchReset: function () {
            this.$search_container.removeClass("has-results");
            this.$search_results.empty();
            this.$search_input.val("");
        },
       
       
        _searchMenusSchedule: function () {
            this._search_def.reject();
            this._search_def = $.Deferred();
            setTimeout(this._search_def.resolve.bind(this._search_def), 50);
            this._search_def.done(this._searchMenus.bind(this));
        },
        _searchMenus: function () {
            var query = this.$search_input.val();
            if (query === "") {
                this.$search_container.removeClass("has-results");
                $(".sh_backmate_theme_appmenu_div").css("opacity","1");
                this.$search_results.empty();
                return;
            }
            var self = this;
            
            this._rpc({
                model: 'global.search',
                method: 'get_search_result',
                args: [[query]]
            }).then(function(data) {
                if (data) {
                   self._searchableMenus = data
                   
                   var results = fuzzy.filter(query, _.keys(self._searchableMenus), {
//                       pre: "<b>",
//                       post: "</b>",
                   });
                   
                   var results=_.keys(self._searchableMenus)
                   self.$search_container.toggleClass("has-results", Boolean(results.length));
                   console.log("&*",results)
                   if(results.length > 0){
                	   $(".sh_search_results").css("display","block");
                	   self.$search_results.html(QWeb.render("sh_backmate_theme.MenuSearchResults", {
                           results: results,
                           widget: self,
                       }));
                       
                   }else{
                	   $(".sh_backmate_theme_appmenu_div").css("opacity","1");
                	   $(".sh_search_results").css("display","none");
                   }
                   
                   
                }
            });
            
        },
        _onSearchResultsNavigate: function (event) {
        	
        	$(".sh_search_container").css("display","block");
            if (this.$search_results.html().trim() === "") {
                this._searchMenusSchedule();
                return;
            }
            var all = this.$search_results.find(".sh_menu_search_result");
            var key = event.key || String.fromCharCode(event.which);
            var pre_focused = all.filter(".active") || $(all[0]);
            var offset = all.index(pre_focused);
            if (key === "Tab") {
                event.preventDefault();
                key = event.shiftKey ? "ArrowUp" : "ArrowDown";
            }
            switch (key) {
    	        case "ArrowUp":
    	            offset--;
    	            break;
    	        case "ArrowDown":
    	            offset++;
    	            break;
    	        default:
    	        	this._searchMenusSchedule();
                return;
            }
            if (offset < 0) {
                offset = all.length + offset;
            } else if (offset >= all.length) {
                offset -= all.length;
            }
            var new_focused = $(all[offset]);
            pre_focused.removeClass("active");
            new_focused.addClass("active");
            this.$search_results.scrollTo(new_focused, {
                offset: {
                    top: this.$search_results.height() * -0.5,
                },
            });
        },
        start: function () {
        	var self = this;
        	 this._rpc({
                 model: 'sh.back.theme.config.settings',
                 method: 'search_read',
                 domain: [['id','=',1]],
                 fields: ['theme_style']
             }).then(function(data) {
                 if (data) {
                	
                	 self.$search_input = self.$(".sh_search_input input.usermenu_search_input");
                 }
             });
        	  this.$search_container = this.$(".sh_search_container");
              this.$search_results = this.$(".sh_search_results");
            return this._super();
          
        },
      
       
    });

    GlobalSearch.prototype.sequence = 100;
//    session.user_has_group('sh_backmate_theme_adv.group_global_search_mode').then(function(has_group) {
//    	if(has_group){
    		  SystrayMenu.Items.push(GlobalSearch);
//    	}
//    });
  

   return {
	   GlobalSearch: GlobalSearch,
   };
});