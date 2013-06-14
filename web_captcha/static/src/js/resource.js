var script = document.createElement("script");
console.log();
script.type = "text/javascript";
script.src = "http://www.google.com/recaptcha/api/js/recaptcha_ajax.js";
$("head").append(script);
openerp.web_captcha = function (openerp)
{
    openerp.web.form.widgets.add('captcha', 'openerp.web.form.CaptchaWidget');
    openerp.web.form.CaptchaWidget = openerp.web.form.FieldChar.extend(
        {
        template : "orp_captcha",
        init: function (view, code) {
            this._super(view, code);
        },
        initialize_content: function() {
            this._super();
        },
        start: function () {
               var ds = new openerp.web.DataSetSearch(null, "res.company");                  
               var reads = ds.read_slice(['recaptcha_key'], {}).then(function(models){
                   Recaptcha.create(models[0].recaptcha_key, "or_recaptcha", {
                       theme: "red",
                       callback: Recaptcha.focus_response_field});
                   });
               var spantotal=$('<span>').addClass('oe_form_field oe_form_field_char oe_luis'); 
               spantotal.appendTo(this.$el);
               return this._super();
          },
        render_value: function() {
                 this._super();
        }
    });

}
