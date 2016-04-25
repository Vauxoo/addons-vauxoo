(function(){
    'use strict';
    openerp.Tour.register({
        id: 'shop_test_product_name_variants',
        name: 'Test Product Name with Variants',
        path: '/shop/product/bose-soundlink-mini-sistema-de-altavoces-recargable-para-iphone-hasta-20-horas-sonido-alto-y-claro-6',
        mode: 'test',
        steps: [
            {
                title:     "select Blue Cover",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(Blue)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                            },
                element:   '.js_add_cart_variants span:contains(Blue)',
            },
            {
                title:     "select Base Charger",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(Base)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                           },
                waitNot:   '.product_header:contains(Yellow)',
                waitFor:  '.product_header:contains(Blue)',
                element:    '.js_add_cart_variants span:contains(Base)',
            },
            {
                title:     "select 200w",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(200w)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                           },
                waitNot:   '.product_header:contains(Wall)',
                waitFor:  '.product_header:contains(Base)',
                element:     '.js_add_cart_variants span:contains(200w)',
            },
            {
                title:     "select Pink Cover",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(Pink)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                            },
                waitFor:   '#product_with_variants:contains(200w)',
                waitNot:   '#product_with_variants:contains(100w)',
                element:     '.js_add_cart_variants span:contains(Pink)',
            },
            {
                title:     "select Wall Charger",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(Wall)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                           },
                waitNot:   '.product_header:contains(Blue Cover)',
                waitFor:  '.product_header:contains(Pink)',
                element:     '.js_add_cart_variants span:contains(Wall)',
            },
            {
                title:     "select 100w",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(100w)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                           },
                waitNot:   '.product_header:contains(Base)',
                waitFor:  '.product_header:contains(Wall)',
                element: '.js_add_cart_variants span:contains(100w)',
            },
            {
                title:     "select Yellow Cover",
                onload:    function(Tour){
                               var $item = $('.js_add_cart_variants span:contains(Blue)');
                               $item.trigger('click');
                               $item.prev().trigger('click');
                            },
                waitFor:   '#product_with_variants:contains(100w)',
                waitNot:   '#product_with_variants:contains(200w)',
                element:    '.js_add_cart_variants span:contains(Blue)',
            },
        ],
    });

}());

