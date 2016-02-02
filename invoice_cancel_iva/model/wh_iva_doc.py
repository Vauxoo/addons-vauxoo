# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
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

from openerp.osv import osv, fields


class WhIvaDoc(osv.Model):
    _inherit = 'account.wh.iva'

    _columns = {

        'prev_state': fields.char('Previos State', 12,
                                  help="Field to keep the previous state of\
                                    the invoice at the time of canceling")

    }

    def check_state_cancel(self, cr, uid, ids, context=None):
        '''
        Check invoice state to not move in state
        '''
        # iva_brw = self.browse(cr, uid, ids, context=context)[0]

        for i in self.browse(cr, uid, ids, context=context)[0].wh_lines:
            # print "i.invoice_id.state", i.invoice_id.state
            if i.invoice_id.state == 'cancel':
                return False

        return True
