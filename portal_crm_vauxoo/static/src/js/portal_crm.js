openerp.portal_crm_vauxoo = function (instance) {                                                            
var _t = instance.web._t,                                                                           
   _lt = instance.web._lt;                                                                          
var QWeb = instance.web.qweb; 

instance.web.form.FieldCharBS3 = instance.web.form.FieldChar.extend({                                    
    template: 'FieldCharBS3',
});  
instance.web.form.widgets.add('FieldCharBS3','instance.web.form.FieldCharBS3');
};

