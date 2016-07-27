# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductMergeUoMFieldExclude(models.Model):
    _description = 'Product Merge Field Exclude'
    _name = "product.merge.uom.field.exclude"

    field_id = fields.Many2one(comodel_name='ir.model.fields',
                               string='Field', required=True,
                               domain=[('relation', '=', 'product.uom')])
    model_id = fields.Many2one(comodel_name='ir.model',
                               related='field_id.model_id',
                               string='Model', readonly=True)
    name = fields.Char(related='field_id.name')
