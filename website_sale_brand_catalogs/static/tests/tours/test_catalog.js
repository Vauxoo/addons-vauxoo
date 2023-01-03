odoo.define("website_sale_brand_catalogs.test_catalog", function (require) {
    "use strict";

    const tour = require("web_tour.tour");

    require("web.dom_ready");

    tour.register(
        "website_sale_brand_catalogs.test_catalog",
        {
            test: true,
        },
        [
            {
                content: "Click menu catalogs",
                trigger: 'a[href="/catalog"]',
                run: "click",
            },
            {
                content: "Click on brand",
                trigger: "div.brand_card",
                run: "click",
            },
            {
                content: "Click on content",
                trigger: "div.brand_name",
                run: "click",
            },
            {
                content: "Click on brand",
                trigger: "div.brand_image",
                run: "click",
            },
            {
                content: "Click on catalog",
                trigger: "div.img-catalog",
                run: "click",
            },
            {
                trigger: 'input[name="contact_name"]',
                content: "give name",
                run: "text Contact name",
            },
            {
                trigger: 'input[name="email_from"]',
                content: "give email",
                run: "text test@test.com",
            },
            {
                trigger: 'input[name="phone"]',
                content: "give phone",
                run: "text 1234567890",
            },
            {
                trigger: ".download_attachment",
                content: "Download catalog",
                run: "click",
            },
        ]
    );
});
