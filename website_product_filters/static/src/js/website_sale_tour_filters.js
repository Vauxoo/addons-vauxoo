(function (){
    'use strict';
    openerp.Tour.register({
        id: 'shop_test_filters',
        name: 'Test Shop With filters',
        path: '/shop',
        mode: 'test',
        steps: [
            {
                title: 'Click on category computers Keyboard Mouse',
                element: 'a:contains("Keyboard / Mouse")',
            },
            {
                title: 'Select 16 GB filter on memory section',
                waitNot: '*[data-name="iPad Mini"],[data-name="iPad Retina Display"]',
                waitFor: '.js_attributes',
                element: 'label:contains(16 GB) input',
            },
            {
                title: 'Select price range of 0 to 100 USD',
                waitFor: 'h4:contains(16 GB)',
                waitNot: '*[data-name="Apple Wireless Keyboard"]',
                element: '.js_attributes input[name=range]input[value=1]',
            },
            {
                title: 'Select an iPod',
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
