//-*- coding: utf-8 -*-
//############################################################################
//
//   Module Writen For Odoo, Open Source Management Solution
//
//   Copyright (c) 2017 Vauxoo - http://www.vauxoo.com
//   All Rights Reserved.
//   info Vauxoo (info@vauxoo.com)
//   coded by: Jose Robles <josemanuel@vauxoo.com>
//
//############################################################################
odoo.define('web.web_widget_json_graph', function (require) {
"use strict";

    var core = require('web.core');
    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var QWeb = core.qweb;

    var JSONGraphWidget = AbstractField.extend({
        template: 'JSONGraph',
        cssLibs: [
        '/web/static/lib/nvd3/nv.d3.css'
    ],
    jsLibs: [
        '/web/static/lib/nvd3/d3.v3.js',
        '/web/static/lib/nvd3/nv.d3.js',
        '/web/static/src/js/libs/nvd3.js'
    ],
        _render: function(){
            var info = JSON.parse(this.value);
            //this.$el.html(QWeb.render('JSONGraph', {}));
            /*jsl:ignore*/
            /*
            Ignoring lint erros caused by nv and d3 variables from NVD3.js
            */
            nv.addGraph(function() {
                var chart = nv.models.lineChart()
                    .useInteractiveGuideline(true);
                chart.xAxis
                    .axisLabel(info.label_x)
                    .tickFormat(d3.format(',r'));

                chart.yAxis
                    .axisLabel(info.label_y)
                    .tickFormat(d3.format('.02f'));

                d3.select('.nv_content svg')
                    .datum(info.data)
                    .transition().duration(500)
                    .call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
            /*jsl:end*/
        },
        _destroy: function () {
            return this._super();
        },
    });
    field_registry.add('json_graph', JSONGraphWidget);

});
