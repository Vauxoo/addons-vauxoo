# coding: utf-8

"""Inherit the account.model.line model in the account_model_plans Odoo module.
"""

###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.osv import fields, osv


class AccountModelLine(osv.Model):
    """Extend the account.model.line model:
        - Add a new field named analytics_id.
    """

    _inherit = 'account.model.line'
    _columns = {
        'analytics_id': fields.many2one(
            'account.analytic.plan.instance', string='Analytic Plan Instance',
            help='Analytic Plan Instance'),
    }


class AccountModel(osv.Model):
    """Extend the account.model model:
        - overwrite the generate_line_values method to take into account the
          analytics_id field.
    """

    _inherit = 'account.model'

    def generate(self, cr, uid, ids, data=None, context=None):
        if data is None:
            data = {}
        move_ids = []
        entry = {}
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        pt_obj = self.pool.get('account.payment.term')
        period_obj = self.pool.get('account.period')

        if context is None:
            context = {}

        if data.get('date', False):
            context = dict(context)
            context.update({'date': data['date']})

        move_date = context.get('date', time.strftime('%Y-%m-%d'))
        move_date = datetime.strptime(move_date,"%Y-%m-%d")
        for model in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'company_id': model.company_id.id})
            period_ids = period_obj.find(cr, uid, dt=context.get('date', False), context=ctx)
            period_id = period_ids and period_ids[0] or False
            ctx.update({'journal_id': model.journal_id.id,'period_id': period_id})
            try:
                entry['name'] = model.name%{'year': move_date.strftime('%Y'), 'month': move_date.strftime('%m'), 'date': move_date.strftime('%Y-%m')}
            except:
                raise osv.except_osv(_('Wrong Model!'), _('You have a wrong expression "%(...)s" in your model!'))
            move_id = account_move_obj.create(cr, uid, {
                'ref': entry['name'],
                'period_id': period_id,
                'journal_id': model.journal_id.id,
                'date': context.get('date', fields.date.context_today(self,cr,uid,context=context))
            })
            move_ids.append(move_id)
            for line in model.lines_id:
                analytic_account_id = False
                if line.analytic_account_id:
                    if not model.journal_id.analytic_journal_id:
                        raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (model.journal_id.name,))
                    analytic_account_id = line.analytic_account_id.id
                analytics_id = False
                if line.analytics_id:
                    if not model.journal_id.analytic_journal_id:
                        raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (model.journal_id.name,))
                    analytics_id = line.analytics_id.id
                val = {
                    'move_id': move_id,
                    'journal_id': model.journal_id.id,
                    'period_id': period_id,
                    'analytic_account_id': analytic_account_id,
                    'analytics_id': analytics_id
                }

                date_maturity = context.get('date',time.strftime('%Y-%m-%d'))
                if line.date_maturity == 'partner':
                    if not line.partner_id:
                        raise osv.except_osv(_('Error!'), _("Maturity date of entry line generated by model line '%s' of model '%s' is based on partner payment term!" \
                                                                "\nPlease define partner on it!")%(line.name, model.name))

                    payment_term_id = False
                    if model.journal_id.type in ('purchase', 'purchase_refund') and line.partner_id.property_supplier_payment_term:
                        payment_term_id = line.partner_id.property_supplier_payment_term.id
                    elif line.partner_id.property_payment_term:
                        payment_term_id = line.partner_id.property_payment_term.id
                    if payment_term_id:
                        pterm_list = pt_obj.compute(cr, uid, payment_term_id, value=1, date_ref=date_maturity)
                        if pterm_list:
                            pterm_list = [l[0] for l in pterm_list]
                            pterm_list.sort()
                            date_maturity = pterm_list[-1]

                val.update({
                    'name': line.name,
                    'quantity': line.quantity,
                    'debit': line.debit,
                    'credit': line.credit,
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.partner_id.id,
                    'date': context.get('date', fields.date.context_today(self,cr,uid,context=context)),
                    'date_maturity': date_maturity
                })
                account_move_line_obj.create(cr, uid, val, context=ctx)

        return move_ids

