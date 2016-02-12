from openerp import models, api

class Product(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _get_product_comments_qty(self, product_id):
        mail = self.env['mail.message']
        message_qty = mail.search_count([('res_id', '=' , int(product_id)),
                                         ('website_published', '=', True),
                                         ('model', '=', 'product.template'),
                                         ('type', '=', 'comment')])
        return message_qty
