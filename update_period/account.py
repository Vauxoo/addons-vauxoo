# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Javier Duran <javieredm@gmail.com>,
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

from openerp.osv import osv


class account_move(osv.Model):
    _inherit = 'account.move'

    def action_update_period(self, cr, uid, ids, context={}):
        moves = self.browse(cr, uid, ids[0])
        period_ids = self.pool.get('account.period').search(cr, uid, [(
            'date_start', '<=', moves.date), ('date_stop', '>=', moves.date)])
        if len(period_ids):
            period_id = period_ids[0]
            cr.execute('UPDATE account_move_line SET period_id=%s '
                       'WHERE move_id =%s', (period_id, ids[0]))

            self.write(cr, uid, ids, {'period_id': period_id})

        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
