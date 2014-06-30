# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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
#
from openerp.osv import fields, osv
from openerp import netsvc

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    
    def _compute_lines(self, cr, uid, ids, name, args, context=None):
        result = {}
        for payslip in self.browse(cr, uid, ids, context=context):
            src = []
            lines = []
            if payslip.move_id:
                for p in payslip.move_id.line_id:
                    temp_lines = []
                    if p.reconcile_id:
                        temp_lines = map(lambda x: x.id, p.reconcile_id.line_id)
                    elif p.reconcile_partial_id:
                        temp_lines = map(lambda x: x.id, p.reconcile_partial_id.line_partial_ids)
                    lines += [x for x in temp_lines if x not in lines]
                    src.append(p.id)

            lines = filter(lambda x: x not in src, lines)
            result[payslip.id] = lines
        return result
    
    def _reconciled(self, cr, uid, ids, name, args, context=None):
        res = {}
        wf_service = netsvc.LocalService("workflow")
        for pay in self.browse(cr, uid, ids, context=context):
            res[pay.id] = self.test_paid(cr, uid, [pay.id])
            if not res[pay.id] and pay.state == 'paid':
                wf_service.trg_validate(uid, 'hr.payslip', pay.id, 'open_test', cr)
        return res
        
    def _get_payslip_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        payslip_ids = []
        if move:
            payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('move_id', 'in', move.keys())], context=context)
        return payslip_ids
        
    def _get_payslip_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        payslip_ids = []
        if move:
            payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('move_id', 'in', move.keys())], context=context)
        return payslip_ids

    _columns = {
        'state': fields.selection([
                    ('draft', 'Draft'),
                    ('verify', 'Waiting'),
                    ('done', 'Done'),
                    ('cancel', 'Rejected'),
                    ('paid', 'Paid'),
                ], 'Status', select=True, readonly=True,
                    help='* When the payslip is created the status is \'Draft\'.\
                    \n* If the payslip is under verification, the status is \'Waiting\'. \
                    \n* If the payslip is confirmed then status is set to \'Done\'.\
                    \n* When user cancel payslip the status is \'Rejected\'.\
                    \n* When the payment is done the status id \'Paid\'.'),
        'payment_ids': fields.function(_compute_lines, relation='account.move.line',
            type="many2many", string='Payments'),
        'reconciled': fields.function(_reconciled, string='Paid/Reconciled', type='boolean',
            store={
                'hr.payslip': (lambda self, cr, uid, ids, c={}: ids, [], 50),
                'account.move.line': (_get_payslip_from_line, None, 50),
                'account.move.reconcile': (_get_payslip_from_reconcile, None, 50),
            }, help="It indicates that the payslip has been paid and the journal entry of the payslip has been reconciled with one or several journal entries of payment."),
        }
        
    def move_line_id_payment_get(self, cr, uid, ids, *args):
        if not ids: return []
        result = self.move_line_id_payment_gets(cr, uid, ids, *args)
        return result.get(ids[0], [])

    def move_line_id_payment_gets(self, cr, uid, ids, *args):
        res = {}
        if not ids: return res
        payslip_bwr = self.browse(cr, uid, ids[0])
        account_ids = []
        for x in payslip_bwr.details_by_salary_rule_category:
            if x.salary_rule_id.account_credit.id:
                account_ids.append(x.salary_rule_id.account_credit.id)
        if not account_ids: return res
        cr.execute('SELECT i.id, l.id '\
                   'FROM account_move_line l '\
                   'LEFT JOIN hr_payslip i ON (i.move_id=l.move_id) '\
                   'WHERE i.id IN %s '\
                   'AND l.account_id=%s',
                   (tuple(ids), account_ids[0]))
        for r in cr.fetchall():
            res.setdefault(r[0], [])
            res[r[0]].append( r[1] )
        return res
        
    def test_paid(self, cr, uid, ids, *args):
        res = self.move_line_id_payment_get(cr, uid, ids)
        if not res:
            return False
        ok = True
        for id in res:
            cr.execute('select reconcile_id from account_move_line where id=%s', (id,))
            ok = ok and  bool(cr.fetchone()[0])
        return ok
