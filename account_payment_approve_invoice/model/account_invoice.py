##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Maria Gabriela Quilarque)          
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
##############################################################################
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
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_invoice(osv.osv):
    """
    OpenERP Model : Account Invoice
    """

    _inherit = 'account.invoice'

    _columns = {
        'to_pay': fields.boolean('To Pay',readonly=True, help="This field was mark when the purchase manager approve this invoice to be pay"),
    }
    _defaults = {
        'to_pay': False,
    }


    def payment_approve(self, cr, uid, ids, context=None):
        '''
        Mark boolean as True, to approve invoice to be pay.
        '''
    	context = context or {}
        return self.write(cr,uid,ids,{'to_pay':True})

    def payment_disapprove(self, cr, uid, ids, context=None):
        '''
        Mark boolean as False, to Disapprove invoice to be pay.
        '''
        context = context or {}
        return self.write(cr,uid,ids,{'to_pay':False})
