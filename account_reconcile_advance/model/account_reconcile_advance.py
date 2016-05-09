# coding: utf-8
from openerp.osv import osv, fields
from openerp.tools.translate import _


class AccountMoveLine(osv.Model):
    _inherit = 'account.move.line'

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                context=None, count=False, access_rights_uid=None):

        move_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')

        lista_invoice = context.get('has_invoice_ids', False)
        lista_invoice = lista_invoice and lista_invoice[0] or []
        lista_invoice = lista_invoice and lista_invoice[2] or []

        lista_voucher = context.get('has_voucher_ids', False)
        lista_voucher = lista_voucher and lista_voucher[0] or []
        lista_voucher = lista_voucher and lista_voucher[2] or []

        no_incluir = ['id', 'not in', []]
        l_ids = []

        if lista_invoice:
            context.pop('has_invoice_ids')
            for inv in lista_invoice:
                moves_up = move_obj.search(cr, uid, [('invoice', '=', inv)])
                l_ids = l_ids + moves_up

        if lista_voucher:
            context.pop('has_voucher_ids')
            for vou in lista_voucher:
                vouchers_up = voucher_obj.browse(cr, uid, vou, context=context)
                mv = vouchers_up.move_id.id
                moves_up = move_obj.search(cr, uid, [('move_id', '=', mv)])
                l_ids = l_ids + moves_up

        no_incluir[2] += l_ids

        args.append(no_incluir)

        return super(AccountMoveLine, self)._search(
            cr,
            uid,
            args,
            offset=offset,
            limit=limit,
            order=order,
            context=context,
            count=count,
            access_rights_uid=access_rights_uid)


