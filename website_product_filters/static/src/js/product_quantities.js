(function() {
    'use strict';

    openerp.website.if_dom_contains('.js_attributes .nav-pills', function(){
        $.ajax({
          url: "/get_prods",
          method: "POST",
          data: { category: $("#products_grid_before li.active").data("categid")},
          beforeSend: function( xhr ) {
            $('span.att-value').after(' <i class="fa fa-spinner fa-spin"></i>');
          }
        }).done(function( data ) {
              $.each(JSON.parse(data), function(i, obj) {
                $('span.att-value#'+obj.id).next().replaceWith('<span class="black-text">('+obj.qty+')</span>');
                $('span.att-value').next('.fa-spinner').replaceWith(' <span class="black-text">(0)</span>');
              });
          $(".js_attributes li.attribute").has("span.black-text:contains('0')").remove();
          $('div.attr-list').each(function(){
            var $div_list = $(this);
            if ($div_list.find('li.attribute').length <= 5) {
                $div_list.find('a.show-more').remove();
              }
            });

          });
    });

}());
