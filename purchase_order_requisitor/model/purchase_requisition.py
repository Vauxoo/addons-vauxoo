# -*- encoding: utf-8 -*-
########################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools

class purchase_order(osv.Model):
    _inherit = "purchase.order"

    _columns = {
        'rfq_user_id': fields.many2one('res.users', 'Requisitor'),
    }

class purchase_requisition(osv.Model):
    _inherit = "purchase.requisition"


    def make_purchase_order(self, cr, uid, ids, partner_id,
                                    context=None):
        if context is None:
            context = {}
        res = super(purchase_requisition, self).make_purchase_order(cr, uid, ids, partner_id, context=context)

        if res:
            requisition_user = self.browse(
                cr, uid, res.keys()[0], context=context).user_id
            purchase_order_obj = self.pool.get('purchase.order')
            purchase_order_obj.write(
                            cr, uid, res[res.keys()[0]],
                            {'rfq_user_id': requisition_user.id})
        return res
