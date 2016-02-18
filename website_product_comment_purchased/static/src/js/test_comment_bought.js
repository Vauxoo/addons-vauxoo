    (function(){
    'use strict';
    openerp.Tour.register({
        id: 'shop_comment_bought',
        name: 'Shop comment bought',
        path: '/shop?search=ipod',
        mode: 'test',
        steps: [
            {
                title:     'select ipod',
                element:   '.oe_product_cart a:contains("iPod")',
            },
            {
                title:     "write a comment",
                content:   'Before bought the product, write a comment',
                element:   'form[id="comment"] div a:contains(Post)',
                onload: function() {
                    $('textarea[name="comment"]').val("Comments from test");
                }
            },
            {
                title:     'look for a tag "customer bought the item"',
                content:   'Waith Not a comment of the current user logged in, that has the tag "Customer bought the item"',
                waitNot:   'span.label.label-success:contains("Customer bought the item")',
                element:   'label:contains(32 GB) input',
            },
            {
                title:     'click on add to cart on ipod details',
                element:   'form[action^="/shop/cart/update"] .btn',
            },
            {
                title:     'go to checkout',
                element:   'a:contains("Process Checkout")',
            },
            {
                title:     'fill the checkout',
                element:   'form[action="/shop/confirm_order"] .btn:contains("Confirm")',
                onload: function (tour) {
                    $("input[name='name']").val("website_sale-test-shoptest");
                    $("input[name='email']").val("website_sale_test_shoptest@websitesaletest.odoo.com");
                    $("input[name='phone']").val("123");
                    $("input[name='street2']").val("123");
                    $("input[name='city']").val("123");
                    $("input[name='zip']").val("123");
                    $("select[name='country_id']").val("21");
                },
            },
            {
                title:     "select payment",
                element:   '#payment_method label:has(img[title="Wire Transfer"]) input',
            },
            {
                title:     "Pay Now",
                waitFor:   '#payment_method label:has(input:checked):has(img[title="Wire Transfer"])',
                element:   '.oe_sale_acquirer_button .btn[type="submit"]:visible',
            },
            {
                title:     "finish Process",
                waitFor:   '.oe_website_sale:contains("Thank you for your order")',
                element:   'a[href="/shop"]',
            },
            {
                title:     "search ipod",
                element:   'form:has(input[name="search"]) a.a-submit',
                onload: function() {
                    $('input[name="search"]').val("ipod");
                }
            },
            {
                title:     "select ipod",
                element:   '.oe_product_cart a:contains("iPod")',
            },
            {
                title:     "write a comment",
                content:   'After bought the product, write a comment',
                element:   'form[id="comment"] div a:contains(Post)',
                onload: function() {
                    $('textarea[name="comment"]').val("Comments from test");
                }
            },
            {
                title:     'Customer bought the intem ipod',
                content:   'Waith For a comment of the current user logged in, that has the tag "Customer bought the item"',
                waitFor:   'span.label.label-success:contains("Customer bought the item")',
            },
        ],
    });
}());