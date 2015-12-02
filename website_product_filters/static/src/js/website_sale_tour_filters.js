(function (){
    'use strict';
    openerp.Tour.register({
        id: 'shop_test_filters',
        name: 'Test Shop With filters',
        path: '/shop',
        mode: 'test',
        steps: [
            {
                title: 'Click on category Computers',
                element: 'i[data-arrowid="2"]',
            },
            {
                title: 'Click on category Devices',
                waitFor: 'a:contains(Devices)',
                element: 'i[data-arrowid="11"]',
            },
            {
                title: 'Click on category Keyboard / Mouse',
                waitFor: 'a:contains("Keyboard / Mouse")',
                element: 'li[data-categid="15"] a:contains("Keyboard / Mouse")',
            },
            {
                title: 'Select 16 GB filter on memory section',
                waitNot: '*[data-name="iPad Mini"],[data-name="iPad Retina Display"]',
                waitFor: '.js_attributes label:contains(16 GB), .js_attributes label:contains(32 GB)',
                element: 'label:contains(16 GB) input',
            },
            {
                title: 'Select price range of 0 to 100 USD',
                waitFor: '.sort_bar h4:contains(16 GB)',
                // waitNot: '(#products_grid div.oe_product_cart").not(":contains(iPod)"',
                element: '.js_attributes input[name=range]input[value=1]',
            },
            {
                title: 'Click on category Computers',
                waitFor: 'a:contains(Computers)',
                element: 'li[data-categid="21"] a:contains("Computers")',
            },
            {
                title: 'Click on category Computer all-in-one',
                waitFor: 'a:contains("Computer all-in-one")',
                element: 'li[data-categid="22"] a:contains("Computer all-in-one")',
            },
            {
                title: 'Filter by 16GB iPad',
                waitFor: '.js_attributes label:contains(16 GB), .js_attributes label:contains(32 GB)',
                element: 'label:contains(16 GB) input',
            },
            {
                title: 'Filter by White value on iPad',
                waitFor: '.sort_bar h4:contains(16 GB)',
                element: '.js_attributes label.css_attribute_color input[value="2-3"]',
            },
            {
                title: 'Test 32GB on iPad',
                waitFor: '.sort_bar h4:contains(White)',
                element: 'label:contains(32 GB) input',
            },
            {
                title: 'Delete 32GB from checkbox list',
                element: '.sort_bar h4:contains(32 GB) a.removable-badge',
            },
        ],
    });

}());
