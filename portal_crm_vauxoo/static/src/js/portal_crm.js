openerp.portal_crm_vauxoo = function (instance) {                                                            
var _t = instance.web._t,                                                                           
   _lt = instance.web._lt;                                                                          
var QWeb = instance.web.qweb; 

instance.web.FormView.include({
    start: function(){
        self = this        
        this._super.apply(this, arguments).done(function () {
            if (typeof self.$(".bs3-footer")[0] != "undefined") {
                var Footer = new instance.portal_news.FooterWeb();
                Footer.appendTo(self.$el);
            } 
        }); 
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

