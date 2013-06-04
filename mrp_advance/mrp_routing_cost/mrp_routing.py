# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

from tools import config


class mrp_routing_workcenter(osv.Model):
    _inherit = "mrp.routing.workcenter"

    def _calcular(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in self.browse(cr, uid, ids):
            cost = 0.00
            cost = i.hour_nbr*i.costo
            res[i.id] = cost
        return res

    _columns = {
        'costo': fields.float('Costo Unitario', required=True),
        'costo_total': fields.function(_calcular, method=True, type='float',
            string='Costo Total', store=False),
    }
    _defaults = {
        'costo': lambda *a: 0.0,
    }
