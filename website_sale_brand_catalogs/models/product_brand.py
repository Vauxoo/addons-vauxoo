from odoo import fields, models


class ProductBrand(models.Model):
    _inherit = "product.brand"

    catalog_ids = fields.One2many("product.brand.attachment", "brand_id", string="Catalogs")
    description_catalog = fields.Html(string="Description for the website", sanitize_attributes=False)
