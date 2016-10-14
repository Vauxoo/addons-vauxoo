odoo.define('pos_disable_customer.pos_disable_customer', function (require){
"use strict";

var screens = require('point_of_sale.screens');

    screens.ClientListScreenWidget.include({
        renderElement: function(){
            this._super();
            this.$('.new-customer').hide();
        }
    });

});
