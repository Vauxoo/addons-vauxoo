(function() {
    'use strict';

    openerp.website.if_dom_contains('.opproducts', function(){
            var max_range =0;
            $( document  ).ready(function() {
                $.post("/get_other_purchased_products",{
                    product_id: $('.product_id').val(),
                    max_product_qty: 7,
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
            $('.opproducts').on('beforeChange', function(event, slick, currentSlide, nextSlide){
                if(nextSlide > max_range){
                    $.post("/get_other_purchased_products",{
                        product_id: $('.product_id').val(),
                        offset: nextSlide + 1,
                        max_product_qty: 6,
                    },
                    function(data){
                        if(data){
                            $('.opproducts').slick('slickAdd',data);
                            $('.opproducts').slick('unslick');
                            $('.opproducts').slick({
                                  arrows: true,
                                  infinite: true,
                                    speed: 500
                            });
                            $('.opproducts').slick('slickPrev');
                        }
                    });
                    max_range = nextSlide;
                }
            });
    });


}());
