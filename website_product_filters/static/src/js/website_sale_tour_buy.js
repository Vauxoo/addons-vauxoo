(function () {
    'use strict';
    openerp.Tour.register({
        id:   'shop_buy_product',
        name: "Try to buy products",
        path: '/shop',
        mode: 'test',
        steps: [
            {
                title:  "search ipod",
                element: 'form:has(input[name="search"]) a.a-submit',
                onload: function() {
                    $('input[name="search"]').val("ipod");
                }
            },
            {
                title:     "select ipod",
                element:   '.oe_product_cart a:contains("iPod")',
            },
            {
                title:     "select ipod 32GB",
                waitFor:   '#product_detail',
                element:   'label:contains(32 GB) input',
            },
            {
                title:     "click on add to cart",
                waitFor:   'label:contains(32 GB) input[checked]',
                element:   'form[action^="/shop/cart/update"] .btn',
            },
        ]
    });

}());
