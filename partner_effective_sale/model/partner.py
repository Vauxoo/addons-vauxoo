#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>           
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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

from openerp.osv import fields, osv

class Partner(osv.osv):
    _inherit = 'res.partner'

    def _fnct_search_date(self, cr, uid, obj, name, args, context=None):
        if not len(args):                                                       
            return []                                                           
        context = context or {}
        res = []
        ids = self.search(cr,uid,[],context=context)
        if not ids:                                                                
            return [('id', '=', 0)]                                                
        model = name=='sale_order_date' and 'sale_order' or 'account_invoice'
        fieldname = name=='sale_order_date' and 'date_order' or 'date_invoice'
        query='''
            SELECT partner_id as id, '''+fieldname+'''
            FROM (
                SELECT t2.partner_id, t2.'''+fieldname+'''
                FROM '''+model+''' t2
                WHERE (t2.partner_id,t2.'''+fieldname+''') IN (
                    SELECT t1.partner_id,t1.'''+fieldname+'''
                    FROM '''+model+''' t1
                    WHERE t1.partner_id = t2.partner_id
                    ORDER BY t1.'''+fieldname+'''
                    LIMIT 1)
            ) v
            WHERE partner_id IN %s
                AND '''+fieldname+'''%s\'%s\';'''

        for arg in args:                                                        
            if arg[1] in ('=','>=','<=','>','<') and arg[2]:
                cr.execute(query%(str(tuple(ids)),arg[1],arg[2]))
                res += [i[0] for i in cr.fetchall()]
        if not res:                                                                
            return [('id', '=', 0)]                                                
        return [('id', 'in', res)]    

    def _fnct_get_date(self, cr, uid, ids, fieldname, arg, context=None):
        context = context or {}
        res = {}.fromkeys(ids,None)
        so_obj = self.pool.get('sale.order')
        inv_obj = self.pool.get('account.invoice')
        for id in ids:
            s_id = so_obj.search(cr, uid,
                    [('partner_id','=',id)],order='date_order asc',limit=1) or []
            i_id = inv_obj.search(cr, uid,
                    #TODO: in the future set args for state in ['open','paid']
                    [('partner_id','=',id),('type','=','out_invoice')],
                    order='date_invoice asc',limit=1) or []
            res[id]= {
                'sale_order_date' : s_id and \
                    so_obj.browse(cr,uid,s_id[0],context=context).date_order \
                    or None,
                'invoice_date':  i_id and \
                    inv_obj.browse(cr,uid,i_id[0],context=context).date_invoice \
                    or None,}
        return res

    _columns = {
        'sale_order_date':fields.function(
            _fnct_get_date,
            method = True,
            type = 'date',
            string = 'First Sale Order',
            multi='sale_invoice',
            fnct_search=_fnct_search_date,
            ),
        'invoice_date':fields.function(
            _fnct_get_date,
            method = True,
            type = 'date',
            string = 'First Sale Invoice',
            multi='sale_invoice',
            fnct_search=_fnct_search_date,
            ),
    }
Partner()
