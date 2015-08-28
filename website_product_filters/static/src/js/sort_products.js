(function(){
  'use strict';

  var website = openerp.website;
  website.snippet.animationRegistry.productFilters = website.snippet.Animation.extend({
    selector : ".oe_product.oe_list.oe_product_cart",
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
      console.log("loaded shit");
      $("#product_sorter").change(function() {
          var val = "";
          $("#product_sorter option:selected").each(function() {
            val += $( this ).val();;
          });
          var $wrapper = $('#products_grid');
          if (val == 'rating'){
            $wrapper.find('.oe_product.oe_list.oe_product_cart').sort(function (a, b) {
              return +b.dataset.rating - +a.dataset.rating;
            }).appendTo( $wrapper );
          }
          if (val == 'name')
          {
            $wrapper.find('.oe_product.oe_list.oe_product_cart').sort(function (a, b) {
              return b.dataset.name < a.dataset.name;
            }).appendTo( $wrapper );
          }
        })
        .trigger( "change" );
    },

  })

})();
