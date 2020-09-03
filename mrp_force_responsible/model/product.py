from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    production_responsible = fields.Many2one(
        'res.users',
        help='This user will be used as responsible to production orders '
        'when using this product.')
