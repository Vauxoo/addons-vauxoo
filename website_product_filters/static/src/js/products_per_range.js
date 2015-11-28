(function() {
    'use strict';

    openerp.website.if_dom_contains('.js_attributes', function(){
        $.ajax({
            url: "/get_ranges",
            method: "POST",
            data: {category: $("#products_grid_before li.active").data("categid")},
            beforeSend: function( xhr ){
                $('.upper').after(' <i class="fa fa-spinner fa-spin"></i>');
               }
            }).done(function( data ){
              console.log(JSON.parse(data));
              $.each(JSON.parse(data), function(i, obj) {
                $('.upper'+obj.id).next().replaceWith('<span class="badge">'+obj.qty+'</span>');
              });
            });
    });

}());
