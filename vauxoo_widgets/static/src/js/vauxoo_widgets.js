openerp.vauxoo_widgets = function (instance) {                                                            
var _t = instance.web._t,                                                                           
   _lt = instance.web._lt;                                                                          
var QWeb = instance.web.qweb; 

instance.web.form.FieldCharBS3 = instance.web.form.FieldChar.extend({                                    
    template: 'FieldCharBS3',
    initialize_field: function(){
            this._super()
    }
});  
instance.web.form.FieldEmailBS3 = instance.web.form.FieldEmail.extend({                                    
    template: 'FieldEmailBS3',
});  
instance.web.form.FieldTextBS3 = instance.web.form.FieldText.extend({                                    
    template: 'FieldTextBS3',
});  
instance.web.form.FieldBinaryBS3 = instance.web.form.FieldBinaryFile.extend({                                   
    template: 'FieldBinaryBS3',
});
instance.web.form.widgets.add('FieldCharBS3','instance.web.form.FieldCharBS3');
instance.web.form.widgets.add('FieldEmailBS3','instance.web.form.FieldEmailBS3');
instance.web.form.widgets.add('FieldTextBS3','instance.web.form.FieldTextBS3');
instance.web.form.widgets.add('FieldBinaryBS3','instance.web.form.FieldBinaryBS3');                     
};

