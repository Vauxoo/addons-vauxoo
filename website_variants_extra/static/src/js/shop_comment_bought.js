(function () {
    'use strict';
    var _t = openerp._t;
    var steps = openerp.Tour.tours.shop_comment_bought.steps;
    for (var k=0; k<steps.length; k++) {
        // Inserting extra steps for the pertinent DOM changes made by this module
        if (steps[k].title === "go to checkout") {
            steps.splice(k, 1,
            {
                title:     "go to checkout",
                element:   'a:contains("Proceed to checkout")',
            },
            {
                title:     "click on 'Process checkout' button",
                element:   'a:contains("Process Checkout")',
            }
            );
            break;
        }
    }
    for (var l=0; l<steps.length; l++) {
        if (steps[l].title === "finish Process") {
            steps.splice(l, 1,
            {
                title:     "click Shop",
                waitFor:   '.oe_website_sale:contains("Thank you for your order")',
                element:   'a.dropdown-toggle:contains(Shop)',
            },
            {
                title:     "finish Process",
                element:   'a[href="/shop"]',
            }
            );
            break;
        }
    }
}());
