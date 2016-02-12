(function() {
    'use strict';

    openerp.website.if_dom_contains('#product_with_variants', function(){
        $('.oe_website_sale').on('click', 'input.js_variant_change, select.js_variant_change', function (ev) {
            var $ul = $(this).parents('ul.js_add_cart_variants:first');
            var $parent = $ul.closest('.js_product');
            var variants_str="";
            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                var attr = $(this).attr('title');
                if (typeof attr !== typeof undefined && attr !== false){
                    variants_str += ", " + $(this).attr('title');
                }
                else{
                    variants_str = $(this).next().html();
                }
            });
            var $product_name = $('#product_with_variants').html();
            var index = $product_name.indexOf(",");
            if(index > -1){
                $product_name = $product_name.substring(0,index);
            }
            $('#product_with_variants').html($product_name+", "+variants_str);
        });
        $('input.js_variant_change, select.js_variant_change', this).first().trigger('click');
    });
    openerp.website.if_dom_contains('#no-reviews', function(){
        var comments_qty = $('#comments-list').children().length;
        if (comments_qty > 0){
            var concept = comments_qty >= 2 ? "reviews" : "review";
            $('#no-reviews').text(comments_qty+" "+concept);
        }
        else{
            $('#no-reviews').parent().hide();
        }
    });
}());

