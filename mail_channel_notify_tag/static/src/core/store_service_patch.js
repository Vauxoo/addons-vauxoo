import {Store} from "@mail/core/common/store_service";
import {patch} from "@web/core/utils/patch";

patch(Store.prototype, {
    async getMessagePostParams({postData}) {
        const params = await super.getMessagePostParams(...arguments);
        const channelIds = (postData.mentionedChannels || []).map((channel) => channel.id);
        if (channelIds.length) {
            params.post_data.channel_ids = channelIds;
        }
        return params;
    },
});
