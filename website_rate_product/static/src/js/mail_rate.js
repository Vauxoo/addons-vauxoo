openerp.website_rate_product = function(instance) {
    instance.mail.MessageCommon.include({
        init: function (parent, datasets, options){
            this.rating = datasets.rating || 0;
            this._super.apply(this, arguments);
        }
    });
};
