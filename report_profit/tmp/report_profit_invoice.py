# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv
from tools.sql import drop_view_if_exists
import time
import datetime
from mx.DateTime import *
from tools import config


class report_profit_invoice(osv.osv):
    def _get_prod_stock(self, cr, uid, ids, name, arg, context={}):
        res = {}
        prod_obj = self.pool.get('product.product')

        loc_ids = 1
        for line in self.browse(cr, uid, ids, context=context):
            startf = datetime.date.fromtimestamp(time.mktime(time.strptime(line.name,"%Y-%m-%d")))
            start = DateTime(int(startf.year),1,1)
            end = DateTime(int(startf.year),int(startf.month),int(startf.day))
            d1 = start.strftime('%Y-%m-%d %H:%M:%S')
            d2 = end.strftime('%Y-%m-%d %H:%M:%S')
            c = context.copy()
            c.update({'location': loc_ids,'from_date':d1,'to_date':d2})
            res.setdefault(line.id, 0.0)
            if line.product_id and line.product_id.id:
                prd = prod_obj.browse(cr, uid, line.product_id.id,context=c)
                res[line.id] = prd.qty_available
        return res

    _name = "report.profit.invoice"
    _description = "Move by Invoice"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True, select=True),
        'invoice_id':fields.many2one('account.invoice', 'Invoice', readonly=True, select=True),
        'move_id': fields.many2one('account.move', 'Move', readonly=True, select=True),
        'acc_cost': fields.float('Cost', readonly=True, help="Valor que adquiere el elemento para estimacion de costo de inventario"),
        'product_id':fields.many2one('product.product', 'Product', readonly=True, select=True),
        'line_id':fields.many2one('account.invoice.line', 'Linea', readonly=True, select=True),
        'quantity': fields.float('Quantity', readonly=True, help="Valor que adquiere el elemento para estimacion de costo de inventario"),
        'stock': fields.function(_get_prod_stock, method=True, type='float', string='Existencia', digits=(16, int(config['price_accuracy']))),

    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_profit_invoice')
        cr.execute("""
            create or replace view report_profit_invoice as (
            select
                l.id as id,
                to_char(i.date_invoice, 'YYYY-MM-DD') as name,
                i.id as invoice_id,
                m.id as move_id,
                l.acc_cost as acc_cost,
                l.product_id as product_id,
                l.id as line_id,
                l.quantity as quantity
            from account_invoice i
                inner join account_move m on (m.id=i.move_id)
                right join account_invoice_line l on (i.id=l.invoice_id)
                left join product_template t on (t.id=l.product_id)
            where i.state not in ('draft', 'cancel') and t.type!='service'
            group by l.id,to_char(i.date_invoice, 'YYYY-MM-DD'),i.id,m.id,l.acc_cost,l.product_id,l.quantity
            order by name
            )
        """)
report_profit_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

