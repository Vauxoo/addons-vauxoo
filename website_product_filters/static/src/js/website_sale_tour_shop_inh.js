(function () {
    'use strict';

    var _t = openerp._t;

    var shop = openerp.Tour.tours.shop.steps;
    /* jshint loopfunc:true */
    for (var r=0; r<shop.length; r++) {
        if (shop[r].title === _t("Create Product")) {
            shop.splice(r, 1,
            {
                waitNot:   '.modal form#editor_new_product input[type=text]:not([value!=""])',
                element:   '.modal button.btn-primary:contains(Continue)',
                placement: 'right',
                title:     _t("Create Product"),
                content:   _t("Click <em>Continue</em> to create the product."),
            }
            );
        break;
        }
    }
    // remove all the steps after step "change the price"
    for (r=0; r<shop.length; r++) {
        if (shop[r].title === _t("Change the price")) {
            shop.splice(r+1, 8);
        break;
        }
    }
}());
