(function () {
    'use strict';

    var _t = openerp._t;
    var website = openerp.website;
    website.ready().done(function() {
    openerp.Tour.register({
        id: 'shop',
        name: _t("Create a product"),
        steps: [
            {
                title:     _t("Welcome to your shop"),
                content:   _t("You successfully installed the e-commerce. This guide will help you to create your product and promote your sales."),
                popover:   { next: _t("Start Tutorial"), end: _t("Skip It") },
            },
            {
                element:   '#content-menu-button',
                placement: 'left',
                title:     _t("Create your first product"),
                content:   _t("Click here to add a new product."),
                popover:   { fixed: true },
            },
            {
                element:   'a[data-action=new_product]',
                placement: 'left',
                title:     _t("Create a new product"),
                content:   _t("Select 'New Product' to create it and manage its properties to boost your sales."),
                popover:   { fixed: true },
            },
            {
                element:   '.modal #editor_new_product input[type=text]',
                sampleText: 'New Product',
                placement: 'right',
                title:     _t("Choose name"),
                content:   _t("Enter a name for your new product then click 'Continue'."),
            },
            {
                waitNot:   '.modal input[type=text]:not([value!=""])',
                element:   '.modal button.btn-primary',
                placement: 'right',
                title:     _t("Create Product"),
                content:   _t("Click <em>Continue</em> to create the product."),
            },
            {
                waitFor:   'body:has(button[data-action=save]:visible):has(.js_sale)',
                title:     _t("New product created"),
                content:   _t("This page contains all the information related to the new product."),
                popover:   { next: _t("Continue") },
            },
            {
                element:   '.product_price .oe_currency_value:visible',
                sampleText: '20.50',
                placement: 'left',
                title:     _t("Change the price"),
                content:   _t("Edit the price of this product by clicking on the amount."),
            },
        ]
    });
    });

}());
