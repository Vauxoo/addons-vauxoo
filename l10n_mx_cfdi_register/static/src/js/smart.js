openerp.create_openerp_instance = function (instance) {                                                                
var _t = instance.web._t,                                                                              
   _lt = instance.web._lt;                                                                             
var QWeb = instance.web.qweb;

instance.web.form.FieldTextHtmlReadonly = instance.web.form.FieldTextHtml.extend({
    init: function() {                                                              
        this._super.apply(this, arguments);                                     
    },                                                                          
    initialize_content: function() {
        this._super.apply(this, arguments);                                     
    },  
    render_value: function() {                                                                          
        this.$textarea.val(this.get('value') || '');                                                
        this._updating_editor = true;                                                               
        this.$cleditor.updateFrame();                                                               
        this._updating_editor = false;                                                              
        this.$el.html(this.get('value'));                                                           
    }, 
});

instance.web.form.widgets = instance.web.form.widgets.extend({                                      
    'html_readonly' : 'instance.web.form.FieldTextHtmlReadonly',                                                                  
});

}; 
