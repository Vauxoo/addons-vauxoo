# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools, release
from openerp import SUPERUSER_ID

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_invoice_sequence(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for invoice in self.browse(cr, SUPERUSER_ID, ids):
            sequence_id = False
            company = invoice.company_id
            while True:
                if invoice.type == 'out_invoice':
                    if 'invoice_out_sequence_id' in company._columns:
                        sequence_id = company.invoice_out_sequence_id
                elif invoice.type == 'out_refund':
                    if 'invoice_out_refund_sequence_id' in company._columns:
                        sequence_id = company.invoice_out_refund_sequence_id
                company = company.parent_id
                if sequence_id or not company:
                    break
            if not sequence_id:
                if 'invoice_sequence_id' in invoice.journal_id._columns \
                    and invoice.journal_id.invoice_sequence_id:
                    sequence_id = invoice.journal_id.invoice_sequence_id
                elif 'sequence_id' in invoice.journal_id._columns and \
                    invoice.journal_id.sequence_id:
                    sequence_id = invoice.journal_id.sequence_id
            sequence_id = sequence_id and sequence_id.id or False
            if not sequence_id:
                sequence_str = 'account.invoice.' + invoice.type
                test = 'code=%s'
                cr.execute('SELECT id FROM ir_sequence WHERE ' +
                    test+' AND active=%s LIMIT 1', (sequence_str, True))
                res2 = cr.dictfetchone()
                sequence_id = res2 and res2['id'] or False
            res[invoice.id] = sequence_id
        return res

    _columns = {
        'invoice_sequence_id': fields.function(_get_invoice_sequence,
            method=True, type='many2one', relation='ir.sequence',
            string='Invoice Sequence', store=True, help='Sequence used \
            in the invoice'),
    }

    def action_number(self, cr, uid, ids, *args):
        if release.version >= '6':
            return super(account_invoice, self).action_number(cr, uid,
                ids, *args)
        else:
            return self.action_number5(cr, uid, ids, *args)

    def action_number5(self, cr, uid, ids, *args):
        invoice_id__sequence_id = self._get_invoice_sequence(
            cr, uid, ids)  # Linea agregada
        # Sustituye a la funcion original, es el mismo codigo, solo le agrega
        # unas lineas, y no hacer SUPER
        """OpenERP
        cr.execute('SELECT id, type, number, move_id, reference ' \
                   'FROM account_invoice ' \
                   'WHERE id IN %s',
                   (tuple(ids),))
        """
        # TinyERP compatibility
        cr.execute('SELECT id, type, number, move_id, reference '
                   'FROM account_invoice '
                   'WHERE id IN ('+','.join(map(str, ids))+')')
        obj_inv = self.browse(cr, uid, ids)[0]
        for (id, invtype, number, move_id, reference) in cr.fetchall():
            if not number:
                tmp_context = {
                    'fiscalyear_id': obj_inv.period_id and obj_inv.\
                        period_id.fiscalyear_id and obj_inv.period_id.\
                        fiscalyear_id.id or False,
                }
                """
                #if obj_inv.journal_id.invoice_sequence_id:#Original line code
                if obj_inv.journal_id.invoice_sequence_id or \
                    invoice_id__sequence_id[id]:#Agregue esta linea
                    #sid = obj_inv.journal_id.invoice_sequence_id.id#Original line code
                    sid = invoice_id__sequence_id[id] or obj_inv.\
                        journal_id.invoice_sequence_id.id#Esta es la linea modificada
                    number = self.pool.get('ir.sequence').get_id(
                        cr, uid, sid, 'id=%s', context=tmp_context)
                else:
                    number = self.pool.get('ir.sequence').get_id(cr, uid,
                        'account.invoice.' + invtype, 'code=%s',
                        context=tmp_context)
                """
                sid = invoice_id__sequence_id[id]
                if sid:
                    number = self.pool.get('ir.sequence').get_id(
                        cr, uid, sid, 'id=%s', context=tmp_context)
                if not number:
                    raise osv.except_osv(
                        'Warning !', "Not defined a secuence of folios !")

                if invtype in ('in_invoice', 'in_refund'):
                    ref = reference
                else:
                    ref = self._convert_ref(cr, uid, number)
                cr.execute('UPDATE account_invoice SET number=%s '
                           'WHERE id=%s', (number, id))
                cr.execute('UPDATE account_move SET ref=%s '
                           'WHERE id=%s AND (ref is null OR ref = \'\')',
                          (ref, move_id))
                cr.execute('UPDATE account_move_line SET ref=%s '
                           'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                          (ref, move_id))
                cr.execute('UPDATE account_analytic_line SET ref=%s '
                           'FROM account_move_line '
                           'WHERE account_move_line.move_id = %s '
                           'AND account_analytic_line.move_id = account_move_line.id',
                          (ref, move_id))
        return True
