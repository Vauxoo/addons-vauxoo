# coding: utf-8
from openerp.osv import osv, fields

QUERY_REC_AML = '''
SELECT aml_id, id
FROM
    (SELECT
        l.id AS aml_id
        , l.reconcile_id AS p_reconcile_id
        , l.reconcile_partial_id AS p_reconcile_partial_id
    FROM account_move_line l
    INNER JOIN account_journal j ON l.journal_id = j.id
    INNER JOIN account_account a ON l.account_id = a.id
    WHERE
        l.state = 'valid'
        AND l.credit != 0.0
        AND a.type = 'receivable'
        AND j.type IN ('cash', 'bank')
        AND (l.reconcile_id IS NOT NULL OR l.reconcile_partial_id IS NOT NULL)
    ) AS PAY_VIEW,
    (SELECT
        l.id
        , l.reconcile_id AS i_reconcile_id
        , l.reconcile_partial_id AS i_reconcile_partial_id
    FROM account_move_line l
    INNER JOIN account_account a ON l.account_id = a.id
    INNER JOIN account_journal j ON l.journal_id = j.id
    WHERE
        l.state = 'valid'
        AND l.debit != 0.0
        AND a.type = 'receivable'
        AND j.type IN ('sale')
        AND (l.reconcile_id IS NOT NULL OR l.reconcile_partial_id IS NOT NULL)
    ) AS INV_VIEW
WHERE
    (p_reconcile_id = i_reconcile_id
    OR
    p_reconcile_partial_id = i_reconcile_partial_id)
'''

QUERY_REC_INVOICE = '''
SELECT id, invoice_id
FROM
    (SELECT
        l.id
        , l.reconcile_id AS p_reconcile_id
        , l.reconcile_partial_id AS p_reconcile_partial_id
    FROM account_move_line l
    INNER JOIN account_journal j ON l.journal_id = j.id
    INNER JOIN account_account a ON l.account_id = a.id
    WHERE
        l.state = 'valid'
        AND l.credit != 0.0
        AND a.type = 'receivable'
        AND j.type IN ('cash', 'bank')
        AND (l.reconcile_id IS NOT NULL OR l.reconcile_partial_id IS NOT NULL)
    ) AS PAY_VIEW,
    (SELECT
        i.id AS invoice_id
        , l.reconcile_id AS i_reconcile_id
        , l.reconcile_partial_id AS i_reconcile_partial_id
    FROM account_move_line l
    INNER JOIN account_invoice i ON l.move_id = i.move_id
    INNER JOIN account_account a ON l.account_id = a.id
    INNER JOIN account_journal j ON l.journal_id = j.id
    WHERE
        l.state = 'valid'
        AND l.debit != 0.0
        AND a.type = 'receivable'
        AND j.type IN ('sale')
        AND (l.reconcile_id IS NOT NULL OR l.reconcile_partial_id IS NOT NULL)
    ) AS INV_VIEW
WHERE
    (p_reconcile_id = i_reconcile_id
    OR
    p_reconcile_partial_id = i_reconcile_partial_id)
'''


