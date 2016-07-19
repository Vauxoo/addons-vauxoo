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
                element:   "form a:contains(Post)",
            },
            {
                title:     "Review if the comment has been posted to the product",
                waitFor:   "p:contains(Test comment for rating)",
                waitNot:   "a#comments:contains(0 comment)",
            },

        ]
    });

}());