class AccountReconcileAdvance(osv.Model):

    """description"""

    _name = 'account.reconcile.advance'

    # pylint: disable=W0621
    def default_get(self, cr, uid, fields, context=None):
        """Returns default values for the fields
        """
        context = context or {}

        res = super(AccountReconcileAdvance, self).default_get(
            cr, uid, fields, context=context)
        if not context.get('default_type', False):
            res.update({'type': 'pay'})

        return res

    # pylint: disable=W8105
    _columns = {
        'name': fields.char(
            'Name',
            size=256,
            help='Name of This Advance Document'),
        'date': fields.date('Date', help='Document Date'),
        'date_post': fields.date(
            'Accounting Date',
            help='Date to be used in Journal Entries when posted'),
        'type': fields.selection(
            [('pay', 'Payment'), ('rec', 'Receipt')],
            help='State'),
        'state': fields.selection(
            [('draft', 'Draft'), ('cancel', 'Cancel'), ('done', 'Done')],
            help='State'),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            help='Company'),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            help='Advance Partner'),
        'period_id': fields.many2one(
            'account.period',
            'Accounting Period',
            help='Period where Journal Entries will be posted'),
        'journal_id': fields.many2one(
            'account.journal',
            'Journal',
            help='Accounting Journal where Entries will be posted'),
        'move_id': fields.many2one(
            'account.move',
            'Accounting Entry',
            help='Accounting Entry'),
        'invoice_ids': fields.many2many(
            'account.invoice',
            'ara_invoice_rel',
            'ara_id',
            'inv_id',
            'Invoices',
            help='Invoices to be used in this Advance'),
        'voucher_ids': fields.many2many(
            'account.voucher',
            'ara_voucher_rel',
            'ara_id',
            'voucher_id',
            'Advances',
            help='Advances to be used'),
        'ai_aml_ids': fields.many2many(
            'account.move.line',
            'ara_ai_aml_rel',
            'ara_id',
            'aml_id',
            'Invoice Entry Lines',
            help=''),
        'av_aml_ids': fields.many2many(
            'account.move.line',
            'ara_av_aml_rel',
            'ara_id',
            'aml_id',
            'Advance Entry Lines',
            help=''),
    }
    _defaults = {
        'state': 'draft',
        'company_id': lambda s, c, u, cx: s.pool.get('res.users').browse(
            c, u, u, cx).company_id.id,
        'date': fields.date.today
    }

    def invoice_credit_lines(self, cr, uid, ids, amount, am_id=None,
                             account_id=False, partner_id=False,
                             date=None, context=None):
        """Invoice credit lines
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ara_brw = self.browse(cr, uid, ids[0], context=context)
        account_id = account_id or \
            ara_brw.partner_id.property_account_payable.id
        partner_id = ara_brw.partner_id.id
        date = date or ara_brw.date_post or fields.date.today()
        period_id = ara_brw.period_id or ara_brw.period_id.id
        vals = {
            'move_id': am_id or ara_brw.move_id.id,
            'journal_id': ara_brw.journal_id.id,
            'date': date,
            'period_id': period_id or self.pool.get('account.period').find(
                cr, uid, dt=date, context=context)[0],
            'debit': 0.0,
            'name': _('Advance Applied'),
            'partner_id': partner_id,
            'account_id': account_id,
            'credit': amount,
        }
        return aml_obj.create(cr, uid, vals, context=context)

    def invoice_debit_lines(self, cr, uid, ids, amount, am_id=None,
                            account_id=False, partner_id=False, date=None,
                            context=None):
        """Invoice debit lines
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ara_brw = self.browse(cr, uid, ids[0], context=context)
        account_id = account_id or \
            ara_brw.partner_id.property_account_payable.id
        partner_id = ara_brw.partner_id.id
        date = date or ara_brw.date_post or fields.date.today()
        period_id = ara_brw.period_id or ara_brw.period_id.id
        vals = {
            'move_id': am_id or ara_brw.move_id.id,
            'journal_id': ara_brw.journal_id.id,
            'date': date,
            'period_id': period_id or self.pool.get('account.period').find(
                cr, uid, dt=date, context=context)[0],
            'debit': amount,
            'name': _('Invoice Payment with Advance'),
            'partner_id': partner_id,
            'account_id': account_id,
            'credit': 0.0,
        }
        return aml_obj.create(cr, uid, vals, context=context)

    def validate_data(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ara_brw = self.browse(cr, uid, ids[0], context=context)
        res = []
        res.append((ara_brw.invoice_ids or ara_brw.ai_aml_ids) and
                   True or False)
        res.append((ara_brw.voucher_ids or ara_brw.av_aml_ids) and True or
                   ara_brw.av_aml_ids and True or False)

        if all(res):
            return True
        else:
            raise osv.except_osv(_('Error!'), _("Please Field the Invoices & "
                                                "Advances Fields"))

    def payment_reconcile(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        self.validate_data(cr, uid, ids, context=context)
        inv_obj = self.pool.get('account.invoice')
        aml_obj = self.pool.get('account.move.line')
        am_obj = self.pool.get('account.move')
        res = {}

        # El documento con los datos a conciliar
        ara_brw = self.browse(cr, uid, ids[0], context=context)

        # Se preparan los valores para el account.move que se va a crear
        am_vals = am_obj.account_move_prepare(
            cr,
            uid,
            ara_brw.journal_id.id,
            date=ara_brw.date_post,
            ref=ara_brw.name,
            company_id=ara_brw.company_id.id,
            context=context)

        # Se crea el acocunt.move
        am_id = am_obj.create(cr, uid, am_vals, context=context)

        # Se obtienen las facturas incluidas en la conciliacion, las facturas
        # (deudas)
        invoice_ids = [inv.id for inv in ara_brw.invoice_ids]
        invoice_ids = inv_obj.search(cr, uid, [('id', 'in', invoice_ids)],
                                     order='date_due asc', context=context)

        # Se obtienen los asientos contables (deudores)
        ai_aml_ids = ara_brw.ai_aml_ids and [
            k.id for k in ara_brw.ai_aml_ids] or []

        av_aml_ids = []
        # Se obtienen los asientos contables de los anticipos (vouchers,
        # credito)
        for av_brw in ara_brw.voucher_ids:
            av_aml_ids += [l.id for l in av_brw.move_ids if
                           l.account_id.type == (
                               ara_brw.type == 'pay' and
                               'payable' or 'receivable') and not
                           l.reconcile_id and not l.reconcile_partial_id]

        # Se unen los asientos contables de los anticipos con los asientos
        # contables escogidos man.
        av_aml_ids += ara_brw.av_aml_ids and [
            l.id for l in ara_brw.av_aml_ids] or []
        av_aml_ids = list(set(av_aml_ids))

        # Se ordenan en forma ascendente
        av_aml_ids = aml_obj.search(cr, uid, [('id', 'in', av_aml_ids)],
                                    order='date asc', context=context)

        # In the future this should be like this
        # while (invoice_ids or ai_aml_ids) and av_aml_ids:
        inv_sum = 0.0
        aml_sum = 0.0
        aml_grn_sum = 0.0
        mem_av_aml_ids = av_aml_ids and av_aml_ids[:] or []
        lines_2_rec = []
        lines_2_par = []
        aml2_brw = None

        inv_brw = None
        aml2_brw = None

        while (invoice_ids or ai_aml_ids or inv_sum) and \
                (av_aml_ids or aml_sum):
            # Get money to pay debts. Whenever we are cashless or our debts are
            # greater than the money we have: Use the ATM. And while there is
            # money

            # Let us pick our debt
            if invoice_ids:
                if not inv_sum:
                    #               BE AWARE MULTICURRENCY MISSING HERE
                    inv_brw = inv_obj.browse(
                        cr, uid, invoice_ids.pop(0), context=context)
                    inv_sum = inv_brw.residual

            elif ai_aml_ids:
                if not inv_sum:
                    aml2_brw = aml_obj.browse(
                        cr, uid, ai_aml_ids.pop(0), context=context)
                    inv_sum = aml2_brw[ara_brw.type ==
                                       'pay' and 'credit' or 'debit']

            # Agarrar dinero mas viejo
            while(aml_sum == 0.0 or inv_sum > aml_sum) and av_aml_ids:
                aml_brw = aml_obj.browse(
                    cr, uid, av_aml_ids.pop(0), context=context)
                aml_sum += aml_brw[ara_brw.type ==
                                   'pay' and 'debit' or 'credit']
                aml_grn_sum += aml_brw[ara_brw.type ==
                                       'pay' and 'debit' or 'credit']  # unused
#               grouping by account_id should be done here

#           While we have plenty of money to pay our debts and there are debts
#           to pay. Let us pay them!
            while inv_sum and inv_sum <= aml_sum:

                if inv_brw:
                    #               Let us spend our money
                    aml_sum -= inv_sum
#               BE AWARE MULTICURRENCY MISSING HERE
                    get_aml = ara_brw.type == 'pay' and \
                        self.invoice_debit_lines or self.invoice_credit_lines
                    payid = get_aml(cr, uid, ids, inv_sum,
                                    account_id=inv_brw.account_id.id,
                                    am_id=am_id, context=context)
                    inv_sum = 0.0
                    iamls = [line.id for line in inv_brw.move_id.line_id if
                             line.account_id.type == (ara_brw.type == 'pay' and
                                                      'payable' or
                                                      'receivable')]
                    pamls = [line.id for line in inv_brw.payment_ids]
                    lines_2_rec.append(iamls + pamls + [payid])
                    inv_brw = None

                elif aml2_brw:
                    # Let us spend our money
                    aml_sum -= inv_sum
#               BE AWARE MULTICURRENCY MISSING HERE
                    get_aml = ara_brw.type == 'pay' and \
                        self.invoice_debit_lines or self.invoice_credit_lines
#               Creates its own mirror and fully reconciliates them
                    payid = get_aml(cr, uid, ids, inv_sum,
                                    account_id=aml2_brw.account_id.id,
                                    am_id=am_id, context=context)
                    inv_sum = 0.0
                    lines_2_rec.append([payid, aml2_brw.id])
                    aml2_brw = None

#           ATM has run out of cash however we still have cash though we are
#           not able to fully pay our debts. Let us use the remaining
            if not av_aml_ids and aml_sum and inv_sum > aml_sum:
                #   Payments are over. Last line to invoice is made with the
                #   aml_sum
                get_aml = ara_brw.type == 'pay' and \
                    self.invoice_debit_lines or self.invoice_credit_lines

                if inv_brw:
                    payid = get_aml(cr, uid, ids, aml_sum,
                                    account_id=inv_brw.account_id.id,
                                    am_id=am_id, context=context)
                    iamls = [line.id for line in inv_brw.move_id.line_id if
                             line.account_id.type == (ara_brw.type == 'pay' and
                                                      'payable' or
                                                      'receivable')]
                    pamls = [line.id for line in inv_brw.payment_ids]
                    lines_2_par.append(iamls + pamls + [payid])
#               BE AWARE MULTICURRENCY MISSING HERE
                else:
                    payid = get_aml(cr, uid, ids, aml_sum,
                                    account_id=aml2_brw.account_id.id,
                                    am_id=am_id, context=context)
                    lines_2_par.append([payid, aml2_brw.id])
#               BE AWARE MULTICURRENCY MISSING HERE

                aml_sum = 0.0

        if av_aml_ids:
            #           spare aml's. We will do nothing with these lines
            #           these were the advances we did not use
            pass

        used_aml_ids = list(set(mem_av_aml_ids) - set(av_aml_ids))

        adv_2_rec = []
        if used_aml_ids:

            #   when reconciling among used_aml_ids, those ids should be
            #   grouped by account_id, take care of the last used_aml_ids,
            #   because is with that the aml_sum (debit) should be created.
            #   aml_grn_sum => credit
            #   aml_sum => debit
            if aml_sum:
                # if some remaining money get around it will not be reconciled
                # This should be sent to a method in order to be captured
                if ara_brw.type == 'pay':
                    acc_id = ara_brw.partner_id.property_account_payable.id
                else:
                    acc_id = ara_brw.partner_id.property_account_receivable.id
                get_aml = ara_brw.type == 'pay' and \
                    self.invoice_debit_lines or self.invoice_credit_lines
                get_aml(cr, uid, ids, aml_sum, account_id=acc_id,
                        am_id=am_id, context=context)

            get_aml = ara_brw.type == 'pay' and self.invoice_credit_lines or \
                self.invoice_debit_lines
            for aml_brw in aml_obj.browse(cr, uid, used_aml_ids,
                                          context=context):
                adv_2_rec.append([get_aml(cr, uid, ids,
                                          aml_brw[ara_brw.type ==
                                                  'pay' and 'debit' or
                                                  'credit'],
                                          account_id=aml_brw.account_id.id,
                                          am_id=am_id, context=context),
                                  aml_brw.id])

        for line_pair in adv_2_rec + lines_2_rec:
            if not line_pair:
                continue
            aml_obj.reconcile(
                cr, uid, line_pair, 'manual', context=context)

        for line_pair in lines_2_par:
            if not line_pair:
                continue
            aml_obj.reconcile_partial(
                cr, uid, line_pair, 'manual', context=context)

        ara_brw.write({'move_id': am_id, 'state': 'done'})

        return res


class AccountVoucher(osv.Model):
    _inherit = 'account.voucher'

    def _get_advance(self, cr, uid, ids, name, args, context=None):
        """Check if there is at least one payable or receivable line not
        reconciled at all, if so it will be regarded as an advance
        """
        context = context or {}
        res = {}.fromkeys(ids, False)
        for av_brw in self.browse(cr, uid, ids, context=context):
            if av_brw.state != 'posted':
                continue
            i = [l.reconcile_id and True or l.reconcile_partial_id and True or
                 False
                 for l in av_brw.move_ids
                 if l.account_id.type in ('receivable', 'payable')]
            res[av_brw.id] = not all(i) if i else False
        return res

    def _get_voucher_advance(self, cr, uid, ids, context=None):
        context = context or {}
        res = set()
        aml_obj = self.pool.get('account.move.line')
        for element in aml_obj.browse(cr, uid, ids, context=context):
            if not element.move_id:
                continue
            res.add(element.move_id.id)
        res = list(res)

        if not res:
            return []

        av_obj = self.pool.get('account.voucher')
        return av_obj.search(cr,
                             uid,
                             [('move_id', 'in', res)],
                             context=context)

    # pylint: disable=W8105
    _columns = {
        'advance': fields.function(_get_advance,
                                   method=True,
                                   string='Is an Advance?',
                                   store={
                                       'account.voucher': (
                                           lambda s,
                                           c,
                                           u,
                                           ids,
                                           cx: ids,
                                           ['move_ids', 'move_id', 'state'],
                                           15),
                                       'account.move.line': (
                                           _get_voucher_advance,
                                           ['reconcile_id',
                                            'reconcile_partial_id'],
                                           30)
                                   },
                                   help='If the payable or receivable are '
                                   'not fully reconcile then it is advance',
                                   type='boolean')
    }
