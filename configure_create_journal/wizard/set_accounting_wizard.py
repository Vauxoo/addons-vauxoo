# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jorge Angel Naranjo(jorge_nr@vauxoo.com)
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

from openerp.osv import fields, osv

class configure_create_journal(osv.osv_memory):
    _name = 'configure.create.journal'
    
    _columns={
        'parent_id': fields.many2one('account.account', 'Parent',
            ondelete='cascade', domain=[('type','=','view')], required=True),
        'user_type': fields.many2one('account.account.type', 'User Type',
            required=True)
    }

    def configure_journal(self, cr, uid, ids, context=None):
        journal_obj = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        sequence_obj = self.pool.get('ir.sequence')
        form = self.browse(cr, uid, ids[0])
        company_user = self.pool.get('res.company')._company_default_get(cr,
                uid, 'configure.create.journal', context=context)
        cr.execute("""
            SELECT 
                nivel.id,
                nivel.name,
                nivel.type,
                nivel.company_id
                FROM
                ( SELECT node.company_id,node.type,node.id as id,node.name
                    FROM account_account AS node,account_account AS parent
                    WHERE node.parent_left BETWEEN parent.parent_left
                    AND parent.parent_right
                    AND parent.id = %s
                    ORDER BY parent.parent_left ) nivel
                WHERE nivel.id<> %s
                AND nivel.type <> 'view'
              """,(form.parent_id.id, form.parent_id.id,))
        dat = cr.dictfetchall()
        code_journal = 0
        for acc_j in dat:
            code_journal += 1
            account_obj.write(cr, uid, acc_j['id'], {
                'type': 'liquidity',
                'user_type': form.user_type.id,
                } )
            journal_id = journal_obj.create(cr, uid, {
                'name': acc_j['name'],
                'code': 'BN%s' % code_journal,
                'type': 'bank',
                'default_debit_account_id': acc_j['id'],
                'default_credit_account_id': acc_j['id'],
            })
            journal_bwr = journal_obj.browse(cr, uid, journal_id,
                context=context )
            sequence_obj.write(cr, uid, journal_bwr.sequence_id.id,
                {'company_id': company_user})
        return False
    
