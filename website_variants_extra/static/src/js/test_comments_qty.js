(function(){
    'use strict';
    openerp.Tour.register({
        id: 'shop_test_comment_qty',
        name: 'Test Product Name with Variants',
        path: '/shop/product/bose-soundlink-mini-sistema-de-altavoces-recargable-para-iphone-hasta-20-horas-sonido-alto-y-claro-6',
        mode: 'test',
        steps: [
            {
                title: 'check comment qty',
                waitFor: '#no-reviews:contains(4)',
                element: '#no-reviews',
            },
            {
                title:     "Write first comment",
                onload:    function(Tour){
                            $('#comment textarea').text('1st Phantom Comment');
                               $('#comment .fa-star-o:last').trigger('click');
                            },
                element:  'form a:contains(Post)',
            },
            {
                title:     "Publish a comment",
                onload:    function(Tour){
                                $('#comments-list .btn-danger').first().trigger('click');
                           },
                waitFor:   '#comments-list:first:contains(1st)',
                element:   '#comments-list',
            },
            {
                title:     "Redact second comment",
                onload:    function(Tour){
                            $('#comment textarea').text('2nd Phantom Comment');
                               $('#comment .fa-star-o:last').trigger('click');
                            },
                waitFor:   '#comments-list:first:contains(1st)',
            },
            {
                title:     "Post second comment",
                element:   'form a:contains(Post)',
                onload:    function(Tour){
                            $('form a:contains(Post)').trigger('click');
                            },
            },
            {
                title: 'check comment qty',
                waitFor: '#no-reviews:contains(5)',
            },
            {
                title:     "Publish second comment",
                onload:    function(Tour){
                                $('#comments-list .btn-danger').first().trigger('click');
                           },
                waitFor:   '#comments-list li:first:contains(2nd)',
                element:   '#comments-list',
            },
            {
                title:     "Post Not published comment",
                onload:    function(Tour){
                            $('#comment textarea').text('3rd Phantom Comment');
                               $('#comment .fa-star-o:last').trigger('click');
                            },
                waitFor:   '#comments-list:first:contains(2nd)',
                element:  'form a:contains(Post)',
            },
            {
                title: 'check comment qty',
                waitFor: '#no-reviews:contains(6)',
                element: '#no-reviews',
            },
        ],
    });

}());

