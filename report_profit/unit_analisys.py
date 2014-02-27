#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: javier@vauxoo.com
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
##########################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class product_uom_consol(osv.Model):
    _name = 'product.uom.consol'
    _description = 'A third unit to consolidate the sales and purchase.'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'uom_line_ids': fields.one2many('product.uom.consol.line',
                                        'p_uom_c_id', 'Units', required=False),
    }


class product_uom_consol_line(osv.Model):
    """
    Third Unit to consolidate sales and purchases!
    """
    _name = 'product.uom.consol.line'
    _description = ''' Elements to control the seconds unit of measure. '''

    def _factor(self, cursor, user, ids, name, arg, context):
        res = {}
        for uom in self.browse(cursor, user, ids, context=context):
            if uom.factor_consol:
                if uom.factor_inv_data_consol:
                    res[uom.id] = uom.factor_inv_data_consol
                else:
                    res[uom.id] = round(1 / uom.factor_consol, 6)
            else:
                res[uom.id] = 0.0
        return res
    _columns = {
        'p_uom_c_id': fields.many2one('product.uom.consol', 'Consolidate Unit',
                                      required=False),
        'factor_consol': fields.float('Rate', digits=(12, 6), required=True,
                                      help='The coefficient for the formula:\n'
                                      '1 (base unit) = coeff (this unit). Rate'
                                      '= 1 / Factor.'),
        'factor_inv_consol': fields.function(_factor, digits=(12, 6),
                                             method=True, string='Factor inv',
                                             help='The coefficient for the'
                                             formula: \n'
                                             'coeff (base unit) = 1'
                                             '(this unit).Factor = 1 / Rate.'),
        'factor_inv_data_consol': fields.float('Factor', digits=(12, 6)),
        'rounding_consol': fields.float('Rounding Precision', digits=(16, 3),
                                        required=True,
                                        help="""The computed quantity will be a
                                        multiple of this value.  Use 1.0 for
                                        products that can not be split."""),
        'analysis': fields.boolean('Active'),
        'p_uom_id': fields.many2one('product.uom', 'Unit of measure',
                                    required=True,
                                    help="Unit of Measure used for compute."),
        'name': fields.char('Name', size=64, required=False),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
