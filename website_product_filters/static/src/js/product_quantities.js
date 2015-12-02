(function() {
    'use strict';

    openerp.website.if_dom_contains('.js_attributes', function(){
        $.ajax({
          url: "/get_prods",
          method: "POST",
          data: { category: $("#products_grid_before li.active").data("categid")},
          beforeSend: function( xhr ) {
            $('span.att-value').after(' <i class="fa fa-spinner fa-spin"></i>');
          }
        }).done(function( data ) {
              $.each(JSON.parse(data), function(i, obj) {
                $('span.att-value#'+obj.id).next().replaceWith('<span class="badge">'+obj.qty+'</span>');
                $('span.att-value').next('.fa-spinner').replaceWith(' <span class="badge">0</span>');
                // $(".js_attributes li.attribute:contains(0)").remove();
              });
          $(".js_attributes li.attribute").has("span.badge:contains('0')").remove();
          });
    });

}());
