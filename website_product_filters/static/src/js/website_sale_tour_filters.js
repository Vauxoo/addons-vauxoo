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
                element: 'li[data-categid="2"] a',
            },
            {
                title: 'Click on category Devices',
                content: "Here we check if the products on the tree are the right ones to render on popular products",
                waitFor: 'a:contains(Bose Mini Bluetooth Speaker), a:contains(Apple Wireless Keyboard), a:contains(Apple In-Ear Headphones)',
                element: 'li[data-categid="11"] a',
            },
            {
                title: 'Click on category Keyboard / Mouse',
                content: "This step will wait to see if it finds the subcagtegories on the main div of subcategories",
                waitFor: '.subcategories:contains("Keyboard / Mouse"), .subcategories:contains("Screen"), .subcategories:contains("Speakers")',
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
                element: '.js_attributes input[name=range]input[value=1]',
            },
            {
                title: 'Click on category Computers',
                waitFor: 'a:contains(Computers)',
                element: 'ul.breadcrumb li:contains(Computers) a',
            },
            {
                title: 'Click on subcategory Computers',
                waitFor: 'a:contains(Computers)',
                element: '.nav-pills ul a:contains(Computers)',
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
