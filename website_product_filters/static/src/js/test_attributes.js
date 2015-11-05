(function () {
    'use strict';
    var _t = openerp._t;
    var steps = openerp.Tour.tours.shop_buy_product.steps;
    for (var k=0; k<steps.length; k++) {
        if (steps[k].title === "click on add to cart") {
            steps.splice(k+1, 0, {
                title:     _t("click in modal on 'Proceed to checkout' button"),
                element:   '.modal a:contains("Proceed to checkout")',
            });
            break;
        }
    }

    openerp.Tour.register({
        id:   'shop_customize',
        name: "Customize the page and search a product",
        path: '/shop',
        mode: 'test',
        steps: [
            {
                title:     "open customize menu",
                element:   '#customize-menu-button',
            },
            {
                title:     "click on 'Product Attribute's Filters'",
                element:   "#customize-menu a:contains(Product Attribute's Filters)",
            },
        ]
    });

}());
