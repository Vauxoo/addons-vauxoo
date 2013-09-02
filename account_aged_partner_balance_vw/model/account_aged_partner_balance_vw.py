# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
import openerp.tools as tools
from openerp.tools.translate import _

import openerp.netsvc as netsvc
import time
import os


class account_aged_partner_balance_vw(osv.TransientModel):
    _name = 'account.aged.partner.balance.vw'
    _rec_name = 'partner_id'
    _order = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner'),
        'total': fields.float(u'Total'),
        'not_due': fields.float(u'Not Due'),
        'days_due_01to30': fields.float(u'01/30'),
        'days_due_31to60': fields.float(u'31/60'),
        'days_due_61to90': fields.float(u'61/90'),
        'days_due_91to120': fields.float(u'91/120'),
        'days_due_121togr': fields.float(u'+121'),
        'company_id': fields.many2one('res.company', u'Company'),
        'currency_company_id': fields.many2one('res.currency', u'Company Currency'),
        'aatb_id':fields.many2one('account.aged.trial.balance', ('Aged Trial '
            'Balance'), help='Aged Trail Balance Document'), 
        
    }

class account_aged_trial_balance(osv.TransientModel):
    _inherit = 'account.aged.trial.balance'

    _columns = {
        'partner_line_ids':fields.one2many('account.aged.partner.balance.vw',
        'aatb_id', 'Partner Aged Trail Balance', 
        help='Partner Aged Trail Balance'), 
        'type':fields.selection([('variation','Variation in Periods'),
                            ('distributed','Distributed Payments over Debts'),
                            ], 'Type of Report',help='Reporte Type'), 
        'state':fields.selection([('draft','New'),('open','Open'),('done','Done'),
                                    ], 'Status',help='Document State'), 
    }

    _defaults = {
        'state': 'draft',
        'type': 'variation',
    }

    def to_start(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr,uid,ids[0],context=context)
        wzd_brw.write({'state':'draft', 'partner_line_ids':[(6,0,[])]})
        return {}

    def compute_lines(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr,uid,ids[0],context=context)
        wzd_brw.write({'state':'open'})
        res = self.check_report(cr, uid, ids, context=context)

        data = res['datas']
        form = data['form']
        self.set_context(cr,uid,ids,data,context=context)
        if wzd_brw.type in ('variation','distributed'):
            res = self._get_lines(cr,uid,ids,form,context=context)
            res = map(lambda x: (0,0,x),res)
            wzd_brw.write({'partner_line_ids':res})
        return {}

    def set_context(self, cr, uid, ids, data, context=None): 
        context = context or {}
        self.total_account=[]
        obj_move = self.pool.get('account.move.line')
        context = data['form'].get('used_context', {})
        context.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(cr, uid, obj='l', context=context)
        self.direction_selection = data['form'].get('direction_selection', 'past')
        self.target_move = data['form'].get('target_move', 'all')
        self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        if (data['form']['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (data['form']['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']

    def _get_lines(self, cr, uid, ids, form, context=None):
        context = context or {}
        res = []
        wzd_brw = self.browse(cr,uid,ids[0],context=context)
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                       OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
        partners = cr.dictfetchall()
        ## mise a 0 du total
        for i in range(7):
            self.total_account.append(0)
        #
        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [x['id'] for x in partners]
        if not partner_ids:
            return []
        # This dictionary will store the debit-credit for all partners, using partner_id as key.

        type_query = ''
        type_query_r = ''
        if wzd_brw.type=='distributed':
            if wzd_brw.result_selection == 'customer':
                type_query =  ', SUM(l.credit)'
                type_query_r =  ', SUM(l.debit)'
            elif wzd_brw.result_selection == 'supplier':
                type_query =  ', SUM(l.debit)'
                type_query_r =  ', SUM(l.credit)'

        advances = {}

        totals = {}
        cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    ' + type_query + '\
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
        t = cr.fetchall()
        for i in t:
            totals[i[0]] = i[1]

        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
            cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' > %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' < %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                    FROM account_move_line AS l, account_account, account_move am 
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id''', args_list)
            t = cr.fetchall()
            d = {}
            for i in t:
                d[i[0]] = i[1]
            history.append(d)

        for partner in partners:
            values = {}
            ## If choise selection is in the future
            if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                before = False
                if future_past.has_key(partner['id']):
                    before = [ future_past[partner['id']] ]
                self.total_account[6] = self.total_account[6] + (before and before[0] or 0.0)
                values['direction'] = before and before[0] or 0.0
            elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                after = False
                if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                    after = [ future_past[partner['id']] ]

                self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
                values['direction'] = after and after[0] or 0.0

            for i in range(5):
                during = False
                if history[i].has_key(partner['id']):
                    during = [ history[i][partner['id']] ]
                # Ajout du compteur
                self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if totals.has_key( partner['id'] ):
                total = [ totals[partner['id']] ]
            values['total'] = total and total[0] or 0.0
            ## Add for total
            self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']
            values['partner_id'] = partner['id']

            res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5)+['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        mapping = {
                'direction' : 'not_due',
                '4' : 'days_due_01to30', 
                '3' : 'days_due_31to60', 
                '2' : 'days_due_61to90',
                '1' : 'days_due_91to120',
                '0' : 'days_due_121togr',
                }
        res2=[]
        for r in res:
            for j,k in mapping.iteritems():
                r[k]=r.pop(j)
            r.pop('name')
            res2.append(r)
        return res2

