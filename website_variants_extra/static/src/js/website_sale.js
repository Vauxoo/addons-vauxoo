$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    console.log('Website.')
    $(oe_website_sale).on('click', 'input.js_variant_change, select.js_variant_change', function (ev) {
        var $ul = $(this).parents('ul.js_add_cart_variants:first');
        var $parent = $ul.closest('.js_product');
        $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
            var $identifier = +$(this).val();
            $('.oe_variant_description').addClass('hidden');
            $('.oe_variant_description_' + $identifier).removeClass('hidden');
        });
    });
    $('ul.js_add_cart_variants', oe_website_sale).each(function () {
        $('input.js_variant_change, select.js_variant_change', this).first().trigger('click');
    });
});
});
