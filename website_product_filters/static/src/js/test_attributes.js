(function () {
    'use strict';
    var _t = openerp._t;
    var steps = openerp.Tour.tours.shop_customize.steps;
    for (var k=0; k<steps.length; k++) {
        // Inserting extra steps for the pertinent DOM changes made by this module
        if (steps[k].title === "click on 'Product Attribute's Filters'") {
            steps.splice(k+1, 0, {
                title: 'Click On Category "Computers"',
                element: 'li[data-categid="2"] a',
            },
            {
                title: 'Click On Subcategory "Computers"',
                content: "Here we check if the products on the tree are the right ones to render on popular products",
                waitFor: 'b:contains(Computers)',
                element: 'li[data-categid="21"] a',
            },
            {
                title: 'Click On Subcategory "Computer all-in-one"',
                content: "Here we check if the atributes div appears on the DOM",
                element: 'li[data-categid="22"] a',

            }
            );
        }
        if (steps[k].title === "open customize menu bis") {
            steps.splice(k, 1, {
                title: 'Open Customize Menu',
                element: '#customize-menu-button',
            }
            );
        }
        if (steps[k].title === "remove 'Product Attribute's Filters'") {
            steps.splice(k, 1);
        }
        if (steps[k].title === "finish") {
            steps.splice(k, 1, {
                title: 'Finished tour',
            });
        }
    }
    steps = openerp.Tour.tours.shop_buy_product.steps;
    for (k=0; k<steps.length; k++) {
        // Inserting extra steps for the pertinent DOM changes made by this module
        if (steps[k].title === "finish") {
            steps.splice(k, 1);
        }
    }
}());
