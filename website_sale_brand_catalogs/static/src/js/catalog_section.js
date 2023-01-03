odoo.define("website_sale_brand_catalogs.catalog_section", (require) => {
    "use strict";
    const core = require("web.core");
    require("website.s_website_form");
    const publicWidget = require("web.public.widget");
    const _t = core._t;

    publicWidget.registry.catalogSection = publicWidget.Widget.extend({
        selector: ".catalog_section",
        events: {
            "click .see_pdf, .download_pdf": "_onClickPdf",
        },
        _onClickPdf(ev) {
            let $currentTarget = $(ev.currentTarget);
            let behavior = $currentTarget.hasClass("see_pdf") ? "see" : "download";
            let attachment_id = $currentTarget.attr("data-attachment-id");
            $currentTarget
                .parents("div.catalog_section")
                .find(".download_attachment")
                .attr("data-attachment-id", attachment_id)
                .attr("data-pdf-mode", behavior);
        },
    });

    publicWidget.registry.sendForm = publicWidget.registry.s_website_form.extend({
        selector: ".catalog_section form",
        events: _.extend({}, publicWidget.registry.s_website_form.prototype.events, {
            "click .download_attachment": "_downloadAttachment",
        }),
        _downloadAttachment(ev) {
            if (this.check_fields($("#download_form"))) {
                let attachment_id = $(ev.currentTarget).attr("data-attachment-id");
                let mode = $(ev.currentTarget).attr("data-pdf-mode");
                if (mode === "download") {
                    window.location = "/web/content/" + attachment_id + "?download=true";
                } else {
                    window.open("/web/content/" + attachment_id);
                }
                this.send(ev);
            } else {
                $(".download_attachment")
                    .popover({
                        content: _t("You must complete all fields"),
                        trigger: "focus",
                    })
                    .popover("show");
            }
        },
        check_fields(obj) {
            let form_fields = true;
            obj.find("input").each(function () {
                if ($(this).val().length <= 0) {
                    form_fields = false;
                    return false;
                }
            });
            if (form_fields) {
                return true;
            }
        },
    });
});
