openerp.account_budget_imp = function (openerp) {
    openerp.web_kanban.KanbanRecord.include({
        renderElement: function() {
            this.qweb_context = {
                record: this.record,
                widget: this,
                read_only_mode: this.view.options.read_only_mode
            };
            for (var p in this) {
                if (_.str.startsWith(p, 'kanban_')) {
                    this.qweb_context[p] = _.bind(this[p], this);
                }
            }
            var $el = openerp.web.qweb.render(this.template, {
                'widget': this,
                'content': this.view.qweb.render('kanban-box', this.qweb_context)
            });
            this.replaceElement($el);
        },
        bind_events: function(){
            var ko = this.$el.find('.oe_kanban_options');
            if (this.$el.find('.oe_openoptions').length) {
                this.$el.find('.oe_openoptions').click(function(){
                    /*
                    var ko = this.$el.find('.oe_kanban_options');
                    */
                    ko.toggle();
                    console.log('En el Click de this ::: ' + ko.html());
                });
            }
        this._super(); 
        },
        start: function(){
            this._super();
        },
        kanban_name_resumed: function(r) {
            var show_txt = r.raw_value;
            if (r.type === "many2one"){
                show_txtbase = r.raw_value[1];
                if (show_txtbase){
                    if (show_txtbase.split('/').length >= 3){
                        /*
                        TODO: maybe change and count characters too! to allow
                        mantain the get_name in only one line.
                        */
                        show_txto =  show_txtbase.split('/')[0].substring(0, 4);
                        show_txtf =  show_txtbase.split('/').pop();
                        show_txt = show_txto+'/../'+show_txtf;
                    }
                }
            }
            return show_txt 
        }
    });
};

