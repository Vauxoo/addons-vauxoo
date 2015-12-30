(function(){
  'use strict';

  var website = openerp.website;
  website.snippet.animationRegistry.collapsible_categories = website.snippet.Animation.extend({
    selector : "#o_shop_collapse_category",
    start: function(){
      this.redrow();
    },
    // stop: function(){
    //   this.clean();
    // },

    redrow: function(debug){
      // this.clean(debug);
      this.build(debug);
    },

    // clean:function(debug){
    //   this.$target.empty();
    // },

    build: function(debug){
        if(!$('#o_shop_collapse_category, .oe_website_sale').length) {
          return $.Deferred().reject("DOM doesn't contain '#o_shop_collapse_category, .oe_website_sale'");
        }

        $('#o_shop_collapse_category').on('click', '.fa-chevron-right',function(){
          $(this).parent().siblings().find('.fa-chevron-down:first').click();
          $(this).parents('li').find('ul:first').show('normal');
          $(this).toggleClass('fa-chevron-down fa-chevron-right');
        });

        $('#o_shop_collapse_category').on('click', '.fa-chevron-down',function(){

          $(this).parent().find('ul:first').hide('normal');
          $(this).toggleClass('fa-chevron-down fa-chevron-right');
        });
    },

  });

})();
