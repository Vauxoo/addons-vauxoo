# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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

import time
from tools.translate import _
from osv import fields, osv
import pooler

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'pay_method_id': fields.many2one('pay.method', 'Metodo de Pago', help = 'Indica la forma en que se pagó o se pagará la factura, donde las opciones pueden ser: cheque, transferencia bancaria, depósito en cuenta bancaria, tarjeta de crédito, efectivo etc. Si no se sabe como va ser pagada la factura, dejarlo vacío y en el xml aparecerá “No identificado”.'),
    }
res_partner()
