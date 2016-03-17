$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    $('form.js_attributes select').on('change', function () {
        var $form =$(this).closest("form");
        var search_query = $('.search-query').val();
        var input = $("<input>")
                     .attr("type", "hidden")
                     .attr("name", "search").val(search_query);
        $form.append($(input));
        $form.submit();
    });

});
});
