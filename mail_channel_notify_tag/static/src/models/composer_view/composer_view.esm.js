/** @odoo-module **/

import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "ComposerView",
    recordMethods: {
        /**
         * @override
         */
        _getMessageData() {
            return {
                ...this._super(...arguments),
                channel_ids: this.composer.mentionedChannels.map((channel) => channel.id),
            };
        },
    },
});
