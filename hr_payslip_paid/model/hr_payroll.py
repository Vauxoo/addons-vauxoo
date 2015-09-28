# coding: utf-8
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
from openerp import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    @api.depends(
        'move_id.line_id.account_id',
        'move_id.line_id.reconcile_id')
    def _compute_payments(self):
        lines = []
        if self.move_id:
            lines = []
            for p_line_id in self.move_id.line_id:
                temp_lines = []
                if p_line_id.reconcile_id:
                    temp_lines = [
                        line.id for line in p_line_id.reconcile_id.line_id
                        if line != p_line_id]
                elif p_line_id.reconcile_partial_id:
                    temp_lines = [
                        line.id for line in
                        p_line_id.reconcile_partial_id.line_partial_ids
                        if line != p_line_id]
                lines += [x for x in temp_lines if x not in lines]
        self.payment_ids = lines

    @api.one
    @api.depends(
        'move_id.line_id.account_id',
        'move_id.line_id.reconcile_id')
    def _compute_reconciled(self):
        self.reconciled = self.test_paid()

    state = fields.Selection(
        selection_add=[('paid', _('Paid'))],
        help="* When the payslip is created the status is 'Draft'.\
            \n* If the payslip is under verification, the status is 'Waiting'.\
            \n* If the payslip is confirmed then status is set to 'Done'.\
            \n* When user cancel payslip the status is 'Rejected'.\
            \n* When the payment is done the status id 'Paid'.")
    payment_ids = fields.Many2many(
        'account.move.line', string='Payments', compute='_compute_payments')
    reconciled = fields.Boolean(
        string='Paid/Reconciled', store=True, readonly=True,
        compute='_compute_reconciled', help="It indicates that the payslip has"
        " been paid and the journal entry of the payslip has been reconciled "
        "with one or several journal entries of payment.")

    @api.multi
    def move_line_id_payment_get(self):
        # return the move line ids with the same account as the payroll self
        res = {}
        if not self.id:
            return res
        account_ids = []
        for det in self.details_by_salary_rule_category:
            if det.salary_rule_id.account_credit.id:
                account = det.salary_rule_id.account_credit
                if account.type == 'payable' and account.reconcile:
                    account_ids.append(account.id)
        if not account_ids:
            return res
        query = '''SELECT i.id, l.id
                   FROM account_move_line l
                   LEFT JOIN hr_payslip i ON (i.move_id=l.move_id)
                   WHERE i.id IN %s
                   AND l.account_id=%s'''
        self._cr.execute(query, (tuple(self.ids), account_ids[0]))
        for result in self._cr.fetchall():
            res.setdefault(result[0], [])
            res[result[0]].append(result[1])
        return res.get(self.id, [])

    @api.multi
    def test_paid(self):
        # check whether all corresponding account move lines are reconciled
        line_ids = self.move_line_id_payment_get()
        if not line_ids:
            return False
        query = "SELECT reconcile_id FROM account_move_line WHERE id IN %s"
        self._cr.execute(query, (tuple(line_ids),))
        return all(row[0] for row in self._cr.fetchall())
