from odoo import http
from odoo.http import request


class WebsiteCatalogs(http.Controller):
    @http.route(
        [
            "/catalog",
            "/catalog/page/<int:page>",
            '/catalog/brand/<model("product.brand"):brand>',
            '/catalog/brand/<model("product.brand"):brand>/page/<int:page>',
        ],
        type="http",
        auth="public",
        website=True,
    )
    def brand_catalogs(self, brand=None, page=0, bpp=False, **kw):
        catalog_brands = self.catalog_brands()
        if brand:
            values = self.catalog_brand_detail(brand)
            return request.render("website_sale_brand_catalogs.brand_details", values)
        if bpp:
            try:
                bpp = int(bpp)
                kw["bpp"] = bpp
            except ValueError:
                bpp = False
        if not bpp:
            bpp = request.env["website"].get_current_website().brand_bpp or 20
        domain = []
        page_url = "/catalog"
        brands_count = catalog_brands.search_count(domain)
        pager = request.website.pager(url=page_url, total=brands_count, page=page, step=bpp, scope=3, url_args=kw)
        catalog_brands = catalog_brands.search(domain, offset=pager["offset"], limit=bpp, order="id ASC")
        values = {"pager": pager, "bpp": bpp, "catalog_brands": catalog_brands}
        template = "website_sale_brand_catalogs.brand_catalog"
        return request.render(template, values)

    def get_domain_catalogs(self):
        return [("catalog_ids", "!=", False)]

    def catalog_brands(self):
        domain = self.get_domain_catalogs()
        return request.env["product.brand"].search(domain)

    def catalog_brand_detail(self, brand_id):
        catalogs_brand = request.env["product.brand"].browse(int(brand_id))
        values = {
            "active_page": "catalog_ids",
            "brand": brand_id,
            "catalogs": catalogs_brand.catalog_ids,
        }
        return values
