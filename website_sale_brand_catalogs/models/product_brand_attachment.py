from odoo import fields, models


class ProductBrandAttachment(models.Model):
    _name = "product.brand.attachment"
    _description = "Product brand attachment"
    _inherit = [
        "website.multi.mixin",
        "website.published.mixin",
        "image.mixin",
    ]

    name = fields.Char(translate=True, required=True)
    attachment_id = fields.Many2one("ir.attachment")
    brand_id = fields.Many2one("product.brand")
