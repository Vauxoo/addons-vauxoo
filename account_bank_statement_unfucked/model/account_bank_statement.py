# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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

from openerp.osv import osv


class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'

    #Disable pylint W0622 because it is overwriting the original function
    #of the account_bank_statement class
    #odoo/addons/account/account_bank_statement.py#L639

    # pylint: disable=W0622
    def get_move_lines_for_reconciliation(
            self, cr, uid, st_line, excluded_ids=None, str=False, offset=0,
            limit=None, count=False, additional_domain=None, context=None):
        """
        This function is overwrite to solve the follow issue of Odoo v8.0:
            when refund debit/credit is create first that invoice and
            after reconciled two aml en bank statement widget show counterpart
            reference to refund debit/credit
            issue: https://github.com/odoo/odoo/issues/5129
        """
        mv_line_pool = self.pool.get('account.move.line')
        domain = self._domain_move_lines_for_reconciliation(
            cr, uid, st_line, excluded_ids=excluded_ids, str=str,
            additional_domain=additional_domain, context=context)

        # Get move lines ; in case of a partial reconciliation, only consider
        # one line
        filtered_lines = []
        reconcile_partial_ids = []
        actual_offset = offset
        while True:
            line_ids = mv_line_pool.search(
                cr, uid, domain, offset=actual_offset, limit=limit,
                order="date_maturity asc, id asc", context=context)
            lines = mv_line_pool.browse(cr, uid, line_ids, context=context)
            make_one_more_loop = False
            for line in lines:
                # We validate that move to show in bank statement
                # the line.amount_residual < 0
                # This change is reference to
                # issue:https://github.com/odoo/odoo/issues/5129
                if line.reconcile_partial_id and\
                    line.reconcile_partial_id.id in\
                        reconcile_partial_ids or line.amount_residual < 0:
                    # if we filtered a line because it is partially reconciled
                    # with an already selected line, we must do one more loop
                    # in order to get the right number of items in the pager
                    make_one_more_loop = True
                    continue
                filtered_lines.append(line)
                if line.reconcile_partial_id:
                    reconcile_partial_ids.append(line.reconcile_partial_id.id)

            if not limit or not\
                    make_one_more_loop or len(filtered_lines) >= limit:
                break
            actual_offset = actual_offset + limit
        lines = limit and filtered_lines[:limit] or filtered_lines

        # Either return number of lines
        if count:
            return len(lines)

        # Or return list of dicts representing the formatted move lines
        else:
            target_currency = st_line.currency_id or\
                st_line.journal_id.currency or\
                st_line.journal_id.company_id.currency_id
            mv_lines = mv_line_pool.\
                prepare_move_lines_for_reconciliation_widget(
                    cr, uid, lines, target_currency=target_currency,
                    target_date=st_line.date, context=context)
            has_no_partner = not bool(st_line.partner_id.id)
            for line in mv_lines:
                line['has_no_partner'] = has_no_partner
            return mv_lines
