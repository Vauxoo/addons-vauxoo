odoo.define('stock_by_warehouse.warehouse', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var form_common = require('web.AbstractField');
var formats = require('web.field_utils');
var fieldRegistry = require('web.field_registry');
var {EventDispatcherMixin} = require('web.mixins');
var QWeb = core.qweb;
var _t = core._t;

var Locations = Widget.extend(EventDispatcherMixin, {
    init: function (parent, info) {
        this._super(...arguments);
        this.info = info;
    },

    start: function () {
        this._super(...arguments);
        var info = this.info;
        if (info !== false) {
            _.each(info.content, function (k, v) {
                k.index = v;
                k.name = k.warehouse_name;
                k.locations_quantity_formatted = formats.format["integer"](
                    k.locations_available, "", {digits: k.digits});
                k.locations_info = k.info_content;
            });
        }
        var popover = _t('There is no stock available');
        if (info !== false && info.available_locations !== 0) {
            popover = QWeb.render('StockAvailabilityPopOver', {
                'lines': info.content || [],
            });
        }

        var options = {
            content: popover,
            html: true,
            placement: 'right',
            title: info.title || "",
            trigger: 'focus',
            delay: {"show": 0, "hide": 100},
        };
        this.$el.popover(options);
    },
});

var ShowPaymentLineWidget = form_common.extend({
    _render: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.info = JSON.parse(this.value);

        if (this.nodeOptions.by_location){
            this.$el.html(QWeb.render('StockAvailabilityAlert', {
                'locations_available':  formats.format["integer"](
                    self.info.available_locations || 0, this.field, {
                        digits: self.info.digits || 0}),
            }));

            var popover = new Locations(this, this.info);
            popover.attachTo($('.js_available_info'));
        } else{
            this.$el.html(QWeb.render('ShowWarehouseInfo', {
                'show':  formats.format["float"](self.info.warehouse || "", this.field, {digits: self.info.digits || ""})
            }));
            var button = this.$('.js_product_warehouse');
            if (self.info !== false) {
                _.each(self.info.content, function (k, v) {
                    k.index = v;
                    k.available_not_res_formated = formats.format["float"](k.available_not_res, "", {digits: k.digits});
                    k.available_formated  = formats.format["float"](k.available, "", {digits: k.digits});
                    k.incoming_formated  = formats.format["float"](k.incoming, "", {digits: k.digits});
                    k.outgoing_formated  = formats.format["float"](k.outgoing, "", {digits: k.digits});
                    k.virtual_formated  = formats.format["float"](k.virtual, "", {digits: k.digits});
                    k.saleable_formated  = formats.format["float"](k.saleable, "", {digits: k.digits});
                });
            }
            var popover = QWeb.render('ProductWarehousePopOver', {
                'lines': self.info.content || []
            });
            var options = {
                'content': popover,
                'html': true,
                'placement': this.nodeOptions.placement || 'right',
                'title': this.nodeOptions.title || self.info.title || "",
                'trigger': 'focus',
                'delay': { "show": 0, "hide": 100 }
            };
            $(button).popover(options);
        }

    },
});

fieldRegistry.add('warehouse', ShowPaymentLineWidget);

return {
    Locations: Locations,
    ShowPaymentLineWidget: ShowPaymentLineWidget,
};
});
