openerp.web_captcha = function (openerp)
{
    openerp.web.form.widgets.add('captcha', 'openerp.web.form.CaptchaWidget');
    openerp.web.form.CaptchaWidget = openerp.web.form.FieldChar.extend(
        {
        template : "captcha",
        init: function (view, code) {
            this._super(view, code);
            console.log(view); 
            console.log(code); 
            console.log('loading...');
        },
        start: function () {
            this.$el.text("Hello, world!");
            console.log("loading dd2"); 
        }
    });

}
