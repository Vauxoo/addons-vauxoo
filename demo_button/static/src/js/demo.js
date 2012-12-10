openerp.demo_button = function (instance) {
    var QWeb = instance.web.qweb;
          _t = instance.web._t;
    /**
     * ------------------------------------------------------------
     * UserMenu
     * ------------------------------------------------------------
     * 
     * Add a link on the top user bar for ask for full help
     */
    instance.web.DemoButton = instance.web.Widget.extend({
        
        template:'demo_button.DemoButton',
    
        start: function () {
            this.$('.oe_demo_button').on('click', this.on_see_doc );
//            this.$el.click('click','.oe_process_tech',this.on_see_proc);
            this._super();
        },
        
        on_see_doc: function(event) {
            this.rpc("/web/webclient/version_info", {}).done(function(res) {
                var $help = $(QWeb.render("demo_button.AllFonts",
                                          {version_info: res,
                                           widget: instance,
                                          }));
                var $dialog = instance.web.dialog($help, {autoOpen: true,
                                            modal: true,
                                            top:0, 
                                            show:{ effect: 'drop', 
                                                   direction: "up" },
                                            hide:{ effect: 'drop', 
                                                   direction: "up" },
                                            resizable: false,
                                            width: "auto",
                                            position: "top",
                                            title: _t("All Icon Fonts")});
            });
        },
    });

    instance.web.UserMenu.include({
        do_update: function(){
            var self = this;
            this._super.apply(this, arguments);
            this.update_promise.then(function() {
                var doc_button = new instance.web.DemoButton();
                doc_button.appendTo(instance.webclient.$el.find('.oe_systray'));
            });
        },
    });
 };
