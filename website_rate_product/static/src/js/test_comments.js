(function () {
    'use strict';
    var _t = openerp._t;
    openerp.Tour.register({
        id:   'product_test_comments',
        name: "Tests rating on product comments",
        path: '/shop/product/5',
        mode: 'test',
        steps: [
            {
                title:     "open customize menu to allow messages",
                element:   '#customize-menu-button',
            },
            {
                title:     "click on 'Discussion'",
                element:   "#customize-menu a:contains(Discussion)",
            },
            {
                title:     "open customize menu to allow rating",
                waitFor:   "#comment",
                element:   '#customize-menu-button',
            },
            {
                title:     "Click on 'Show Product Rating' to view the current rating of the product if any",
                element:   "#customize-menu a:contains(Show Product Rating)",
            },
            {
                title:     "Put a commentary on the product",
                onload: function (tour) {
                    $("textarea[name='comment']").val("Test comment for rating");
                },
            },
            {
                title:     "Rate with 4 stars the comment",
                element:   "#stars-existing span.fa-star-o",
            },
            {
                title:     "Post the comment with the rating",
                element:   "div a:contains(Post)",
            },
            {
                title:     "Review if the comment has been posted to the product",
                waitFor:   "p:contains(Test comment for rating)",
            },

        ]
    });

}());
