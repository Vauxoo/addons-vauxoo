# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _

import logging

_logger = logging.getLogger(__name__)

# Excel Stuff
try:
    import xlrd
except ImportError:
    _logger.info('account_bank_statement_vauxoo: needs xlrd library')
import base64
from datetime import date, datetime, timedelta


class AccountBankStatement(osv.Model):
    _inherit = 'account.bank.statement'

    def _fromto(self, cr, uid, ids, field, arg, context=None):
        statements = self.browse(cr, uid, ids, context=context)
        result = {}
        for st in statements:
            result[st.id] = str(self._get_date_range(
                cr, uid, ids, context=context))
        return result

    def _linestoreview(self, cr, uid, ids, field, arg, context=None):
        statements = self.browse(cr, uid, ids, context=context)
        result = {}
        for st in statements:
            result[st.id] = len(
                [i for i in st.bs_line_ids if i.state != 'done'])
        return result

    _columns = {
        'bs_line_ids': fields.one2many('bank.statement.imported.lines',
                                       'bank_statement_id', 'Statement', required=False),
        'fname': fields.char('File Name Imported', 128, required=False,
                             help="Name of file imported, to be able to do that add as attach\
                 ment an xls file with the corect format directly imported\
                 from Banco Nacional"),
        'from_to_file': fields.function(_fromto, string='Date Range on file',
                                        type='char',
                                        help="Date range read on xls file imported from your\
                 attachments"),
        'lines_toreview': fields.function(_linestoreview,
                                          string='Lines to Review', type='integer',
                                          help="Quantity of lines to verify from file."),
        'move': fields.many2one('account.move', 'Move Temp to conciliate',
                                readonly=True, help="This account move is the used to make the\
             conciliation throught the bank statement imported with excel"),
    }

    def button_confirm_bank(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        context.update({"button_confirm": True})
        bsli_obj = self.pool.get('bank.statement.imported.lines')
        for st in self.browse(cr, uid, ids, context=context):
            bs_line_ids = [a.id for a in st.bs_line_ids]
            for bsil in bsli_obj.browse(cr, uid, bs_line_ids, context=context):
                #~ if bsil.state!="done":
                res.append(bsli_obj.button_setinvoice(
                    cr, uid, [bsil.id], context=context))
                continue
        if all(res):
            return self.write(cr, uid, [st.id], {'state': 'confirm'},
                              context=context)
        else:
            return True

    def file_verify_cr(self, cr, uid, ids, context={}):
        """Verification of format Files.
        For CR Banco Nacional
        #Oficina    FechaMovimiento NumDocumento    Debito  Credito Descripcion
        """
        sheet = context.get('xls_sheet')
        if sheet:
            if sheet.cell(0, 0).value == 'Oficina' and \
                sheet.cell(0, 1).value == 'FechaMovimiento' and \
                sheet.cell(0, 2).value == 'NumDocumento' and \
                sheet.cell(0, 3).value == 'Debito' and \
                sheet.cell(0, 4).value == 'Credito' and \
                    sheet.cell(0, 5).value == 'Descripcion':
                return True
        return False

    def xlrd_to_date(self, cv):
        from1900to1970 = datetime(1970, 1, 1) - datetime(
            1900, 1, 1) + timedelta(days=2)
        value = date.fromtimestamp(int(cv) * 86400) - from1900to1970
        return value

    def write_file(self, cr, uid, ids, context={}):
        sheet = context.get('xls_sheet')
        for i in range(sheet.nrows - 1):
            if i:
                l = {'office': int(sheet.cell_value(i, 0)),
                     'date': self.xlrd_to_date(sheet.cell_value(i, 1)),
                     'numdocument': str(sheet.cell_value(i, 2)).split('.')[0],
                     'debit': sheet.cell_value(i, 3) and
                     float(sheet.cell_value(
                           i, 3).replace(',', '')),
                     'credit': sheet.cell_value(i, 4) and
                     float(sheet.cell_value(
                           i, 4).replace(',', '')),
                     'name': sheet.cell_value(i, 5),
                     }

                self.write(cr, uid, ids, {'bs_line_ids': [
                           (0, 0, l)]}, context=context)
        return True

    def delete_lines_file(self, cr, uid, ids, context=None):
        bs = self.browse(cr, uid, ids, context=context)[0]
        bs.bs_line_ids and [self.write(cr, uid, ids, {
            'bs_line_ids': [(2, i.id)]}) for i in bs.bs_line_ids]
        self.write(cr, uid, ids, {'fname': ''}, context=context)
        return True

    def set_date_period(self, cr, uid, ids, context=None):
        p_obj = self.pool.get('account.period')
        st = self.browse(cr, uid, ids, context=context)[0]
        company_id = st.company_id.id
        range_dates = self._get_date_range(cr, uid, ids, context=context)
        ini_period = p_obj.find(cr, uid, range_dates[
                                0], context={'company_id': company_id})
        end_period = p_obj.find(cr, uid, range_dates[
                                1], context={'company_id': company_id})
        if ini_period != end_period:
            raise osv.except_osv(_("Warning"), _(
                "You can not make a bank reconcilation for bank\
                    moves with dates on different periods"))
        else:
            self.write(cr, uid, ids, {'period_id': ini_period[0],
                                      'date': range_dates[1]}, context=context)
        return True

    def _get_date_range(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)[0].bs_line_ids
        dates = sorted([d.date for d in lines])
        date_range = dates and (dates[0], dates[-1]) or ()
        return date_range

    def set_counterpart(self, cr, uid, ids, context=None):
        """Return account_id to set the line in bank statement
        TODO: Make better doc
        """
        bsl = self.pool.get('bank.statement.imported.lines').browse(
            cr, uid, context.get('bsl_id', []), context=context)
        a_obj = self.pool.get('account.account')
        p_obj = self.pool.get('ir.config_parameter')
        # default algorithm
        rec = p_obj.search(cr, uid, [('key', '=', 'receivable_bs_default')])
        r = eval(p_obj.browse(cr, uid, rec)[0].value)
        pay = p_obj.search(cr, uid, [('key', '=', 'payable_bs_default')])
        p = eval(p_obj.browse(cr, uid, pay)[0].value)
        payrec = bsl.debit and p or r
        aid = a_obj.search(cr, uid, payrec, context=context)
        payrec_id = a_obj.browse(cr, uid, aid, context=context)[0].id
        ######
        # Not Default ones.
        ######
        rec = p_obj.search(cr, uid, [('key', 'ilike', 'bs_default'),
                                     ('key', '<>', 'receivable_bs_default'),
                                     ('key', '<>', 'payable_bs_default')])
        ############################################################
        # Reviewing date on journals
        ############################################################
        concept_ids = bsl.bank_statement_id.journal_id.concept_ids
        try:
            concepts = [(c.sequence, eval(
                c.expresion), c.partner_id.id, c.account_id.id)
                for c in concept_ids]
            print concepts
        except Exception, var:
            print var
        for b in bsl.bank_statement_id.journal_id.concept_ids:
            Exp = eval(b.expresion)
            for e in Exp:
                if e in bsl.name:
                    return (b.account_id and b.account_id.id or payrec_id,
                            b.partner_id and b.partner_id.id)
        return (payrec_id, False)

    def create_aml_tmp(self, cr, uid, ids, context=None):
        am_obj = self.pool.get('account.move')
        aml_obj = self.pool.get('account.move.line')
        p_obj = self.pool.get('account.period')
        partner_obj = self.pool.get('res.partner')
        st = self.browse(cr, uid, ids, context=context)[0]
        company_id = st.company_id.id
        actual = self.browse(cr, uid, ids, context=context)[0]
        period_w = actual.period_id
        journal = actual.journal_id
        if actual.bs_line_ids and actual.bs_line_ids[0].aml_ids:
            raise osv.except_osv(_("Warning"), _(
                "You can not re-create account move's, modify manually on\
                 lines where you need do something or delete lines and start\
                 again (remember delete the account move related)"))

        am_id = am_obj.create(
            cr, uid, {'ref': 'From File %s %s' % (st.fname, st.from_to_file),
                             'period_id': period_w.id,
                             'journal_id': journal.id,
                             'date': actual.date,
                             'narration': '''
                                    Account move created with\
                                     importation from file %s
                                 ''' % (st.fname),
                      }, context=context)
        self.write(cr, uid, ids, {'move': am_id}, context=context)
        range_dates = self._get_date_range(cr, uid, ids, context=context)
        ini_period = p_obj.find(cr, uid, range_dates[
                                0], context={'company_id': company_id})
        end_period = p_obj.find(cr, uid, range_dates[
                                1], context={'company_id': company_id})
        if ini_period != end_period:
            raise osv.except_osv(_("Warning"), _(
                "You can not make a bank reconcilation for bank moves with\
                 dates on different periods"))

        if ini_period != end_period != [period_w.id]:
            raise osv.except_osv(_("Warning"), _(
                "You can not make a bank reconcilation in a period different\
                 to the period indicated on files, please select correct\
                 period it should be %s " % (ini_period and ini_period[0])))

        for bsl in st.bs_line_ids:

            am_id = am_obj.create(
                cr, uid, {
                    'ref': 'From File %s %s' % (st.fname, st.from_to_file),
                    'period_id': period_w.id,
                    'journal_id': journal.id,
                    'date': actual.date,
                    'narration': '''
                        Account move created with importation from file %s
                                 ''' % (st.fname),
                }, context=context)

            acc_id = bsl.debit and st.journal_id.default_credit_account_id.id\
                or st.journal_id.default_debit_account_id.id
            prev = self.set_counterpart(
                cr, uid, ids, context={'bsl_id': bsl.id})
            payrec_id = prev[0]
            pcp_id = prev[1]
            if bsl.debit:
                payrec_id = pcp_id and partner_obj.browse(
                    cr, uid, pcp_id, context=context
                ).property_account_payable.id or payrec_id
            if bsl.credit:
                payrec_id = pcp_id and partner_obj.browse(
                    cr, uid, pcp_id, context=context
                ).property_account_receivable.id or payrec_id
            if not journal.currency or\
                    journal.currency.id == journal.company_id.currency_id.id:
                aml_obj.create(cr, uid, {'move_id': am_id,
                                         'name': bsl.name,
                                         'date': bsl.date,
                                         'credit': bsl.debit,
                                         'debit': bsl.credit,
                                         'stff_id': bsl.id,
                                         'account_id': acc_id, },
                               context=context)
                aml_obj.create(cr, uid, {'move_id': am_id,
                                         'name': bsl.name,
                                         'date': bsl.date,
                                         'credit': bsl.credit,
                                         'debit': bsl.debit,
                                         'stff_id': bsl.id,
                                         'partner_id': pcp_id,
                                         'account_id': payrec_id, },
                               context=context)
            elif journal.currency.id != journal.company_id.currency_id.id:
                amount = bsl.debit and bsl.debit or bsl.credit
                curobj = self.pool.get('res.currency')
                amount = curobj.compute(
                    cr, uid, journal.currency.id,
                    journal.company_id.currency_id.id, amount, context=context)
                aml_obj.create(cr, uid, {'move_id': am_id,
                                         'name': bsl.name,
                                         'date': bsl.date,
                                         'credit': bsl.debit and
                                         amount or 0.00,
                                         'debit': bsl.credit and
                                         amount or 0.00,
                                         'stff_id': bsl.id,
                                         'amount_currency': bsl.debit and
                                         bsl.debit or bsl.credit,
                                         'account_id': acc_id, },
                               context=context)
                aml_obj.create(cr, uid, {'move_id': am_id,
                                         'name': bsl.name,
                                         'date': bsl.date,
                                         'credit': bsl.credit and
                                         amount or 0.00,
                                         'debit': bsl.debit and
                                         amount or 0.00,
                                         'partner_id': pcp_id,
                                         'stff_id': bsl.id,
                                         'amount_currency': bsl.debit and
                                         bsl.debit or bsl.credit,
                                         'account_id': payrec_id, },
                               context=context)
            bsl.write({'move_id': am_id, 'counterpart_id': payrec_id,
                       'partnercounterpart_id': pcp_id and pcp_id or False})

        self.log(cr, uid, st.id, _('Account Move Temporary For this Statement \
                                    Id Was Created is created %s ') % (st.id))
        am_obj.log(cr, uid, am_id, _(
            'Account Move Temporary is created %s ') % (am_id))
        return True

    def read_file(self, cr, uid, ids, context=None):
        att_obj = self.pool.get('ir.attachment')
        file_xls_ids = att_obj.search(cr, uid, [
            ('res_model', '=', 'account.bank.statement'),
            ('res_id', 'in', ids)])
        if len(file_xls_ids) != 1:
            raise osv.except_osv(_('Warning'),
                                 _('I found quatity of attachments <> 1 ! \
            Please Attach JUST One XLS file to this bank statement.'))
        file_xls_brw = att_obj.browse(cr, uid, file_xls_ids, context=context)
        if len(file_xls_ids) == 1:
            checkfilename = file_xls_brw[0].datas_fname and file_xls_brw[
                0].datas_fname.endswith('.xls')
            if checkfilename:
                fname_ = '/tmp/%s' % (file_xls_brw[0].datas_fname)
                f = open(fname_, 'w')
                f.write(base64.b64decode(file_xls_brw[0].datas))
                f.close()
                doc = xlrd.open_workbook(fname_)
                sheet = doc.sheet_by_index(0)
                context.update({'xls_sheet': sheet})
                if self.file_verify_cr(cr, uid, ids, context=context):
                    if self.write_file(cr, uid, ids, context=context):
                        self.write(cr, uid, ids, {'fname': file_xls_brw[
                                   0].datas_fname}, context=context)
                        self.set_date_period(cr, uid, ids, context=context)
            else:
                raise osv.except_osv(_('Warning'),
                                     _('File Must be an XLS file ! \
                    Please verify save as correctly in excel your exported\
                    file from bank statement'))
        file_xls_brw = att_obj.browse(cr, uid, file_xls_ids, context=context)
        return True


class BankStatementImportedLines(osv.Model):

    """OpenERP Model : ClassName
    """

    _name = 'bank.statement.imported.lines'
    _description = 'Imported lines for banks files'

    # def _balance(self, cr, uid,ids,field_name,args,context=None):
    # res = {}
    #
    # for i in ids:
    # debit = 0.0
    # amt_unt = 0.0
    # bsil_brw = self.browse(cr,uid,i,context=context)
    # counterpart_id = bsil_brw.counterpart_id
    # for aml in bsil_brw.aml_ids:
    # if aml.account_id == counterpart_id:
    # debit += aml.debit or aml.credit
    # for inv in bsil_brw.invoice_ids:
    # if inv.account_id == counterpart_id:
    # amt_unt += inv.amount_total
    # for amls in bsil_brw.acc_move_line_ids:
    # if amls.account_id == counterpart_id:
    # amt_unt+=amls[aml.debit and 'credit' or 'debit']
    #
    # res[i]=debit-amt_unt
    # return res
    _columns = {
        'name': fields.char('Description', size=255, required=True,
                            readonly=False),
        'date': fields.date('Date', required=True),
        'numdocument': fields.char('Num Document', size=64, required=True,
                                   readonly=False),
        'debit': fields.float('Debit',
                              digits_compute=dp.get_precision(
                                  'Account'), required=True),
        'invo_move_line': fields.boolean('Chek',
                                         help='Chek if invoice and account move line exist'),
        'move_id': fields.many2one('account.move', 'Account Move'),
        'credit': fields.float('Credit',
                               digits_compute=dp.get_precision(
                                   'Account'), required=True),
        'office': fields.char('Office', size=16, required=False,
                              readonly=False),
        'bank_statement_id': fields.many2one('account.bank.statement',
                                             'Bank Statement', required=True),
        'acc_move_line_ids': fields.many2many('account.move.line',
                                              'account_move_line_rel', 'aml_ids', 'aml_id'),
        'company_id': fields.many2one('res.company', 'Company',
                                      required=False),
        'aml_ids': fields.one2many('account.move.line', 'stff_id',
                                   'Account Move Lines'),
        'counterpart_id': fields.many2one('account.account',
                                          'Account Counterpart', required=False,
                                          help="This will be the account to make the account move line as\
             counterpart."),
        'partnercounterpart_id': fields.many2one('res.partner',
                                                 'Partner Counterpart', required=False,
                                                 help="This will be the partner to make written on the\
             account move line as counterpart., if you change this value,\
             the account payable or receivable will be automatic selected on\
             Account Move Lines related, specially usefull when you pay\
             several things in the same invoice, Petty cash for example, just\
             select your partner petty cash"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done')
        ], 'State',
            help='If this bank statement line is confirmed or not, to help\
             useability issues',
            readonly=True, select=True),
        'invoice_ids': fields.many2many('account.invoice', 'bs_invoice_rel',
                                        'st_id_id', 'invoice_id', 'Invoices',
                                        help="Invoices to be reconciled with this line",
                                        ),  # TODO: Resolve: We should use date as filter, is a question of POV
        #'balance':fields.function(_balance,method=True,digits_compute=dp.get_precision('Account'),type='float',string='Balance',store=False),
    }

    _defaults = {
        'name': lambda *a: None,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').
        _company_default_get(cr, uid, 'account.account', context=c),
        'state': 'draft',
    }

    # def explode_aml(self,cr,uid,ids,,context=None):
    # if context is None:
    # context={}
    def change_account(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        acc_journal = []
        bank_line_brw = self.browse(cr, uid, ids, context=context)
        account_move_line_obj = self.pool.get('account.move.line')
        for line in bank_line_brw:

            if line.invoice_ids or line.acc_move_line_ids:
                raise osv.except_osv(_("Warning"), _(
                    "You can not change account because this bank statement\
                     have documents"))

            if line.state != 'done':

                for aml in line.aml_ids:
                    acc_journal.append(
                        line.bank_statement_id.journal_id and
                        line.bank_statement_id.
                        journal_id.default_debit_account_id and
                        line.bank_statement_id.
                        journal_id.default_debit_account_id.id)

                    acc_journal.append(
                        line.bank_statement_id.journal_id and
                        line.bank_statement_id.journal_id.
                        default_credit_account_id and
                        line.bank_statement_id.journal_id.
                        default_credit_account_id.id)

                    if aml.account_id and aml.account_id.id not in acc_journal:
                        account_move_line_obj.copy(
                            cr, uid, aml.id, {
                                'account_id': line.counterpart_id and
                                line.counterpart_id.id})
                        account_move_line_obj.unlink(
                            cr, uid, [aml.id], context=context)

    def prepare(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        aml = False
        total = 0
        invoice_obj = self.pool.get('account.invoice')
        account_move_line_obj = self.pool.get('account.move.line')
        for abs_brw in self.browse(cr, uid, ids, context=context):
            for line in abs_brw.aml_ids:
                if context.get('button_confirm'):
                    if line.account_id == abs_brw.counterpart_id and not\
                            line.reconcile_partial_id and not\
                            line.reconcile_id:
                        aml = line

                else:
                    if line.account_id == abs_brw.counterpart_id:
                        aml = line
            if aml:

                aml_ids = [line.id for i in abs_brw.invoice_ids
                           if i.state == 'open'
                           for line in i.move_id.line_id
                           if i.account_id.id == line.account_id.id and not
                           line.reconcile_id]

                aml_ids += [i.id for i in abs_brw.acc_move_line_ids]

                aml_ids = aml_ids and account_move_line_obj.search(cr, uid, [
                    ('id', 'in', aml_ids)], order='date asc', context=context)

                if aml.debit and not context.get('cancel', False) or\
                        aml.credit and not context.get('cancel', False):

                    total = aml.debit or aml.credit
                    for aml_id in account_move_line_obj.browse(cr, uid,
                                                               aml_ids, context=context):
                        if aml_id.date_maturity and\
                                aml_id.date_maturity < abs_brw.date or True:
                            partner_id = aml_id.partner_id and\
                                aml_id.partner_id.id
                            if total > (aml_id.reconcile_partial_id and
                                        aml_id.invoice and
                                        aml_id.invoice.residual or
                                        aml_id[aml.debit and 'credit' or 'debit']):
                                total = total - (
                                    aml_id.reconcile_partial_id and
                                    aml_id.invoice and
                                    aml_id.invoice.residual or aml_id[
                                        aml.debit and
                                        'credit' or 'debit'])
                                res.append(
                                    (account_move_line_obj.copy(
                                        cr, uid, aml.id, {
                                            'partner_id': aml_id.partner_id and
                                            aml_id.partner_id.id,
                                            '%s' % (aml.debit > 0 and
                                                    'debit' or aml.credit > 0 and
                                                    'credit'):
                                            (aml_id.reconcile_partial_id and
                                                aml_id.invoice and
                                                aml_id.invoice.residual or
                                                aml_id[aml.debit and
                                                       'credit' or 'debit'])}),
                                     aml_id.id))

                            elif total > 0 and (aml_id.reconcile_partial_id and
                                                aml_id.invoice and aml_id.invoice.residual or
                                                aml_id[aml.debit and
                                                       'credit' or 'debit']) >= total:
                                res.append(
                                    (account_move_line_obj.copy(
                                        cr, uid, aml.id, {
                                            'partner_id': aml_id.partner_id and
                                            aml_id.partner_id.id,
                                            '%s' % (aml.debit > 0 and
                                                    'debit' or aml.credit > 0 and
                                                    'credit'): total}),
                                     aml_id.id))
                                total = 0

                            elif total <= 0:
                                break

                if total > 0 and res:
                    account_move_line_obj.copy(
                        cr, uid, aml.id, {'partner_id': partner_id,
                                          '%s' % (aml.debit > 0 and
                                                  'debit' or aml.credit > 0 and 'credit'): total})
                res and account_move_line_obj.unlink(
                    cr, uid, [aml.id], context=context)

            if context.get('cancel', False) and aml:
                invoice_ids = [i.id for i in abs_brw.invoice_ids]
                move_ids = [d.id for d in abs_brw.acc_move_line_ids]
                for invoice in invoice_obj.browse(
                        cr, uid, invoice_ids, context=context):
                    if abs_brw.move_id:
                        res.append(
                            account_move_line_obj.search(
                                cr, uid, [('move_id', '=', abs_brw.move_id.id),
                                          ('account_id', '=', invoice.account_id.id)]))

                    else:
                        res.append(
                            account_move_line_obj.search(
                                cr, uid, [('invoice', 'in', invoice_ids),
                                          ('account_id', '=',
                                           invoice.account_id.id),
                                          ]))
                    res.append('%s' % (
                        aml.debit > 0 and
                               'debit' or aml.credit > 0 and 'credit'))
                    break

                for move in account_move_line_obj.browse(
                        cr, uid, move_ids, context=context):
                    res.append(
                        account_move_line_obj.search(
                            cr, uid, [('move_id', '=', abs_brw.move_id.id),
                                      ('account_id', '=', move.account_id.id)]))
                    res.append('%s' % (
                        aml.debit > 0 and
                        'debit' or aml.credit > 0 and 'credit'))
                    break

                res and [res[0].append(
                    i.id) for i in abs_brw.acc_move_line_ids]

                # res.append(aml.id)
        return res

    def begin_move(self, cr, uid, ids, type, context=None):
        if context is None:
            context = {}
        total = 0
        aml_id = []
        account_move_line_obj = self.pool.get('account.move.line')
        for abs_brw in self.browse(cr, uid, ids, context=context):
            for line in abs_brw.aml_ids:
                total = total + line[type]
                # total = total + eval('line.%s'%type)

                line[type] and aml_id.append(line.id)
                # eval('line.%s'%type) and aml_id.append(line.id)

        account_move_line_obj.copy(cr, uid, aml_id[
                                   0], {type: total, 'partner_id': []})
        account_move_line_obj.unlink(cr, uid, aml_id, context=context)

        return True

    def invoice_or_move_line(self, cr, uid, ids, invoice_ids,
                             acc_move_line_ids, context=None):
        if context is None:
            context = {}

        res = {'value': {}}
        if invoice_ids and\
                invoice_ids[0][2] or acc_move_line_ids and acc_move_line_ids[0][2]:
            res['value'].update({'invo_move_line': True})

        else:
            res['value'].update({'invo_move_line': False})

        return res

    def button_validate(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_obj = self.pool.get('account.move')

        context.update({'cancel': True})
        for abs_brw in self.browse(cr, uid, ids, context=context):
            account_move_obj.button_cancel(cr, uid, [abs_brw.move_id
                                                     and abs_brw.move_id.id], context=context)

        res = self.prepare(cr, uid, ids, context=context)
        if res and res[0]:

            account_move_line_obj._remove_move_reconcile(
                cr, uid, res[0], context=context)
            self.begin_move(cr, uid, ids, res[1], context=context)
            return self.write(cr, uid, ids, {'state': 'draft'},
                              context=context)

        return True

    def button_setinvoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        recon = []
        account_move_line_obj = self.pool.get('account.move.line')
        account_move = self.pool.get('account.move')

        for abs_brw in self.browse(cr, uid, ids, context=context):
            res = self.prepare(cr, uid, ids, context=context)

            if res:
                for reconcile in res:
                    recon = []
                    recon.append(reconcile[0])
                    recon.append(reconcile[1])
                    account_move_line_obj.reconcile_partial(
                        cr, uid, recon, 'manual', context=context)
                self.button_validate(cr, uid, ids, context=context)
                account_move.button_validate(cr, uid, [
                                             abs_brw.move_id and
                                             abs_brw.move_id.id],
                                             context=context)
        return {}


class AccountMoveLine(osv.Model):

    _inherit = 'account.move.line'
    _columns = {
        'stff_id': fields.many2one('bank.statement.imported.lines',
                                   'Statement from File line'),
    }
