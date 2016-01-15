(function () {
    'use strict';
    openerp.Tour.register({
        id:   'shop_buy_product',
        name: "Try to buy products",
        path: '/shop/product/ipod-13',
        mode: 'test',
        steps: [
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
