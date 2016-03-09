(function() {
    'use strict';

    openerp.website.if_dom_contains('.opproducts', function(){
            var max_range =6;
            $( document  ).ready(function() {
                $.post("/get_other_purchased_products",{
                    product_id: $('.product_id').val(),
                    max_product_qty: 12,
                },
                function(data){
                    $('.opproducts').html(data);
                    $('.opproducts').slick({
                          arrows: true,
                          infinite: false,
                            speed: 500
                    });
                });
            });
            $('.opproducts').on('afterChange', function(event, slick, currentSlide){
                var next_slide = currentSlide + 6;
                if(next_slide > max_range){
                    $.post("/get_other_purchased_products",{
                        product_id: $('.product_id').val(),
                        offset: next_slide,
                        max_product_qty: 6,
                    },
                    function(data){
                        if(data){
                            $('.opproducts').slick('slickAdd',data);
                        }
                    });
                    max_range = next_slide;
                }
            });
    });


}());
