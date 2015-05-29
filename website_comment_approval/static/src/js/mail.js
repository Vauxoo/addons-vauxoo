openerp.website_comment_approval = function(instance) {
    var mail = instance.mail;
    instance.mail.MessageCommon.include({
        init: function (parent, datasets, options){
            this.website_published = datasets.website_published || false;
            this._super.apply(this, arguments);
        }
    });
};
