# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

from openerp.tools.translate import _

from openerp.osv import osv, fields
import decimal_precision as dp


class account_move(osv.Model):
    _inherit = "account.move"

    """example of query that get these fields ---
    select sum(credit), sum(debit)
    from account_move_line
    where move_id=27
    """

    def _sum_credit_debit(self, cr, uid, ids, field, arg, context=None):
        suma = []
        dict = {}
        for id in ids:
            cr.execute("""select sum(credit), sum(debit)
                        from account_move_line
                        where move_id=%s""", (id,))
            suma = cr.fetchone()
            dict[id] = {field[0]: suma[0], field[1]: suma[1]}
        return dict  # {25:{total_debit:1200},{total_credit:1200}}

    _columns = {
        'total_debit': fields.function(_sum_credit_debit,
                               string='Total debit', method=True,
                               digits_compute=dp.get_precision(
                                   'Account'),
                               type='float', multi="total_credit_debit"),
        'total_credit': fields.function(_sum_credit_debit,
                                string='Total credit', method=True,
                                digits_compute=dp.get_precision(
                                    'Account'),
                                type='float', multi="total_credit_debit"),
    }
