(function (){
    'use strict';
    openerp.website.if_dom_contains('.sort_bar', function(){
        $('.removable-badge').click(function(ev) {
            ev.preventDefault();
            var $element = jQuery(this);
            var value_id = $element.data('attrvalue');
            var unknown_id = $element.data('attr-unknown');
            $element.parents("h4").remove();
            if (value_id) {
                $('.att-value#'+value_id).trigger('click');
            }
            if (unknown_id) {
                $(".att-unknown[data-id='"+unknown_id+"']").trigger('click');
            }
        });
    });
}());
