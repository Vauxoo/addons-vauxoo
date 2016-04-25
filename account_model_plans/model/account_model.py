# coding: utf-8

"""Inherit the account.model.line model in the account_model_plans Odoo module.
"""

###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.osv import fields, osv


class AccountModelLine(osv.Model):
    """Extend the account.model.line model:
        - Add a new field named analytics_id.
    """

    _inherit = 'account.model.line'
    _columns = {
        'analytics_id': fields.many2one(
            'account.analytic.plan.instance', string='Analytic Plan Instance',
            help='Analytic Plan Instance'),
    }


class AccountModel(osv.Model):
    """Extend the account.model model:
        - overwrite the generate_line_values method to take into account the
          analytics_id field.
    """

    _inherit = 'account.model'

    def generate_line_values(self, cr, uid, line, context=None):
        """Overwrite method to take into account the analytics_id field.
        The val dictionary is updated to add the field and value.
        @return a tuple (val, context) where val is a dictionary.
        """
        context = context or {}
        val, context = super(AccountModelLine).generate_line_values(
            cr, uid, line, context=context)
        val.update({'analytics_id':
                    line.analytics_id and line.analytics_id.id or False})
        return val, context
