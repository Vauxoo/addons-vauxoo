$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;

    $('form.js_attributes input, form.js_attributes select, form.js_extra_parameters select',oe_website_sale).on('change', function () {
        $(this).closest("form").submit();
    });

});
});
