(function() {
    'use strict';

    openerp.website.if_dom_contains('#product_with_variants', function(){
        $('.oe_website_sale').on('click', 'input.js_variant_change, select.js_variant_change', function (ev) {
            var $ul = $(this).parents('ul.js_add_cart_variants:first');
            var $parent = $ul.closest('.js_product');
            var variants_str="";
            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                if($(this).is('input')){
                    var attr = $(this).attr('title');
                    if (typeof attr !== typeof undefined && attr !== false){
                        variants_str += ", " + $(this).attr('title');
                    }
                    else{
                        variants_str += ", "+ $(this).next().html();
                    }
                }
            });
            $('#product_with_variants').html(variants_str);
        });
        $('input.js_variant_change, select.js_variant_change', this).first().trigger('click');
        $('.warehouse-availability').addClass('product_price');
        $('.website-sale-actions').addClass('product_price');
        $('#add_to_cart').addClass('product_price');
        $('.pepdf').click(function(){
            var product_id= $('.product_id').val();
            var url = '/report/pdf/website_variants_extra.pprintable/'+product_id;
            var win = window.open(url, '_blank');
            win.focus();
        });
    });
}());

