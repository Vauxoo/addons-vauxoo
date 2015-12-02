(function (){
    'use strict';
    openerp.website.if_dom_contains('.sort_bar', function(){
        $('.removable-badge').click(function(ev) {
            ev.preventDefault();
            var $element = jQuery(this);
            var value_id = $element.data('attrvalue');
            $element.parents("h4").remove();
            $('.att-value#'+value_id).trigger('click');
        });
    });
}());
