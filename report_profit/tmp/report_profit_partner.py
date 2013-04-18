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

from openerp.osv import osv, fields
from openerp.tools.sql import drop_view_if_exists



class report_profit_partner(osv.Model):
    _name = "report.profit.partner"
    _description = "Profit by Products and Partner"
    _auto = False
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, select=True),
        'sum_last_cost': fields.float('Last Cost Sum', readonly=True),
        'sum_price_subtotal': fields.float('Subtotal Price Sum', readonly=True),
        'sum_qty_consol': fields.float('Consolidate qty Sum', readonly=True),
        'p_uom_c_id': fields.many2one('product.uom.consol', 'Consolidate Unit', readonly=True),
    }

# where l.quantity != 0 and i.type in ('out_invoice', 'out_refund') and
# i.state in ('open', 'paid')
    def init(self, cr):
        drop_view_if_exists(cr, 'report_profit_partner')
        cr.execute("""
            create or replace view report_profit_partner as (
            select
                partner_id as id,
                partner_id,
                SUM(last_cost) as sum_last_cost,
                SUM(price_subtotal) as sum_price_subtotal,
                SUM(qty_consol) as sum_qty_consol,
                p_uom_c_id
            from report_profit p
            group by partner_id,p_uom_c_id
            )
        """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
