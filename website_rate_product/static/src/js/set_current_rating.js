(function() {
    'use strict';

    openerp.website.if_dom_contains('#stars_no_edit', function(){
      var $star_groups = $(".stars-no-edit");
      $star_groups.each(function(index){
        var $stars = $(this).find("span"),
            rating = $(this).data("rating");
        $stars.each(function(index){
          if (index <= rating-1){
            $(this).removeClass("fa-star-o").addClass("fa-star");
          }
        });
      });

    });

}());
