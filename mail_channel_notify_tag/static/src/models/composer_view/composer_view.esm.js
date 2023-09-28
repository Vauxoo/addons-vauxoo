/** @odoo-module **/

import {registerInstancePatchModel} from "@mail/model/model_core";

registerInstancePatchModel("mail.composer_view", "mail_channel_notify_tag", {
    /**
     * @override
     */
    _getMessageData() {
        return {
            ...this._super(...arguments),
            channel_ids: this.composer.mentionedChannels.map((channel) => channel.id),
        };
    },
});
