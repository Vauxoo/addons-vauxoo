# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
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

import wizard
import pooler

class wizard_open_move_line(wizard.interface):
    def _open_window(self, cr, uid, data, context={}):
        if not context:
            context = {}
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')
        aged_partner_balance_vw_obj = pooler.get_pool(cr.dbname).get('account.aged.partner.balance.vw')
        partner_ids = [aged_partner_balance_vw.partner_id and aged_partner_balance_vw.partner_id.id or False for aged_partner_balance_vw in aged_partner_balance_vw_obj.browse(cr, uid, data['ids'], context=context)]
        #result = mod_obj._get_id(cr, uid, 'account', 'action_account_moves_all_a')
        result = mod_obj._get_id(cr, uid, 'account', 'action_move_line_select')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id])[0]
        #result['context'] = {'partner_id': partner_ids}
        #result['domain'] = [('partner_id','in',partner_ids), ('account_id.type','=','receivable')]
        where_query = []
        days_due_start = context.get('days_due_start', False)
        if days_due_start:
            where_query.append( 'days_due >= %d'%( days_due_start ) )

        days_due_end = context.get('days_due_end', False)
        if days_due_end:
            where_query.append( 'days_due <= %d'%( days_due_end ) )
        where_query_str = (where_query and ' WHERE ' or '') + ' AND '.join( where_query )

        query = """SELECT l.id as id--, l.partner_id, l.company_id
            FROM account_move_line l
            INNER JOIN
               (
                   SELECT id, EXTRACT(DAY FROM (now() - COALESCE(lt.date_maturity,lt.date))) AS days_due
                   FROM account_move_line lt
               ) l2
               ON l2.id = l.id
               AND l.reconcile_id is null --and l.currency_id is null
       """+where_query_str
        cr.execute(query)
        res = cr.fetchall()
        move_ids = [r[0] for r in res]
        result['domain'] = [('partner_id','in',partner_ids), ('account_id.type','=','receivable'), ('id','in',move_ids)]
        return result

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _open_window, 'state': 'end'}
        }
    }
wizard_open_move_line('wizard.open.move.line')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
