odoo.define('mrp_additional_costs.mrp_bom_report', function (require) {
'use strict';

var core = require('web.core');
var framework = require('web.framework');
var stock_report_generic = require('stock.stock_report_generic');
var MrpBomReport = require('mrp.mrp_bom_report');

var QWeb = core.qweb;
var _t = core._t;

MrpBomReport.include({

    get_labour_operations: function(event) {
        var self = this;
        var $parent = $(event.currentTarget).closest('tr');
        var activeID = $parent.data('bom-id');
        var qty = $parent.data('qty');
        var level = $parent.data('level') || 0;
        return this._rpc({
              model: 'report.mrp.report_bom_structure',
              method: 'get_labour_operations',
              args: [
                  activeID,
                  parseFloat(qty),
                  level + 1
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    get_overhead_operations: function(event) {
        var self = this;
        var $parent = $(event.currentTarget).closest('tr');
        var activeID = $parent.data('bom-id');
        var qty = $parent.data('qty');
        var level = $parent.data('level') || 0;
        return this._rpc({
              model: 'report.mrp.report_bom_structure',
              method: 'get_overhead_operations',
              args: [
                  activeID,
                  parseFloat(qty),
                  level + 1
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },


})

})