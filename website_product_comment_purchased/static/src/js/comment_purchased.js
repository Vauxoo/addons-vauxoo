openerp.website_product_comment_purchased = function(instance) {
    instance.mail.MessageCommon.include({
        init: function (parent, datasets, options){
            this.comment_bought= datasets.comment_bought || false;
            this._super.apply(this, arguments);
        }
    });
};


