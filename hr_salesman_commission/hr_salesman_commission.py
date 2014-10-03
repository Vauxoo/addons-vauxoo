import time
import openerp.netsvc as netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _

from openerp.addons.decimal_precision import decimal_precision as dp

import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import openerp.tools as tools
from tools import config
from openerp.tools.misc import currency


class salesman_commission_payment(osv.Model):
    _name = 'salesman.commission.payment'
    _description = 'Salesman Commissions due to effective payments'
    _columns = {
        'commission_number': fields.char('Number', size=64),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Salesman', required=True,
            states={'draft': [('readonly', False)]}),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year',
            required=True, states={'draft': [('readonly', False)]}),
        'period_ids': fields.many2one('account.period', 'Periods',
            required=True, states={'draft': [('readonly', False)]}),
        'payment_ids': fields.many2many('account.move.line',
            'hr_salesman_commission_payment', 'line_id', 'payment_id',
            'Payments', states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'State', select=True, readonly=True),
        'commission_rate':  fields.float('Rate(%)',
            digits_compute=dp.get_precision('Commission'), readonly=False),
        'commission_amount': fields.float('Commission',
            digits_compute=dp.get_precision('Commission'),),
        #'date_created': fields.date('Created Date'),
        #'date_due': fields.date('Due Date'),
        #'date_commissioned' : fields.date('Commissioned Date'),
        #'date_modified' fields.date('Last Modification Date'),
        # REVISAR CON MUCHO DETENIMIENTO
        #'move_line' : fields.many2one(),
        'commission_line_id': fields.one2many('salesman.commission.payment.line',
            'commission_id', 'Commission Lines', readonly=True,
            states={'draft': [('readonly', False)]}),
    }

