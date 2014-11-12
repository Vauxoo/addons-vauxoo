# -*- encoding: utf-8 -*-
# ############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ############ Credits #######################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Moises Lopez <moises@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
# ############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import models, fields


class import_tax_tariff(models.Model):
    _name = "import.tax.tariff"
    _description = "Import Tax Tariff"

    name = fields.Char(required=True)
    tariff_ids = fields.One2many('tariff.tariff',
                                 'import_tax_id',
                                 string='Tariff')
    product_category_id = fields.Many2one('product.category',
                                          string='Product Category',)
    description = fields.Text()


class tariff_tariff(models.Model):
    _name = "tariff.tariff"

    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    code = fields.Char("Code")
    unit_value = fields.Float(digits=(6, 2), help="Tariff per Unit of Product")
    tax_percentage = fields.Float(digits=(6, 2), help="Tax Percentage")
    minimum = fields.Float(digits=(6, 2), help="Amount Minimun")
    import_tax_id = fields.Many2one('import.tax.tariff',
                                    ondelete='set null',
                                    string='Import Tax',
                                    index=True)
    type_id = fields.Selection([('ad_valorem', "Ad Valorem"),
                                ('specific', "Specific"),
                                ('mixed', "Mixed")], string='Type',
                               default='ad_valorem')
