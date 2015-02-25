# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields


class mail_message(osv.Model):
    _inherit = 'mail.message'

    def _comment_bought(self, cr, uid, ids, name, arg, context=None):
        res = {}
        sale_report_obj = self.pool.get('sale.report')
        cr.execute("""
            {0}
            FROM ( {1} )
            {2}
            """.format(sale_report_obj._select(), sale_report_obj._from(),
                   sale_report_obj._group_by()))
        mail_cache = self.browse(cr, uid, ids, context)[0]
        for rep in cr.fetchall():
            product_id = rep[1]
            partner_id = rep[8]
            if mail_cache.res_id == product_id and \
               mail_cache.author_id.id == partner_id:
                res[ids[0]] = 1
        return res

    _columns = {
        'comment_bought': fields.function(_comment_bought, type='boolean',
                                          string='Comment Bought',
                                          store=True),
    }
