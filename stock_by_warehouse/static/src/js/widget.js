odoo.define('product.warehouse', function (require) {
"use strict";

var core = require('web.core');
var form_common = require('web.AbstractField');
var formats = require('web.field_utils');
var fieldRegistry = require('web.field_registry');
var QWeb = core.qweb;


var ShowPaymentLineWidget = form_common.extend({
    _render: function() {
        this._super.apply(this, arguments);
        var info = JSON.parse(this.value);
        this.$el.html(QWeb.render('ShowWarehouseInfo', {
            'show':  formats.format["float"](info.warehouse || "", this.field, {digits: info.digits || ""})
        }));
        var button = this.$('.js_product_warehouse');
        if (info !== false) {
            _.each(info.content, function (k, v) {
                k.index = v;
                k.available_not_res = formats.format["float"](k.available_not_res, "", {digits: k.digits});
                k.available = formats.format["float"](k.available, "", {digits: k.digits});
                k.incoming = formats.format["float"](k.incoming, "", {digits: k.digits});
                k.outgoing = formats.format["float"](k.outgoing, "", {digits: k.digits});
                k.virtual = formats.format["float"](k.virtual, "", {digits: k.digits});
                k.saleable = formats.format["float"](k.saleable, "", {digits: k.digits});
            });
        }
        var popover = QWeb.render('ProductWarehousePopOver', {
            'lines': info.content || []
        });
        var options = {
            'content': popover,
            'html': true,
            'placement': this.nodeOptions.placement || 'right',
            'title': this.nodeOptions.title || info.title,
            'trigger': 'focus',
            'delay': { "show": 0, "hide": 100 }
        };
        $(button).popover(options);
    },
});

fieldRegistry.add('warehouse', ShowPaymentLineWidget);
});
