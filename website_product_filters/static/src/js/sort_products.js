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
      $("#product_sorter").change(function() {
          var val = "";
          $("#product_sorter option:selected").each(function() {
            val += $( this ).val();
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
          if (val == 'pasc'){
            $wrapper.find('.oe_product.oe_list.oe_product_cart').sort(function (a, b) {
              return +a.dataset.price - +b.dataset.price;
            }).appendTo( $wrapper );
          }
          if (val == 'pdesc'){
            $wrapper.find('.oe_product.oe_list.oe_product_cart').sort(function (a, b) {
              return +b.dataset.price - +a.dataset.price;
            }).appendTo( $wrapper );
          }
          if (val == 'popularity'){
            $wrapper.find('.oe_product.oe_list.oe_product_cart').sort(function (a, b) {
              return +b.dataset.views - +a.dataset.views;
            }).appendTo( $wrapper );
          }
          if (val == 'hottest'){
            $wrapper.find('.oe_product.oe_list.oe_product_cart').sort(function (a, b) {
              return +b.dataset.hottest - +a.dataset.hottest;
            }).appendTo( $wrapper );
          }
        })
        .trigger( "change" );
        var selected_category = $(".nav.nav-pills.nav-stacked.nav-hierarchy li.active a");
        var breadcrumb = $("#bread_category");
        var brand_selected = $("li.brand.active");
        var ul = $("ul.breadcrumb");
        breadcrumb.html(selected_category.html());
        brand_selected.each(function(){
          console.log(this);
          ul.append("<li class='attr'>"+this.innerHTML+"</li>");

        });

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
