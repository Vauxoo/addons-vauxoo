(function () {
    'use strict';

    var website = openerp.website;
    openerp.jsonRpc('/website/get_public_id', 'call', {                                                                        
                    'object': 'res.users',                                         
            }).then( function(res_id) {                                          
       Recaptcha.create(res_id, "oerp_recaptcha", {
       theme: "clean",
       });
   });

}());