class AccountMoveLine(osv.Model):

    def _get_reconciling_aml(self, cr, uid, ids, fieldname, arg, context=None):
        res = {}.fromkeys(ids, None)
        context = context or {}
        sub_query = 'AND aml_id IN (%s)' % ', '.join([str(idx) for idx in ids])
        cr.execute(QUERY_REC_AML + sub_query)
        rex = cr.fetchall()

        for aml_id, rec_aml in rex:
            res[aml_id] = rec_aml

        return res

    def _rec_aml_search(self, cursor, user, obj, name, args, context=None):
        if not args:
            return []
        aml_obj = self.pool.get('account.move.line')
        i = 0
        while i < len(args):
            fargs = args[i][0].split('.', 1)
            if len(fargs) > 1:
                args[i] = (fargs[0], 'in', aml_obj.search(
                    cursor, user, [(fargs[1], args[i][1], args[i][2])]))
                i += 1
                continue
            if isinstance(args[i][2], basestring):
                res_ids = aml_obj.name_search(
                    cursor, user, args[i][2], [], args[i][1])
                args[i] = (args[i][0], 'in', [xxx[0] for xxx in res_ids])
            i += 1
        qu1, qu2 = [], []
        for xxx in args:
            if xxx[1] != 'in':
                if (xxx[2] is False) and (xxx[1] == '='):
                    qu1.append('(id IS NULL)')
                elif (xxx[2] is False) and (xxx[1] == '<>' or xxx[1] == '!='):
                    qu1.append('(id IS NOT NULL)')
                else:
                    qu1.append('(id %s %s)' % (xxx[1], '%s'))
                    qu2.append(xxx[2])
            elif xxx[1] == 'in':
                if len(xxx[2]) > 0:
                    qu1.append('(id IN (%s))' % (
                        ','.join(['%s'] * len(xxx[2]))))
                    qu2 += xxx[2]
                else:
                    qu1.append(' (False)')
        if qu1:
            qu1 = ' AND' + ' AND'.join(qu1)
        else:
            qu1 = ''
        cursor.execute(QUERY_REC_AML + qu1, qu2)
        res = cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]

    def _get_reconciling_invoice(self, cr, uid, ids, fieldname, arg,
                                 context=None):
        res = {}.fromkeys(ids, None)
        context = context or {}
        sub_query = 'AND id IN (%s)' % ', '.join([str(xxx) for xxx in ids])
        cr.execute(QUERY_REC_INVOICE + sub_query)
        rex = cr.fetchall()

        for aml_id, inv_id in rex:
            res[aml_id] = inv_id

        return res

    def _rec_invoice_search(self, cursor, user, obj, name, args, context=None):
        if not args:
            return []
        invoice_obj = self.pool.get('account.invoice')
        i = 0
        while i < len(args):
            fargs = args[i][0].split('.', 1)
            if len(fargs) > 1:
                args[i] = (fargs[0], 'in', invoice_obj.search(
                    cursor, user, [(fargs[1], args[i][1], args[i][2])]))
                i += 1
                continue
            if isinstance(args[i][2], basestring):
                res_ids = invoice_obj.name_search(
                    cursor, user, args[i][2], [], args[i][1])
                args[i] = (args[i][0], 'in', [xxx[0] for xxx in res_ids])
            i += 1
        qu1, qu2 = [], []
        for xxx in args:
            if xxx[1] != 'in':
                if (xxx[2] is False) and (xxx[1] == '='):
                    qu1.append('(id IS NULL)')
                elif (xxx[2] is False) and (xxx[1] == '<>' or xxx[1] == '!='):
                    qu1.append('(id IS NOT NULL)')
                else:
                    qu1.append('(id %s %s)' % (xxx[1], '%s'))
                    qu2.append(xxx[2])
            elif xxx[1] == 'in':
                if len(xxx[2]) > 0:
                    qu1.append('(id IN (%s))' % (
                        ','.join(['%s'] * len(xxx[2]))))
                    qu2 += xxx[2]
                else:
                    qu1.append(' (False)')
        if qu1:
            qu1 = ' AND' + ' AND'.join(qu1)
        else:
            qu1 = ''
        cursor.execute(QUERY_REC_INVOICE + qu1, qu2)
        res = cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]

    def _date_last_payment(self, cr, uid, ids, fieldname, arg, context=None):
        res = {}.fromkeys(ids, None)
        context = context or {}
        for aml_brw in self.browse(cr, uid, ids, context=context):
            if aml_brw.rec_aml:
                continue
            if aml_brw.reconcile_id:
                rec_aml_brws = aml_brw.reconcile_id.line_id
            elif aml_brw.reconcile_partial_id:
                rec_aml_brws = aml_brw.reconcile_partial_id.line_partial_ids
            else:
                continue
            date_last_payment = aml_brw.date_last_payment
            for raml_brw in rec_aml_brws:
                if aml_brw.id == raml_brw.id:
                    continue
                date_last_payment = raml_brw.date > date_last_payment and \
                    raml_brw.date or date_last_payment
            res[aml_brw.id] = date_last_payment

        return res

    def _get_aml_related_date(self, cr, uid, ids, context=None):
        res = set([])
        context = context or {}
        for aml_brw in self.browse(cr, uid, ids, context=context):
            if aml_brw.account_id.type != 'receivable':
                continue
            if aml_brw.journal_id.type not in ('bank', 'cash'):
                continue
            if aml_brw.credit == 0.0:
                continue
            if aml_brw.rec_aml:
                res.add(aml_brw.rec_aml.id)
            res.add(aml_brw.id)
        return res

    _inherit = 'account.move.line'

    _columns = {
        'paid_comm': fields.boolean('Paid Commission?'),
        'rec_invoice': fields.function(
            _get_reconciling_invoice,
            string='Reconciling Invoice',
            type="many2one",
            relation="account.invoice",
            fnct_search=_rec_invoice_search,
        ),
        'rec_aml': fields.function(
            _get_reconciling_aml,
            string='Reconciling Journal Item',
            type="many2one",
            relation="account.move.line",
            fnct_search=_rec_aml_search,
        ),
        'date_last_payment': fields.function(
            _date_last_payment, string='Last Payment Date', type="date",
            store={
                _inherit: (_get_aml_related_date,
                           ['reconcile_id', 'reconcile_partial_id',
                            'reconcile_ref'], 15),
            }),
    }
    _defaults = {
        'paid_comm': lambda *a: False,
    }
