(function() {
    'use strict';

    openerp.website.if_dom_contains('#stars_no_edit', function(){
      var $stars = $("span.fa-star-o.no-edit");
      var rating = $("#stars_no_edit").data("rating");
      $stars.each(function(index){
        if (index <= rating-1){
          $(this).removeClass("fa-star-o").addClass("fa-star");
        }
      });

    });

}());
