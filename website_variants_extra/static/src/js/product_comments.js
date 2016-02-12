(function() {
    'use strict';

    openerp.website.if_dom_contains('#no-reviews', function(){
        $.post("/get_comments_qty",{
            product_id: $(".product_id").val(),
        },
        function(data){
            var comments_qty = JSON.parse(data);
            if (comments_qty > 0){
                var concept = comments_qty >= 2 ? "reviews" : "review";
                $('#no-reviews').text(comments_qty+" "+concept);
            }
            else{
                $('#no-reviews').parent().hide();
            }
        });
    });


}());
