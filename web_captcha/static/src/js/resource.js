var script = document.createElement("script");
script.type = "text/javascript";
script.src = "https://www.google.com/recaptcha/api/js/recaptcha_ajax.js";
$("head").append(script);
openerp.web_captcha = function (openerp){
    openerp.web.form.widgets.add('captcha', 'openerp.web.form.CaptchaWidget');
    openerp.web.form.CaptchaWidget = openerp.web.form.FieldChar.extend({
        template : "oerp_captcha",
        init: function (view, code) {
            this._super(view, code);
        },
        initialize_content: function() {
            this._super();
        },
        start: function () {
               var ds = new openerp.web.DataSetSearch(null, "res.company");                  
               var reads = ds.read_slice(['recaptcha_id'], {}).then(function(models){
                   Recaptcha.create(models[0].recaptcha_id, "oerp_recaptcha", {
                       theme: "clean",
                       callback: Recaptcha.focus_response_field});
                   });
               return this._super();
        },
        render_value: function() {
                 this._super();
        },
        store_dom_value: function () {
            if (!this.get('effective_readonly')
                    && this.$('input#recaptcha_response_field').length
                    && this.is_syntax_valid()) {
                var challenge = this.$('input#recaptcha_challenge_field').val();
                var response = this.$('input#recaptcha_response_field').val();
                this.internal_set_value(
                    this.parse_value(
                        challenge+','+response));
            }
        }, 
    });
}
