# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: luis_t@vauxoo.com
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    production_responsible = fields.Many2one(
        'res.users', 'Production responsible',
        help='This user will be used as responsible to production order '
        'when use this product.')