# Copied from account.py (line 297)
    def _default_company(self, cr, uid, context={}):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid,
                                                [('parent_id', '=', False)])[0]

    _defaults = {
        'company_id': _default_company,
        'state': lambda *a: 'draft',
    }

    def payment_ids_change(self, cr, uid, ids, payment_ids, commission_rate=0):
        commission_amount = 0
        # payment_ids is a list which contains a tuple which although contains anothe list
        # with the following structure [(a,b,[x,y,z])]
        # so payment_ids[0] yields a tuple (a,b,[x,y,z])
        # and payment_ids[0][2] yields a list with [x,y,z]
        # which contains the ids of the payments involved
        if payment_ids[0][2]:
            account = self.pool.get('account.move.line')
            # Retrieving from account.move.line list of debit's entries with
            # the following payment_ids
            for each_pay_ids in payment_ids[0][2]:
                debit_account = account.browse(cr, uid, each_pay_ids)
                commission_amount += debit_account.debit * \
                    commission_rate / 100
        return {'value': {'commission_amount': commission_amount}}

    def commissionprepare(self, cr, uid, ids, context=None):
        ###############################
        # DELETE THIS AFTER DEBUGGING #
        ###############################
        print 'ESTO ES IDS: ',
        print ids,
        ###############################
        # context: is dictionary where a pair fields vs. value are store to be
        # used afterwards
        if not context:
            context = {}
        # retrieving the lines from the table in the object
        # salesman.commission.payment.line
        tscpl = self.pool.get('salesman.commission.payment.line')
        taml = self.pool.get('account.move.line')

        for idx in ids:

            # Deleting all those line which complies the commission_id in ids
            cr.execute(
                "DELETE FROM salesman_commission_payment_line\
                    WHERE commission_id=%s", (idx,))
            cr.execute(
                "SELECT payment_id FROM hr_salesman_commission_payment\
                    WHERE line_id=%s", (idx,))
            payment_ids = cr.fetchall()
            ###############################
            print 'payment_ids: ',
            print payment_ids,
            ###############################
            for id in payment_ids:
                ###############################
                print 'id[0]: ',
                print id[0],
                ###############################
                each_line = {}

                each_line['commission_id'] = self.browse(
                    cr, uid, idx, context=context).id
                each_line['date_effective'] = taml.browse(cr, uid, id[0]).date
                each_line['fiscalyear_id'] = taml.browse(
                    cr, uid, id[0]).period_id.fiscalyear_id.id
                each_line['period_id'] = taml.browse(
                    cr, uid, id[0]).period_id.id
                each_line['partner_id'] = taml.browse(
                    cr, uid, id[0]).partner_id.id
                each_line['ref'] = taml.browse(cr, uid, id[0]).ref
                each_line['name'] = taml.browse(cr, uid, id[0]).name
                each_line['journal_id'] = taml.browse(
                    cr, uid, id[0]).journal_id.id
                each_line['debit'] = taml.browse(cr, uid, id[0]).debit
                each_line['commission_rate'] = self.browse(
                    cr, uid, idx, context=context).commission_rate
                each_line['commissioned_amount_line'] = each_line[
                    'debit'] * each_line['commission_rate']/100.0
                each_line['user_id'] = self.browse(
                    cr, uid, idx, context=context).user_id.id
                each_line['commission_paid'] = False

                ###############################
                print 'each_line: ',
                print each_line,
                ###############################
                tscpl.create(cr, uid, each_line)
        self.pool.get('salesman.commission.payment').write(
            cr, uid, ids, {'state': 'draft'}, context=context)

        return True

    #################################
    # Loading Partners a account move lines on banks
    ##################################
    def action_number(self, cr, uid, ids, *args):
        obj_sc = self.browse(cr, uid, ids)[0]
        res = {}
        print 'vendedor: ', obj_sc.user_id.id
        print 'periodo: ', obj_sc.period_ids.id
        cr.execute(("""
                select
                    l.id,
                    l.period_id,
                    l.move_id,
                    p.id as partner,
                    u.id as user
                from res_partner p
                    inner join res_users u on (u.id=p.user_id)
                    inner join account_move_line l on (p.id=l.partner_id)
                    inner join account_account c on (c.id=l.account_id)
                where l.credit != 0
                and c.type = 'receivable'
                and u.id = %s
                and l.period_id = %s
        """) % (obj_sc.user_id.id, obj_sc.period_ids.id)
        )

        for line_id, period_id, move_id, partner_id, user_id in cr.fetchall():
            res[move_id] = (line_id, period_id, partner_id, user_id)
        #################################
        # Debugging changes BEFORE DONE
        ##################################
        print 'comprobante: (asiento,periodo,partner,usuario)'
        print 'PAGO DE TODOS LOS CLIENTES DE UN VENDEDOR: ', res
        return res

    def action_move_create(self, cr, uid, ids, *args):
        obj_sc = self.browse(cr, uid, ids)[0]
        print 'argument: ', args
        move_ids = args[0].keys()
        id_set = ','.join(map(str, move_ids))
        print 'comprobantes: ', move_ids
        res = {}

        cr.execute(("""
                select
                    l.id,
                    l.period_id,
                    l.journal_id,
                    l.partner_id,
                    j.type,
                    l.move_id
                from account_move_line l
                    inner join account_journal j on (j.id=l.journal_id)
                where l.partner_id is null
                and j.type='cash'
                and l.period_id=%s
                and l.move_id in (%s)
        """) % (obj_sc.period_ids.id, id_set)
        )

        for line_id, period_id, journal_id, partner_id, jtpo, move_id in\
            cr.fetchall():
            res[line_id] = (period_id, journal_id, partner_id, jtpo, move_id)

        for aml in res.keys():
            cr.execute(("""
                    update
                        account_move_line
                    set
                        partner_id=%s
                    where id=%s
            """) % (args[0][res[aml][4]][2], aml)
            )
    #################################
    # Debugging changes AFTER DONE
    ##################################
        print 'asiento: (periodo,diario,partner,tipodiario)'
        print 'ASIENTO DE BANCO SIN PARTNER: ', res
        return res

    #################################
    # END OF INTERVENTION
    ##################################

    def action_done(self, cr, uid, ids, context={}):
        res = {}

        res = self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids, res)
#        self.write(cr, uid, ids, {'state':'done'})
        return True


class salesman_commission_payment_line(osv.Model):
    _name = 'salesman.commission.payment.line'
    _columns = {
        'commission_id': fields.many2one('salesman.commission.payment',
            'Commission Lines', required=True),
        'date_effective': fields.date('Effective of the Payment',
            required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year',
            required=True, states={'draft': [('readonly', False)]}),
        'period_id': fields.many2one('account.period', 'Period', required=True,
            select=2),
        'partner_id': fields.many2one('res.partner', 'Partner Ref.'),
        'ref': fields.char('Ref.', size=32),
        'name': fields.char('Name', size=64, required=True),
        'journal_id': fields.many2one('account.journal', 'Journal',
            required=True, select=1),
        'debit': fields.float('Debit', digits=(16, 2)),
        'commission_rate':  fields.float('Rate(%)',
            digits_compute=dp.get_precision('Commission'), readonly=True),
        'commissioned_amount_line':  fields.float('Commission',
            digits_compute=dp.get_precision('Commission'), readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman', required=True,
            states={'draft': [('readonly', False)]}),
        'commission_paid': fields.boolean('Paid Commission'),
    }

# domain=[('code','<>','view'), ('code', '<>', 'closed')]
#        'payment_ids': fields.many2many('account.move.line','hr_salesman_commission_payment','move_id','payment_id','Payments'),
#[('account_id.type','=','receivable'), ('invoice','&lt;&gt;',False), ('reconcile_id','=',False)]
