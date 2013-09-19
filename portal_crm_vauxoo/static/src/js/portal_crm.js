openerp.portal_crm_vauxoo = function (instance) {                                                            
var _t = instance.web._t,                                                                           
   _lt = instance.web._lt;                                                                          
var QWeb = instance.web.qweb; 

instance.web.FormView.include({
    start: function(){                                                                          
        this._super.apply(this, arguments); 
        if (this.$('.bs3-footer')) {
            var Footer = new instance.portal_news.FooterWeb();                                         
            Footer.appendTo(this.$el);
       } 
    }
});

instance.web.form.FieldCharBS3 = instance.web.form.FieldChar.extend({                                    
    template: 'FieldCharBS3',
});  
instance.web.form.FieldEmailBS3 = instance.web.form.FieldEmail.extend({                                    
    template: 'FieldEmailBS3',
});  
instance.web.form.FieldTextBS3 = instance.web.form.FieldText.extend({                                    
    template: 'FieldTextBS3',
});  
instance.web.form.widgets.add('FieldCharBS3','instance.web.form.FieldCharBS3');
instance.web.form.widgets.add('FieldEmailBS3','instance.web.form.FieldEmailBS3');
instance.web.form.widgets.add('FieldTextBS3','instance.web.form.FieldTextBS3');
};

