# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Vauxoo Consultores (info@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ProcurementRule(models.Model):

    _inherit = 'procurement.rule'

    location_bom_id = fields.Many2one(
        'stock.location',
        string='Location of Raw Material',
        domain="[('usage', '=', 'internal'), ('id', '!=', location_id)]",
        help='MO created from procurement will take raw material from here'
    )


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        if procurement.rule_id.location_bom_id:
            res.update(
                {'location_src_id': procurement.rule_id.location_bom_id.id})
        return res
