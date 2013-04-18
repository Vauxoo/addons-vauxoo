#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
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
##########################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

from operator import itemgetter
from lxml import etree


class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    _columns = {
        'ref2': fields.char('Second Reference', size=64, required=False, help="Account entry reference"),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        journal_pool = self.pool.get('account.journal')
        if context is None:
            context = {}
        result = super(account_move_line, self).fields_view_get(
            cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type != 'tree':
            # Remove the toolbar from the form view
            if view_type == 'form':
                if result.get('toolbar', False):
                    result['toolbar']['action'] = []
            # Restrict the list of journal view in search view
            if view_type == 'search' and result['fields'].get('journal_id', False):
                result['fields']['journal_id']['selection'] = journal_pool.name_search(
                    cr, uid, '', [], context=context)
                ctx = context.copy()
                # we add the refunds journal in the selection field of journal
                if context.get('journal_type', False) == 'sale':
                    ctx.update({'journal_type': 'sale_refund'})
                    result['fields']['journal_id'][
                        'selection'] += journal_pool.name_search(cr, uid, '', [], context=ctx)
                elif context.get('journal_type', False) == 'purchase':
                    ctx.update({'journal_type': 'purchase_refund'})
                    result['fields']['journal_id'][
                        'selection'] += journal_pool.name_search(cr, uid, '', [], context=ctx)
            return result
        if context.get('view_mode', False):
            return result
        fld = []
        fields = {}
        flds = []
        title = _("Accounting Entries")
                  #self.view_header_get(cr, uid, view_id, view_type, context)

        ids = journal_pool.search(cr, uid, [])
        journals = journal_pool.browse(cr, uid, ids, context=context)
        all_journal = [None]
        common_fields = {}
        total = len(journals)
        for journal in journals:
            all_journal.append(journal.id)
            for field in journal.view_id.columns_id:
                if not field.field in fields:
                    fields[field.field] = [journal.id]
                    fld.append((field.field, field.sequence))
                    flds.append(field.field)
                    common_fields[field.field] = 1
                else:
                    fields.get(field.field).append(journal.id)
                    common_fields[field.field] = common_fields[field.field] + 1
        fld.append(('period_id', 3))
        fld.append(('journal_id', 10))
        fld.append(('ref2', 2))
        flds.append('period_id')
        flds.append('journal_id')
        flds.append('ref2')
        fields['period_id'] = all_journal
        fields['journal_id'] = all_journal
        fld = sorted(fld, key=itemgetter(1))
        widths = {
            'statement_id': 50,
            'state': 60,
            'tax_code_id': 50,
            'move_id': 40,
        }

        document = etree.Element('tree', string=title, editable="top",
                                 refresh="5", on_write="on_create_write",
                                 colors="red:state=='draft';black:state=='valid'")
        fields_get = self.fields_get(cr, uid, flds, context)
        for field, _seq in fld:
            if common_fields.get(field) == total:
                fields.get(field).append(None)
            # if field=='state':
            #     state = 'colors="red:state==\'draft\'"'
            f = etree.SubElement(document, 'field', name=field)

            if field == 'debit':
                f.set('sum', _("Total debit"))

            elif field == 'credit':
                f.set('sum', _("Total credit"))

            elif field == 'move_id':
                f.set('required', 'False')

            elif field == 'account_tax_id':
                f.set('domain', "[('parent_id', '=' ,False)]")
                f.set('context', "{'journal_id': journal_id}")

            elif field == 'account_id' and journal.id:
                f.set(
                    'domain', "[('journal_id', '=', journal_id),('type','!=','view'), ('type','!=','closed')]")
                f.set(
                    'on_change', 'onchange_account_id(account_id, partner_id)')

            elif field == 'partner_id':
                f.set(
                    'on_change', 'onchange_partner_id(move_id, partner_id, account_id, debit, credit, date, journal_id)')

            elif field == 'journal_id':
                f.set('context', "{'journal_id': journal_id}")

            elif field == 'statement_id':
                f.set(
                    'domain', "[('state', '!=', 'confirm'),('journal_id.type', '=', 'bank')]")
                f.set('invisible', 'True')

            elif field == 'date':
                f.set('on_change', 'onchange_date(date)')

            elif field == 'analytic_account_id':
                # Currently it is not working due to being executed by superclass's fields_view_get
                # f.set('groups', 'analytic.group_analytic_accounting')
                pass

            if field in ('amount_currency', 'currency_id'):
                f.set(
                    'on_change', 'onchange_currency(account_id, amount_currency, currency_id, date, journal_id)')
                f.set('attrs', "{'readonly': [('state', '=', 'valid')]}")

            if field in widths:
                f.set('width', str(widths[field]))

            if field in ('journal_id',):
                f.set("invisible", "context.get('journal_id', False)")
            elif field in ('period_id',):
                f.set("invisible", "context.get('period_id', False)")

            orm.setup_modifiers(f, fields_get[field], context=context,
                                in_tree_view=True)

        result['arch'] = etree.tostring(document, pretty_print=True)
        result['fields'] = fields_get
        return result

account_move_line()
