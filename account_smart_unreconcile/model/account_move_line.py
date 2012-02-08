#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
################################################################################

from osv import fields, osv

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    def _smart_unreconcile(self, cr, uid, amr_id,aml_ids=[], context=None):
        """
        The method takes an account_move_reconcile record,
        and given a certain account_move_line related to it
        it will return a new account_move_reconcile record
        without the given account_move_line record reconciled or 
        partially reconciled.
            :type amr_id: int
            :param amr_id: the id identifying the account_move_reconcile
                            record which is gone to be broken and gather
                            afterwards.
            :type aml_ids: [int]
            :param aml_ids: a list of account_move_line ids which 
                            are going to get rid from the reconcile record
            
            :rtype: bool
            :return: will return True always otherwise it will rise and error.
        """

        if context is None:
            context={}
        obj_amr = self.pool.get('account.move.reconcile')

        if not aml_ids:
            raise osv.except_osv(_('Error'),_('There are not account move lines to unreconcile'))
        
        aml_pre_ids = self.search(cr,uid,[('reconcile_id','=',amr_id)]) or self.search(cr,uid,[('reconcile_partial_id','=',amr_id)])
        aml_rem_ids=list(set(aml_pre_ids) - set(aml_ids))
        
        if len(aml_rem_ids)>= 2 :
            self._remove_move_reconcile(cr, uid, aml_pre_ids, context=context)
            self.reconcile_partial(cr, uid,aml_rem_ids,'auto',context=context)
        else:
            self._remove_move_reconcile(cr, uid, aml_pre_ids,context=context)
        return True
        
account_move_line()
