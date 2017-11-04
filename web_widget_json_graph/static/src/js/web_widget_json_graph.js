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
    var form_common = require('web.form_common');
    var QWeb = core.qweb;

    var JSONGraphWidget = form_common.AbstractField.extend(form_common.ReinitializeFieldMixin, {
        render_value: function(){
            var info = JSON.parse(this.get('value'));
            this.$el.html(QWeb.render('JSONGraph', {}));
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
        destroy: function () {
            return this._super();
        },
    });
    core.form_widget_registry.add('json_graph', JSONGraphWidget);

});
