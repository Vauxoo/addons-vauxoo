(function() {
    'use strict';

    openerp.website.if_dom_contains('#no-reviews', function(){
        var form_url = $('#comment').attr('action');
        if(form_url){
            var product_id = form_url.substr(form_url.lastIndexOf('/')+1);
            $.post("/get_comments_qty",{
                product_id: product_id,
            },
            function(data){
                var comments_qty = JSON.parse(data);
                if (comments_qty > 0){
                    var concept = comments_qty >= 2 ? "reviews" : "review";
                    $('#no-reviews').text("Read "+comments_qty+" "+concept);
                }
            });
        }
        else{
            var comments_qty = $('#comments-list').children().length;
            if (comments_qty > 0){
                var concept = comments_qty >= 2 ? "reviews" : "review";
                $('#no-reviews').text("Read "+comments_qty+" "+concept);
            }
        }
    });


}());
