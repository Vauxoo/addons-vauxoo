(function (){
    'use strict';
    openerp.Tour.register({
        id: 'shop_test_filters',
        name: 'Test Shop With filters',
        path: '/shop',
        mode: 'test',
        steps: [
            {
                title: 'Click on category computers all-in-one',
                element: 'a:contains("Computer all-in-one")',
            },
            {
                title: 'Select 16 GB filter on memory section',
                waitFor: 'form.js_attributes',
                element: 'form.js_attributes label:contains(16 GB) input',
            },
            {
                title: 'Select price range of 0 to 100 USD',
                waitFor: 'h4:contains(16 GB)',
                element: '.js_attributes input[name=range]input[value=1]',
            },
            {
                title: 'Select an iPod',
                waitNot: '*[data-name="iPad Retina Display"],[data-name="iMac"]',
                element: '.oe_product_cart a:contains("iPod")',
            },
            {
                title:     "Select ipod 32GB Radio Button",
                waitFor:   '#product_detail',
                element:   'label:contains(32 GB) input',
            },
            {
                title:     "Click on add to cart",
                waitFor:   'label:contains(32 GB) input[checked]',
                element:   'form[action^="/shop/cart/update"] .btn',
            },
        ],
    });

}());
