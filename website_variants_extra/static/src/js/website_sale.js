$(document).ready(function () {
    /**
    This will be in a web module to be able to use in 100% of odoo.
    source: https://css-tricks.com/snippets/jquery/smooth-scrolling/
    */
    $(function() {
      $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
          var target = $(this.hash);
          target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
          if (target.length) {
            $('html,body').animate({
              scrollTop: target.offset().top
            }, 1000);
            return false;
          }
        }
      });
    });
    /**
    Until here:
    */
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    /**
    Set on click event to set the descriptions and update the 'Actual Configuration' space.
    */
    $(oe_website_sale).on('click', 'input.js_variant_change, select.js_variant_change', function (ev) {
        var $ul = $(this).parents('ul.js_add_cart_variants:first');
        var $parent = $ul.closest('.js_product');
        /**
        Selected all what is checked.
        # TODO: IT IS WORKING ONLY IN THE LAST ONE, IT SHOULD WORK OF EVERY COMBINATION
        */
        $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
            var $identifier = +$(this).val();
            $('.oe_variant_description').addClass('hidden');
            $('.oe_variant_description_' + $identifier).removeClass('hidden');
        });
    });
    /**
    Triggering the click to call the behavior when page is just load
    */
    $('ul.js_add_cart_variants', oe_website_sale).each(function () {
        $('input.js_variant_change, select.js_variant_change', this).first().trigger('click');
    });
});
});
