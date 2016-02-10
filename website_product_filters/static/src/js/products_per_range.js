(function() {
    'use strict';

    openerp.website.if_dom_contains('.js_attributes .nav-pills', function(){
        $.ajax({
            url: "/get_ranges",
            method: "POST",
            data: {category: $("#products_grid_before li.active").data("categid")},
            beforeSend: function( xhr ){
                $('.upper').after(' <i class="fa fa-spinner fa-spin"></i>');
               }
            }).done(function( data ){
              $.each(JSON.parse(data), function(i, obj) {
                $('.upper'+obj.id).next().replaceWith('<span class="black-text">('+obj.qty+')</span>');
              });
            $("span.black-text:contains(0)").parents('li.range').remove();
          $('div.range-list').each(function(){
            var $div_list = $(this);
            if ($div_list.find('li.range').length <= 5) {
                $div_list.find('a.show-more').remove();
              }
            });
        });
    });

}());
