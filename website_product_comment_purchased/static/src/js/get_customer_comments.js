(function() {
    'use strict';
    openerp.website.if_dom_contains('div.oe_msg', function(){
        var authors = [];
        $("div.oe_msg").each(function (){
            authors.push($(this).data("author-id"));
        });
        $.ajax({
            url: "/get_customer_purchased",
            method: "POST",
            data: {author_ids: JSON.stringify(authors),
                   product_id: $("div.oe_msg").data('product-id')},
            beforeSend: function( xhr ){
                $(".oe_msg h5.media-heading small span").after(' <i class="fa fa-spinner fa-spin"></i>');
               }
            }).done(function( data ){
              $.each(JSON.parse(data), function(i, obj) {
                $("div.oe_msg").each(function (){
                    if ($(this).data("author-id") == obj.author_id) {
                        $(this).find("i.fa-spinner").replaceWith('<span class="label label-success">Customer bought the item</span>');
                    }
                });
                $("div.oe_msg").find("i.fa-spinner").remove();
              });
        });
    });

}());
