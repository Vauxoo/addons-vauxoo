# coding: utf-8

from __future__ import division
import datetime
import logging

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

# Extra Imports
try:
    from pandas import DataFrame
except ImportError:
    _logger.info('account_currency_tools is declared '
                 ' from addons-vauxoo '
                 ' you will need: sudo pip install pandas')

COMMISSION_STATES = [
    ('draft', 'Draft'),
    ('open', 'In Progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]

COMMISSION_TYPES = [
    ('partial_payment', 'Partial Payments'),
    ('fully_paid_invoice', 'Fully Paid Invoices'),
]

COMMISSION_SALESMAN_POLICY = [
    ('on_invoice', 'Invoice'),
    ('on_invoiced_partner', 'Partner'),
    ('on_accounting_partner', 'Commercial Entity'),
]

COMMISSION_SCOPES = [
    ('whole_invoice', 'Whole Invoice'),
    ('product_invoiced', 'Invoiced Products '),
]

COMMISSION_POLICY_DATE_START = [
    ('invoice_emission_date', 'Emission Date'),
    ('invoice_due_date', 'Due Date'),
]

COMMISSION_POLICY_DATE_END = [
    ('last_payment_date', 'Last Payment on Invoice'),
    ('date_on_payment', 'Date of Payment'),
]

COMMISSION_POLICY_BAREMO = [
    ('onCompany', 'Company'),
    ('onPartner', 'Partner'),
    ('onAccountingPartner', 'Commercial Entity'),
    ('onUser', 'Salespeople'),
    ('onMatrix', 'Baremo Matrix'),
    ('onCommission', 'Document'),
]


def t_time(date):
    """Trims time from "%Y-%m-%d %H:%M:%S" to "%Y-%m-%d"
    """
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date = datetime.date(date.year, date.month, date.day)
    return date.strftime("%Y-%m-%d")


class CommissionPayment(osv.Model):

    """OpenERP Model : commission_payment
    """

    _name = 'commission.payment'
    _inherit = ['mail.thread']
    _description = __doc__

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid,
                                                             context=context)
        if not company_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'name': fields.char(
            'Commission Concept', size=256, required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'baremo_id': fields.many2one(
            'baremo.book', 'Baremo', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'date_start': fields.date(
            'Start Date', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'date_stop': fields.date(
            'End Date', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'total_comm': fields.float(
            'Total Commission',
            digits_compute=dp.get_precision('Commission'),
            readonly=True, states={'write': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'sale_noids': fields.one2many(
            'commission.sale.noid', 'commission_id',
            'Articulos sin asociacion', readonly=True,
            states={'write': [('readonly', False)]}),
        'noprice_ids': fields.one2many(
            'commission.noprice', 'commission_id',
            'Productos sin precio de lista historico', readonly=True,
            states={'write': [('readonly', False)]}),
        'comm_line_product_ids': fields.one2many(
            'commission.lines', 'commission_id',
            'Comision por productos', readonly=True,
            domain=[('product_id', '!=', False)],
            states={'write': [('readonly', False)]}),
        'comm_line_invoice_ids': fields.one2many(
            'commission.lines', 'commission_id',
            'Comision por productos', readonly=True,
            domain=[('product_id', '=', False)],
            states={'write': [('readonly', False)]}),
        'comm_line_ids': fields.one2many(
            'commission.lines', 'commission_id',
            'Comision por productos', readonly=True,
            states={'write': [('readonly', False)]}),
        'salesman_ids': fields.one2many(
            'commission.salesman', 'commission_id',
            'Salespeople Commissions', readonly=True,
            states={'write': [('readonly', False)]}),
        'user_ids': fields.many2many(
            'res.users', 'commission_users',
            'commission_id', 'user_id', 'Salespeople', required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_ids': fields.many2many(
            'account.invoice', 'commission_account_invoice', 'commission_id',
            'invoice_id', 'Invoices', readonly=True,
            states={'draft': [('readonly', False)]}),
        'aml_ids': fields.many2many(
            'account.move.line', 'commission_aml_rel', 'commission_id',
            'aml_id', 'Journal Items', readonly=True,
        ),
        'comm_voucher_ids': fields.one2many(
            'commission.voucher',
            'commission_id', 'Vouchers afectados en esta comision',
            readonly=True, states={'write': [('readonly', False)]}),
        'comm_invoice_ids': fields.one2many(
            'commission.invoice',
            'commission_id', 'Facturas afectadas en esta comision',
            readonly=True, states={'write': [('readonly', False)]}),
        'state': fields.selection(
            COMMISSION_STATES, 'Estado', readonly=True,
            track_visibility='onchange',
        ),
        'commission_type': fields.selection(
            COMMISSION_TYPES,
            string='Basis', required=True,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'commission_scope': fields.selection(
            COMMISSION_SCOPES,
            string='Scope', required=False,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'commission_policy_date_start': fields.selection(
            COMMISSION_POLICY_DATE_START,
            string='Start Date Computation Policy', required=False,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'commission_policy_date_end': fields.selection(
            COMMISSION_POLICY_DATE_END,
            string='End Date Computation Policy', required=False,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'commission_salesman_policy': fields.selection(
            COMMISSION_SALESMAN_POLICY,
            string='Salesman Policy', required=False,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'commission_baremo_policy': fields.selection(
            COMMISSION_POLICY_BAREMO,
            string='Baremo Policy', required=False,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='onchange',
        ),
        'company_id': fields.many2one('res.company', 'Company',
                                      readonly='1'),
        'currency_id': fields.related(
            'company_id', 'currency_id',
            string='Currency',
            relation='res.currency',
            type='many2one',
            store=True,
            readonly=True,
            help=('Currency at which this report will be \
                    expressed. If not selected will be used the \
                    one set in the company')),
        'exchange_date': fields.date('Exchange Date', help=('Date of change\
                                                            that will be\
                                                            printed in the\
                                                            report, with\
                                                            respect to the\
                                                            currency of the\
                                                            company')),
        'comm_fix': fields.boolean('Fix Commissions?'),
        'unknown_salespeople': fields.boolean('Allow Unknown Salespeople?'),
    }
    _defaults = {
        'name': lambda *a: None,
        'total_comm': lambda *a: 0.00,
        'state': lambda *a: 'draft',
        'company_id': _get_default_company,
    }

    def action_view_fixlines(self, cr, uid, ids, context=None):
        """This function returns an action that display existing Commissions of
        given commission payment ids that are required for some details to
        provide a proper computation of commissions.
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'commission_payment',
                                              'comm_line_fix_act')
        idx = result and result[1] or False
        result = act_obj.read(cr, uid, [idx], context=context)[0]
        # compute the number of payments to display
        cl_ids = []
        for cp_brw in self.browse(cr, uid, ids, context=context):
            cl_ids += [cl_brw.id for cs_brw in cp_brw.salesman_ids
                       if not cs_brw.salesman_id
                       for cl_brw in cs_brw.comm_lines_ids
                       ]
        # choose the view_mode accordingly
        if len(cl_ids) > 0:
            result['domain'] = "[('id','in',[" + ','.join(
                [str(cl_id) for cl_id in cl_ids]
            ) + "])]"
        else:
            result['domain'] = "[('id','in',[])]"
        return result

    def action_view_payment(self, cr, uid, ids, context=None):
        """This function returns an action that display existing Payments of given
        commission payment ids. It can either be a in a list or in a form view,
        if there is only one invoice to show.
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'commission_payment',
                                              'action_account_moves_all_tree')
        idx = result and result[1] or False
        result = act_obj.read(cr, uid, [idx], context=context)[0]
        # compute the number of payments to display
        aml_ids = []
        for cp_brw in self.browse(cr, uid, ids, context=context):
            aml_ids += [aml_brw.id for aml_brw in cp_brw.aml_ids]
        # choose the view_mode accordingly
        if len(aml_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(
                [str(aml_id) for aml_id in aml_ids]
            ) + "])]"
        else:
            result['domain'] = "[('id','in',[])]"
        return result

    def action_view_invoice(self, cr, uid, ids, context=None):
        """This function returns an action that display existing invoices of given
        commission payment ids. It can either be a in a list or in a form view,
        if there is only one invoice to show.
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account',
                                              'action_invoice_tree1')
        idx = result and result[1] or False
        result = act_obj.read(cr, uid, [idx], context=context)[0]
        # compute the number of invoices to display
        inv_ids = []
        for cp_brw in self.browse(cr, uid, ids, context=context):
            inv_ids += [invoice.id for invoice in cp_brw.invoice_ids]
        # choose the view_mode accordingly
        if len(inv_ids) >= 1:
            result['domain'] = "[('id','in',[" + ','.join(
                [str(inv_id) for inv_id in inv_ids]
            ) + "])]"
        else:
            result['domain'] = "[('id','in',[])]"
        return result

    def _prepare_based_on_payments(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        aml_obj = self.pool.get('account.move.line')

        for comm_brw in self.browse(cr, uid, ids, context=context):
            date_start = comm_brw.date_start
            date_stop = comm_brw.date_stop

            # In this search we will restrict domain to those Entry Lines
            # coming from a Cash or Bank Journal within the given dates
            args = [('state', '=', 'valid'),
                    ('date', '>=', date_start),
                    ('date', '<=', date_stop),
                    ('journal_id.type', 'in', ('bank', 'cash')),
                    ('credit', '>', 0.0),
                    ('paid_comm', '=', False),
                    ]
            aml_ids = aml_obj.search(
                cr, uid, args + [('rec_invoice', '!=', False)],
                context=context)

            aml_ids += aml_obj.search(
                cr, uid, args + [('rec_aml', '!=', False)],
                context=context)

            aml_ids = list(set(aml_ids))

            comm_brw.write({
                'aml_ids': [(6, comm_brw.id, aml_ids)]})

            invoice_ids = [aml_brw.rec_invoice.id
                           for aml_brw in comm_brw.aml_ids
                           if aml_brw.rec_invoice
                           ]

            invoice_ids = list(set(invoice_ids))

            comm_brw.write({'invoice_ids': [(6, comm_brw.id, invoice_ids)]})

        return True

    def _prepare_based_on_invoices(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        aml_obj = self.pool.get('account.move.line')

        for comm_brw in self.browse(cr, uid, ids, context=context):
            comm_brw.write({'aml_ids': []})
            date_start = comm_brw.date_start
            date_stop = comm_brw.date_stop

            # En esta busqueda restringimos que la factura de cliente se haya
            # pagado y que  este dentro de la fecha estipulada
            invoice_ids = inv_obj.search(
                cr, uid, [('state', '=', 'paid'),
                          ('type', '=', 'out_invoice'),
                          ('date_last_payment', '>=', date_start),
                          ('date_last_payment', '<=', date_stop),
                          ], context=context)

            comm_brw.write({
                'invoice_ids': [(6, comm_brw.id, invoice_ids)]})

            aml_ids = [aml_brw.id for inv_brw in comm_brw.invoice_ids
                       for aml_brw in inv_brw.payment_ids
                       if aml_brw.journal_id.type in ('bank', 'cash')
                       ]

            aml_ids2 = aml_obj.search(
                cr, uid, [('state', '=', 'valid'),
                          ('reconcile_id', '!=', False),
                          ('journal_id.type', '=', 'sale'),
                          ('date_last_payment', '>=', date_start),
                          ('date_last_payment', '<=', date_stop),
                          ], context=context)

            aml_ids2 = aml_obj.search(
                cr, uid, [('state', '=', 'valid'),
                          ('reconcile_id', '!=', False),
                          ('journal_id.type', 'in', ('bank', 'cash')),
                          ('rec_aml', 'in', aml_ids2),
                          # ('date_last_payment', '>=', date_start),
                          # ('date_last_payment', '<=', date_stop),
                          ], context=context)

            aml_ids = list(set(aml_ids + aml_ids2))
            comm_brw.write({'aml_ids': [(6, comm_brw.id, aml_ids)]})

        return True

    def _get_commission_rate(self, cr, uid, ids, pay_date, inv_date, dcto=0.0,
                             bar_brw=None, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        # Determinar dias entre la emision de la factura del producto y el pago
        # del mismo
        pay_date = datetime.datetime.strptime(pay_date, '%Y-%m-%d')
        inv_date = datetime.datetime.strptime(inv_date, '%Y-%m-%d')
        emission_days = (pay_date - inv_date).days

        # Teniendose dias y descuento por producto se procede a buscar en el
        # baremo el correspondiente valor de comision para el producto en
        # cuestion. se entra con el numero de dias

        # Esta busqueda devuelve los dias ordenadados de menor a mayor dia, de
        # acuerdo con lo estipulado que se ordenaria en el modulo baremo
        bar_day_ids = bar_brw and bar_brw.bar_ids or comm_brw.baremo_id.bar_ids

        no_days = True
        no_dcto = True
        for day_id in bar_day_ids:
            # Se busca que el baremo tenga un rango que cubra a emision_days
            if emission_days <= day_id.number:
                bar_day = day_id.number
                no_days = False
                no_dcto = True
                for dcto_id in day_id.disc_ids:
                    # Se busca que el baremo tenga un rango para el valor de
                    # descuento en producto
                    if dcto <= dcto_id.porc_disc:
                        bardctdsc = dcto_id.porc_disc
                        bar_dcto_comm = dcto_id.porc_com
                        no_dcto = False
                        break
                break

        if (not no_days) and no_dcto:
            bar_dcto_comm = 0.0
            bardctdsc = 0.0

        # Si emission_days no es cubierto por ningun rango del baremo diremos
        # entonces que la comision es cero (0) %
        elif no_days and no_dcto:
            # Diremos que los dias de baremo es menos uno (-1) cuando los dias
            # de emision no esten dentro del rango del baremo
            bar_day = '0.0'
            bardctdsc = 0.0
            bar_dcto_comm = 0.0

        res = dict(
            bar_day=bar_day,
            bar_dcto_comm=bar_dcto_comm,
            bardctdsc=bardctdsc,
            emission_days=emission_days,
        )
        return res

    def _get_commission_policy_start_date(self, cr, uid, ids, pay_id,
                                          context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        aml_brw = aml_obj.browse(cr, uid, pay_id, context=context)
        date = False
        if comm_brw.commission_policy_date_start == 'invoice_emission_date':
            if aml_brw.rec_invoice:
                date = aml_brw.rec_invoice.date_invoice
            else:
                date = aml_brw.rec_aml.date

        elif comm_brw.commission_policy_date_start == 'invoice_due_date':
            if aml_brw.rec_invoice:
                date = aml_brw.rec_invoice.date_due
            else:
                date = aml_brw.rec_aml.date_maturity or aml_brw.rec_aml.date
        return date

    def _get_commission_policy_end_date(self, cr, uid, ids, pay_id,
                                        context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        aml_brw = aml_obj.browse(cr, uid, pay_id, context=context)
        date = aml_brw.date
        if comm_brw.commission_policy_date_end == 'last_payment_date':
            date = aml_brw.rec_aml.date_last_payment or \
                aml_brw.date_last_payment or date
        return date

    def _get_commission_saleman(self, cr, uid, ids, salesman_brw,
                                context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        if not salesman_brw:
            return None
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        user_ids = [usr_brw.id for usr_brw in comm_brw.user_ids]
        if not user_ids:
            return salesman_brw
        if salesman_brw.id not in user_ids:
            return None
        return salesman_brw

    def _get_commission_salesman_policy(self, cr, uid, ids, pay_id,
                                        salesman_id=None, context=None):
        if salesman_id:
            return salesman_id
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        rp_obj = self.pool.get('res.partner')
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        aml_brw = aml_obj.browse(cr, uid, pay_id, context=context)
        res = None
        if aml_brw.rec_invoice:
            if comm_brw.commission_salesman_policy == 'on_invoice':
                res = aml_brw.rec_invoice.user_id
            elif comm_brw.commission_salesman_policy == \
                    'on_invoiced_partner':
                res = aml_brw.rec_invoice.partner_id.user_id
            elif comm_brw.commission_salesman_policy == \
                    'on_accounting_partner':
                res = rp_obj._find_accounting_partner(
                    aml_brw.rec_invoice.partner_id).user_id
        else:
            if comm_brw.commission_salesman_policy in \
                    ('on_invoiced_partner', 'on_invoice'):
                res = aml_brw.rec_aml.partner_id.user_id
            elif comm_brw.commission_salesman_policy == \
                    'on_accounting_partner':
                res = rp_obj._find_accounting_partner(
                    aml_brw.rec_aml.partner_id).user_id

        return res

    def _get_commission_matrix_policy(self, cr, uid, ids, product_id,
                                      salesman_id, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        bm_obj = self.pool.get('baremo.matrix')
        res = bm_obj.search(cr, uid, [
            ('product_id', '=', product_id),
            ('user_id', '=', salesman_id.id),
        ])
        if res:
            return bm_obj.browse(cr, uid, res[0], context=context).baremo_id

        comm_brw = self.browse(cr, uid, ids[0], context=context)
        return comm_brw.baremo_id

    def _get_commission_policy_baremo(self, cr, uid, ids, pay_id,
                                      partner_id=None, salesman_id=None,
                                      context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        partner_id = partner_id or None
        aml_obj = self.pool.get('account.move.line')
        rp_obj = self.pool.get('res.partner')
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        aml_brw = aml_obj.browse(cr, uid, pay_id, context=context)
        res = None
        if comm_brw.commission_baremo_policy == 'onCompany':
            partner_id = comm_brw.company_id.partner_id
        elif comm_brw.commission_baremo_policy == 'onPartner':
            if aml_brw.rec_invoice:
                partner_id = partner_id or aml_brw.rec_invoice.partner_id
            else:
                partner_id = partner_id or aml_brw.rec_aml.partner_id
        elif comm_brw.commission_baremo_policy == 'onAccountingPartner':
            if aml_brw.rec_invoice:
                partner_id = partner_id or aml_brw.rec_invoice.partner_id
            else:
                partner_id = partner_id or aml_brw.rec_aml.partner_id
            partner_id = rp_obj._find_accounting_partner(partner_id)
        elif comm_brw.commission_baremo_policy == 'onUser':
            partner_id = self._get_commission_salesman_policy(
                cr, uid, ids[0], pay_id, salesman_id=salesman_id,
                context=context).partner_id
        elif comm_brw.commission_baremo_policy == 'onCommission':
            res = comm_brw.baremo_id
        # Fall back to baremo in Commission
        if partner_id:
            res = partner_id.baremo_id
        else:
            res = comm_brw.baremo_id
        return res

    def _get_commission_payment_on_invoice_line(self, cr, uid, ids, pay_id,
                                                context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)

        aml_obj = self.pool.get('account.move.line')
        prod_prices = self.pool.get('product.historic.price')
        sale_noids = self.pool.get('commission.sale.noid')
        noprice_ids = self.pool.get('commission.noprice')
        comm_line_ids = self.pool.get('commission.lines')

        aml_brw = aml_obj.browse(cr, uid, pay_id, context=context)
        if not aml_brw.credit:
            return True

        # Retrieve Partner's Salesman
        salesman = self._get_commission_salesman_policy(cr, uid, ids, pay_id,
                                                        context=context)
        salesman_ok = self._get_commission_saleman(cr, uid, ids, salesman,
                                                   context=context)

        if not salesman_ok:
            if not (comm_brw.unknown_salespeople and not salesman):
                return True

        commission_policy_date_start = \
            self._get_commission_policy_start_date(cr, uid, ids, pay_id,
                                                   context=context)

        commission_policy_date_end = \
            self._get_commission_policy_end_date(cr, uid, ids, pay_id,
                                                 context=context)

        # Si esta aqui dentro es porque esta linea tiene una id valida
        # de una factura.
        inv_brw = aml_brw.rec_invoice
        commission_baremo_policy = comm_brw.commission_baremo_policy
        # /!\ NOTE: Retrieve here the fallback commission baremo policy
        if not commission_baremo_policy == 'onMatrix':
            commission_policy_baremo = self._get_commission_policy_baremo(
                cr, uid, ids, pay_id, context=context)

        # Revision de cada linea de factura (productos)
        for inv_lin in inv_brw.invoice_line:

            # Verificar si tiene producto asociado
            if inv_lin.product_id:
                # DETERMINAR EL PORCENTAJE DE IVA EN LA LINEA (perc_iva)
                # =============================================================
                # =============================================================
                # Determinar si la linea de la factura tiene un impuesto
                # (perc_iva). El impuesto aplicado a una linea es igual a la
                # suma de los impuestos se asume que todos los impuestos son
                # porcentuales
                perc_iva = (inv_lin.invoice_line_tax_id and
                            sum([tax.amount for tax in
                                 inv_lin.invoice_line_tax_id]) * 100 or 0.0)
                # Si esta aqui es porque hay un producto asociado
                prod_id = inv_lin.product_id.product_tmpl_id.id
                # se obtienen las listas de precio, vienen ordenadas
                # por defecto, de acuerdo al objeto product.historic de
                # mayor a menor fecha
                price_ids = prod_prices.search(
                    cr, uid,
                    [('product_id', '=', prod_id)])
                # Buscar Precio Historico de Venta de este producto @
                # la fecha de facturacion
                no_price = True

                for price_id in price_ids:
                    prod_prices_brw = \
                        prod_prices.browse(cr, uid, price_id, context=context)
                    if inv_brw.date_invoice >= t_time(prod_prices_brw.name):
                        list_price = prod_prices_brw.price
                        list_date = prod_prices_brw.name
                        no_price = False
                        break
                if not no_price:
                    # Determinar cuanto fue el
                    # descuento en este producto en
                    # aquel momento de la venta
                    if abs((inv_lin.price_subtotal / inv_lin.quantity) -
                           inv_lin.price_unit) > 0.05:
                        # con esto se asegura que no se esta pasando
                        # por alto el descuento en linea
                        price_unit = round((inv_lin.price_subtotal /
                                            inv_lin.quantity), 2)
                    else:
                        price_unit = inv_lin.price_unit
                    dcto = 0.0
                    if list_price:
                        dcto = round((list_price - price_unit) * 100 /
                                     list_price, 1)
                    rate_item = dcto

                    if commission_baremo_policy == 'onMatrix':
                        commission_policy_baremo = \
                            self._get_commission_matrix_policy(
                                cr, uid, ids, inv_lin.product_id.id,
                                salesman, context=None)

                    # CHECK: If no commission policy is passed why it retrieves
                    # values
                    commission_params = self._get_commission_rate(
                        cr, uid, comm_brw.id,
                        commission_policy_date_end,
                        commission_policy_date_start, dcto=0.0,
                        bar_brw=commission_policy_baremo)

                    bar_day = commission_params['bar_day']
                    bar_dcto_comm = commission_params['bar_dcto_comm']
                    bardctdsc = commission_params['bardctdsc']
                    emission_days = commission_params['emission_days']

                    #############################################
                    # CALCULO DE COMISION POR LINEA DE PRODUCTO #
                    #############################################

                    penbxlinea = aml_brw.credit * (
                        inv_lin.price_subtotal /
                        inv_brw.amount_untaxed)
                    fact_sup = 1 - 0.0 / 100 - 0.0 / 100
                    fact_inf = 1 + (perc_iva / 100) * (1 - 0.0 / 100) - \
                        0.0 / 100 - 0.0 / 100

                    comm_line = penbxlinea * fact_sup * (
                        bar_dcto_comm / 100) / fact_inf

                    if aml_brw.currency_id and aml_brw.amount_currency:
                        payxlinea_curr = aml_brw.amount_currency * (
                            inv_lin.price_subtotal /
                            inv_brw.amount_untaxed)

                        commission_currency = (abs(payxlinea_curr) * fact_sup *
                                               (bar_dcto_comm / 100) /
                                               fact_inf)
                    elif aml_brw.currency_id and not aml_brw.amount_currency:
                        return True
                    else:
                        commission_currency = comm_line

                    # Generar las lineas de comision por cada producto
                    comm_line_ids.create(
                        cr, uid, {
                            'commission_id': comm_brw.id,
                            'aml_id': aml_brw.id,
                            'am_rec': inv_brw.move_id.id,
                            'name':
                            aml_brw.move_id.name and
                            aml_brw.move_id.name or '/',
                            'pay_date': aml_brw.date,
                            'pay_off': aml_brw.credit,
                            'partner_id': inv_brw.partner_id.id,
                            'salesman_id': salesman and salesman.id,
                            'pay_inv': aml_brw.credit,
                            'inv_date': inv_brw.date_invoice,
                            'date_start': commission_policy_date_start,
                            'date_stop': commission_policy_date_end,
                            'days': emission_days,
                            'inv_subtotal': inv_brw.amount_untaxed,
                            'product_id': inv_lin.product_id.id,
                            'price_unit': price_unit,
                            'price_subtotal': inv_lin.price_subtotal,
                            'price_list': list_price,
                            'price_date': list_date,
                            'perc_iva': perc_iva,
                            'rate_item': rate_item,
                            'rate_number': bardctdsc,
                            'timespan': bar_day,
                            'baremo_comm': bar_dcto_comm,
                            'commission': comm_line,
                            'commission_currency': commission_currency,
                            'currency_id': inv_brw.currency_id and
                            inv_brw.currency_id.id or
                            inv_brw.company_id.currency_id.id,
                        }, context=context)

                else:
                    # Se genera un lista de tuplas con las lineas,
                    # productos y sus correspondientes fechas en las
                    # cuales no aparece precio de lista, luego al final
                    # se escriben los valores en la correspondiente
                    # bitacora para su inspeccion. ~ #~ print 'No hubo
                    # precio de lista para la fecha estipulada, hay que
                    # generar el precio en este producto \n'
                    noprice_ids.create(cr, uid, {'commission_id': comm_brw.id,
                                                 'product_id': prod_id,
                                                 'date': inv_brw.date_invoice,
                                                 'invoice_num':
                                                 inv_brw.number},
                                       context=context)
            else:
                # cuando una linea no tiene product_id asociado se
                # escribe en una tabla para alertar al operador sobre
                # esta parte no llego a un acuerdo de si se podria
                # permitir al operador cambiar las lineas de la factura
                # puesto que es un asunto muy delicado.
                sale_noids.create(cr, uid, {'commission_id': comm_brw.id,
                                            'inv_line_id': inv_lin.id, },
                                  context=context)
        return True

    def _get_commission_payment_on_invoice(self, cr, uid, ids, aml_id,
                                           context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)

        aml_obj = self.pool.get('account.move.line')
        comm_line_ids = self.pool.get('commission.lines')

        aml_brw = aml_obj.browse(cr, uid, aml_id, context=context)
        if not aml_brw.credit:
            return True

        # Retrieve Partner's Salesman
        salesman = self._get_commission_salesman_policy(cr, uid, ids, aml_id,
                                                        context=context)
        salesman_ok = self._get_commission_saleman(cr, uid, ids, salesman,
                                                   context=context)

        if not salesman_ok:
            if not (comm_brw.unknown_salespeople and not salesman):
                return True

        commission_policy_date_start = \
            self._get_commission_policy_start_date(cr, uid, ids, aml_id,
                                                   context=context)

        commission_policy_date_end = \
            self._get_commission_policy_end_date(cr, uid, ids, aml_id,
                                                 context=context)

        # Si esta aqui dentro es porque esta linea tiene una id valida
        # de una factura.
        inv_brw = aml_brw.rec_invoice

        # DETERMINAR EL PORCENTAJE DE IVA EN LA FACTUR (perc_iva)
        # =======================================================
        # =======================================================
        perc_iva = (inv_brw.amount_total / inv_brw.amount_untaxed - 1) * 100

        commission_policy_baremo = \
            self._get_commission_policy_baremo(cr, uid, ids, aml_id,
                                               context=context)

        commission_params = self._get_commission_rate(
            cr, uid, comm_brw.id,
            commission_policy_date_end,
            commission_policy_date_start, dcto=0.0,
            bar_brw=commission_policy_baremo)

        bar_day = commission_params['bar_day']
        bar_dcto_comm = commission_params['bar_dcto_comm']
        bardctdsc = commission_params['bardctdsc']
        emission_days = commission_params['emission_days']

        ###################################
        # CALCULO DE COMISION POR FACTURA #
        ###################################

        penbxlinea = aml_brw.credit
        fact_sup = 1 - 0.0 / 100 - 0.0 / 100
        fact_inf = 1 + (perc_iva / 100) * (1 - 0.0 / 100) - \
            0.0 / 100 - 0.0 / 100

        comm_line = penbxlinea * fact_sup * (
            bar_dcto_comm / 100) / fact_inf

        if aml_brw.currency_id and aml_brw.amount_currency:
            commission_currency = abs(aml_brw.amount_currency) * fact_sup * (
                bar_dcto_comm / 100) / fact_inf
        elif aml_brw.currency_id and not aml_brw.amount_currency:
            return True
        else:
            commission_currency = comm_line

        # Generar las lineas de comision por cada factura
        comm_line_ids.create(
            cr, uid, {
                'commission_id': comm_brw.id,
                'aml_id': aml_brw.id,
                'am_rec': inv_brw.move_id.id,
                'name':
                aml_brw.move_id.name and
                aml_brw.move_id.name or '/',
                'pay_date': aml_brw.date,
                'pay_off': aml_brw.credit,
                'partner_id': inv_brw.partner_id.id,
                'salesman_id': salesman and salesman.id,
                'pay_inv': aml_brw.credit,
                'inv_date': inv_brw.date_invoice,
                'date_start': commission_policy_date_start,
                'date_stop': commission_policy_date_end,
                'days': emission_days,
                'inv_subtotal': inv_brw.amount_untaxed,
                'perc_iva': perc_iva,
                'rate_number': bardctdsc,
                'timespan': bar_day,
                'baremo_comm': bar_dcto_comm,
                'commission': comm_line,
                'commission_currency': commission_currency,
                'currency_id': inv_brw.currency_id and
                inv_brw.currency_id.id or inv_brw.company_id.currency_id.id,
            }, context=context)

        return True

    def _get_commission_payment_on_aml(self, cr, uid, ids, aml_id,
                                       context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)

        if not comm_brw.unknown_salespeople:
            return True

        aml_obj = self.pool.get('account.move.line')
        comm_line_ids = self.pool.get('commission.lines')

        aml_brw = aml_obj.browse(cr, uid, aml_id, context=context)
        if not aml_brw.credit:
            return True

        commission_policy_date_start = \
            self._get_commission_policy_start_date(cr, uid, ids, aml_id,
                                                   context=context)

        commission_policy_date_end = \
            self._get_commission_policy_end_date(cr, uid, ids, aml_id,
                                                 context=context)

        commission_policy_baremo = \
            self._get_commission_policy_baremo(cr, uid, ids, aml_id,
                                               context=context)

        commission_params = self._get_commission_rate(
            cr, uid, comm_brw.id,
            commission_policy_date_end,
            commission_policy_date_start, dcto=0.0,
            bar_brw=commission_policy_baremo)

        bar_day = commission_params['bar_day']
        bar_dcto_comm = commission_params['bar_dcto_comm']
        bardctdsc = commission_params['bardctdsc']
        emission_days = commission_params['emission_days']

        # Generar las lineas de comision por cada factura
        comm_line_ids.create(
            cr, uid, {
                'commission_id': comm_brw.id,
                'aml_id': aml_brw.id,
                'am_rec': aml_brw.rec_aml.move_id.id,
                'name': aml_brw.move_id.name and aml_brw.move_id.name or '/',
                'pay_date': aml_brw.date,
                'pay_off': aml_brw.credit,
                'partner_id': aml_brw.partner_id.id,
                'salesman_id': None,
                'pay_inv': aml_brw.credit,
                'inv_date': aml_brw.rec_aml.date,
                'date_start': commission_policy_date_start,
                'date_stop': commission_policy_date_end,
                'days': emission_days,
                'inv_subtotal': None,
                'perc_iva': None,
                'rate_number': bardctdsc,
                'timespan': bar_day,
                'baremo_comm': bar_dcto_comm,
                'commission': 0.0,
                'commission_currency': None,
                'currency_id': aml_brw.currency_id and
                aml_brw.currency_id.id or aml_brw.company_id.currency_id.id,
            }, context=context)

        return True

    def _get_commission_payment(self, cr, uid, ids, aml_id, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        if comm_brw.commission_scope == 'product_invoiced':
            self._get_commission_payment_on_invoice_line(cr, uid, ids, aml_id,
                                                         context=context)
        elif comm_brw.commission_scope == 'whole_invoice':
            self._get_commission_payment_on_invoice(cr, uid, ids, aml_id,
                                                    context=context)

        return True

    def _commission_based_on_payments(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}

        for comm_brw in self.browse(cr, uid, ids, context=context):

            payment_ids = set([])
            uninvoice_payment_ids = set([])

            # Read each Journal Entry Line
            for aml_brw in comm_brw.aml_ids:
                # Verificar si la comision del pago ya se ha pagado
                if aml_brw.paid_comm:
                    continue

                # Verificar si esta linea tiene factura
                if not aml_brw.rec_invoice:
                    # TODO: Here we have to deal with the lines that comes from
                    # another system
                    uninvoice_payment_ids.add(aml_brw.id)
                    continue

                payment_ids.add(aml_brw.id)

            for pay_id in payment_ids:
                # se procede con la preparacion de las comisiones.
                self._get_commission_payment(cr, uid, ids, pay_id,
                                             context=context)

            for aml_id in uninvoice_payment_ids:
                # se procede con la preparacion de las comisiones.
                self._get_commission_payment_on_aml(cr, uid, ids, aml_id,
                                                    context=context)

        return True

    def _post_processing(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        salesman_ids = self.pool.get('commission.salesman')
        comm_line_obj = self.pool.get('commission.lines')
        comm_voucher_ids = self.pool.get('commission.voucher')
        comm_invoice_ids = self.pool.get('commission.invoice')

        # habiendo recorrido todos los vouchers, mostrado todos los elementos
        # que necesitan correccion se procede a agrupar las comisiones por
        # vendedor para mayor facilidad de uso

        cl_fields = ['id', 'salesman_id', 'currency_id', 'commission',
                     'commission_currency', 'am_id', 'invoice_id',
                     'comm_salespeople_id', 'comm_voucher_id', ]

        for commission in self.browse(cr, uid, ids, context=context):
            # Erasing what was previously set as Commission per Salesman
            commission.salesman_ids.unlink()
            commission.comm_invoice_ids.unlink()
            commission.comm_voucher_ids.unlink()

            # recoge todos los vendedores y suma el total de sus comisiones
            sale_comm = {}
            # ordena en un arbol todas las lineas de comisiones de producto
            cl_ids = commission.comm_line_ids.read(cl_fields, load=None)
            if not cl_ids:
                continue

            cl_data = DataFrame(cl_ids).set_index('id')
            cl_data_grouped = cl_data.groupby(['salesman_id', 'currency_id'])

            cl_data_agg = cl_data_grouped.sum()
            sale_comm_data = cl_data_agg.to_dict()
            sale_comm_cl = cl_data_grouped.groups

            sale_comm = sale_comm_data.get('commission')
            sale_comm_curr = sale_comm_data.get('commission_currency')
            for key, value in sale_comm.iteritems():
                salesman_id, currency_id = key
                vendor_id = salesman_ids.create(cr, uid, {
                    'commission_id': commission.id,
                    'salesman_id': salesman_id,
                    'currency_id': currency_id,
                    'comm_total': value,
                    'comm_total_currency': sale_comm_curr[key],
                }, context=context)
                commline_ids = [
                    int(item) for item in sale_comm_cl[key].tolist()]
                comm_line_obj.write(cr, uid, commline_ids,
                                    {'comm_salespeople_id': vendor_id})

            commission.write({
                'total_comm': cl_data.sum().get('commission'),
                'comm_fix': not all(
                    cl_data.groupby('salesman_id').groups.keys()),
            })

            cl_ids = commission.comm_line_ids.read(cl_fields, load=None)
            cl_data = DataFrame(cl_ids).set_index('id')
            vc_group = cl_data.groupby(['comm_salespeople_id', 'am_id']).groups

            for key, values in vc_group.iteritems():
                comm_salespeople_id, am_id = key
                comm_voucher_id = comm_voucher_ids.create(cr, uid, {
                    'commission_id': commission.id,
                    'comm_sale_id': comm_salespeople_id,
                    'am_id': am_id,
                }, context=context)
                comm_line_obj.write(cr, uid, values.tolist(),
                                    {'comm_voucher_id': comm_voucher_id},
                                    context=context)

            cl_ids = commission.comm_line_ids.read(cl_fields, load=None)
            cl_data = DataFrame(cl_ids).set_index('id')
            vc_group = cl_data.groupby(['comm_voucher_id',
                                        'invoice_id']).groups

            for key, values in vc_group.iteritems():
                comm_voucher_id, invoice_id = key
                comm_invoice_id = comm_invoice_ids.create(cr, uid, {
                    'commission_id': commission.id,
                    'comm_voucher_id': comm_voucher_id,
                    'invoice_id': invoice_id,
                }, context=context)
                comm_line_obj.write(cr, uid, values.tolist(),
                                    {'comm_invoice_id': comm_invoice_id},
                                    context=context)

        return True

    def prepare(self, cr, uid, ids, context=None):
        """Este metodo recorre los elementos de lineas de asiento y verifica al
        menos tres (3) caracteristicas primordiales para continuar con los
        mismos: estas caracteristicas son:
        - journal_id.type in ('cash', 'bank'): quiere decir que la linea es de
        un deposito bancario (aqui aun no se ha considerado el trato que se le
        da a los cheques devueltos).
        - state == 'valid' : quiere decir que la linea ya se ha contabilizado y
        que esta cuadrado el asiento, condicion necesaria pero no suficiente.
        - paid_comm: que la linea aun no se ha considerado para una comision.

        Si estas tres (3) condiciones se cumplen entonces se puede proceder a
        realizar la revision de las lineas de pago.


        @param cr: cursor to database
        @param uid: id of current user
        @param ids: list of record ids to be process
        @param context: context arguments, like lang, time zone

        @return: return a result
        """
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        if comm_brw.commission_baremo_policy == 'onMatrix' and \
                comm_brw.commission_scope != 'product_invoiced':
            raise osv.except_osv(
                _('Error!'),
                _('Baremo on Matrix only applies on Invoiced Products'))
        # Desvincular lineas existentes, si las hubiere
        comm_brw.clear()
        if comm_brw.commission_type == 'partial_payment':
            self._prepare_based_on_payments(cr, uid, ids, context=context)
        elif comm_brw.commission_type == 'fully_paid_invoice':
            self._prepare_based_on_invoices(cr, uid, ids, context=context)

        self._commission_based_on_payments(cr, uid, ids, context=context)
        self._post_processing(cr, uid, ids, context=context)

        self.write(cr, uid, ids, {'state': 'open'}, context=context)
        return True

    def _recompute_commission(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        for comm_brw in self.browse(cr, uid, ids, context=context):
            for cs_brw in comm_brw.salesman_ids:
                if cs_brw.salesman_id:
                    continue
                for cl_brw in cs_brw.comm_lines_ids:
                    cl_brw._recompute_commission()
        return True

    def action_recompute(self, cr, uid, ids, context=None):

        self._recompute_commission(cr, uid, ids, context=context)
        self._post_processing(cr, uid, ids, context=context)
        return True

    def action_draft(self, cr, user, ids, context=None):

        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        aml_obj = self.pool.get('account.move.line')

        for comm_brw in self.browse(cr, user, ids, context=context):
            if comm_brw.state == 'done':
                aml_obj.write(
                    cr, user,
                    [line.aml_id.id for line in comm_brw.comm_line_ids],
                    {'paid_comm': False}, context=context)

        self.clear(cr, user, ids, context=context)
        self.write(cr, user, ids, {'state': 'draft', 'total_comm': None},
                   context=context)
        return True

    def clear(self, cr, user, ids, context=None):
        """Deletes all associated record from Commission Payment
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        for comm_brw in self.browse(cr, user, ids, context=context):
            comm_brw.sale_noids.unlink()
            comm_brw.noprice_ids.unlink()
            comm_brw.comm_line_ids.unlink()
            comm_brw.salesman_ids.unlink()
            comm_brw.comm_voucher_ids.unlink()
            comm_brw.comm_invoice_ids.unlink()
            comm_brw.write(
                {'aml_ids': [(3, aml_brw.id) for aml_brw in comm_brw.aml_ids],
                 'invoice_ids': [
                     (3, inv_brw.id) for inv_brw in comm_brw.invoice_ids]})

    def validate(self, cr, user, ids, context=None):
        aml_obj = self.pool.get('account.move.line')
        # escribir en el aml el estado buleano de paid_comm a True para indicar
        # que ya esta comision se esta pagando
        # TODO: prior to write anything here paid_comm field has to be check
        # first if any of the line has being paid arise a warning
        for comm_brw in self.browse(cr, user, ids, context=context):
            if comm_brw.comm_fix:
                raise osv.except_osv(_('Error!'), _('There are items to fix'))

            aml_obj.write(cr, user,
                          [line.aml_id.id for line in comm_brw.comm_line_ids],
                          {'paid_comm': True}, context=context)

        # TODO: write the real list of payments and invoices that were taken
        # into account
        self.write(cr, user, ids, {'state': 'done', }, context=context)
        return True


class CommissionSaleNoid(osv.Model):

    """Commission Payment : commission_sale_noid
    """

    _name = 'commission.sale.noid'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'inv_line_id': fields.many2one(
            'account.invoice.line', 'Descripcion de Articulo'),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class CommissionNoprice(osv.Model):

    """Commission Payment : commission_sale_noid
    """

    _name = 'commission.noprice'
    _order = 'product_id'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'date': fields.date('Date'),
        'invoice_num': fields.char('Invoice Number', size=256),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class CommissionLines(osv.Model):

    """Commission Payment : commission_lines
    """

    _name = 'commission.lines'
    _order = 'pay_date'

    _columns = {
        'commission_id': fields.many2one(
            'commission.payment', 'Commission Document', required=True),
        'name': fields.char('Transaccion', size=256, required=True),
        'pay_date': fields.date('Payment Date', required=True),
        'pay_off': fields.float(
            'Pago',
            digits_compute=dp.get_precision('Commission')),

        'aml_id': fields.many2one('account.move.line', 'Entry Line'),
        'am_rec': fields.many2one('account.move', 'Reconciling Entry'),
        'am_id': fields.related(
            'aml_id', 'move_id',
            string='Journal Entry', relation='account.move',
            type='many2one', store=True, readonly=True),

        'invoice_id': fields.related(
            'aml_id', 'rec_invoice',
            string='Reconciling Invoice', relation='account.invoice',
            type='many2one', store=True, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'salesman_id': fields.many2one('res.users', 'Salesman',
                                       required=False),
        'comm_salespeople_id': fields.many2one(
            'commission.salesman', 'Salespeople Commission', required=False),
        'comm_voucher_id': fields.many2one(
            'commission.voucher', 'Voucher Commission', required=False),
        'pay_inv': fields.float(
            'Pay. to Doc.',
            digits_compute=dp.get_precision('Commission')),

        'inv_date': fields.date('Invoice Date'),
        'date_start': fields.date(
            'Start Date', required=False, readonly=True,
        ),
        'date_stop': fields.date(
            'End Date', required=False, readonly=True,
        ),
        'days': fields.float(
            'Comm. Days',
            digits_compute=dp.get_precision('Commission')),

        'inv_subtotal': fields.float(
            'SubTot. Doc.',
            digits_compute=dp.get_precision('Commission')),

        'product_id': fields.many2one('product.product', 'Product'),
        'price_unit': fields.float(
            'Prec. Unit.',
            digits_compute=dp.get_precision('Commission')),
        'price_subtotal': fields.float(
            'SubTot. Product',
            digits_compute=dp.get_precision('Commission')),

        'price_list': fields.float(
            'Price List',
            digits_compute=dp.get_precision('Commission')),
        'price_date': fields.date('List Date'),

        'perc_iva': fields.float(
            'Tax (%)',
            digits_compute=dp.get_precision('Commission')),

        'rate_item': fields.float(
            'Dsct. (%)',
            digits_compute=dp.get_precision('Commission')),

        'rate_number': fields.float(
            'B./Rate (%)',
            digits_compute=dp.get_precision('Commission')),
        'timespan': fields.float(
            'B./Days',
            digits_compute=dp.get_precision('Commission')),
        'baremo_comm': fields.float(
            'B./%Comm.',
            digits_compute=dp.get_precision('Commission')),
        'commission': fields.float(
            'Commission Amount',
            digits_compute=dp.get_precision('Commission')),
        'commission_currency': fields.float(
            'Currency Amount',
            digits_compute=dp.get_precision('Commission')),
        'currency_id': fields.many2one('res.currency', 'Currency'),
    }

    _defaults = {
        'name': lambda *a: None,
    }

    def _recompute_commission(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        cl_brw = self.browse(cr, uid, ids[0], context=context)
        comm_brw = cl_brw.commission_id

        aml_brw = cl_brw.aml_id
        aml_id = cl_brw.aml_id.id
        if not aml_brw.credit:
            return True

        commission_policy_date_start = \
            comm_brw._get_commission_policy_start_date(aml_id)

        commission_policy_date_end = \
            comm_brw._get_commission_policy_end_date(aml_id)

        commission_policy_baremo = \
            comm_brw._get_commission_policy_baremo(
                aml_id, partner_id=cl_brw.partner_id,
                salesman_id=cl_brw.salesman_id)

        commission_params = comm_brw._get_commission_rate(
            commission_policy_date_end,
            commission_policy_date_start, dcto=0.0,
            bar_brw=commission_policy_baremo)

        bar_day = commission_params['bar_day']
        bar_dcto_comm = commission_params['bar_dcto_comm']
        bardctdsc = commission_params['bardctdsc']
        emission_days = commission_params['emission_days']

        ###############################
        # CALCULO DE COMISION POR AML #
        ###############################

        # Right now I have not figure out a way to know how much was taxed
        perc_iva = comm_brw.company_id.comm_tax

        penbxlinea = aml_brw.credit
        fact_sup = 1 - 0.0 / 100 - 0.0 / 100
        fact_inf = 1 + (perc_iva / 100) * (1 - 0.0 / 100) - \
            0.0 / 100 - 0.0 / 100

        comm_line = penbxlinea * fact_sup * (
            bar_dcto_comm / 100) / fact_inf

        if aml_brw.currency_id and aml_brw.amount_currency:
            commission_currency = abs(aml_brw.amount_currency) * fact_sup * (
                bar_dcto_comm / 100) / fact_inf
        elif aml_brw.currency_id and not aml_brw.amount_currency:
            return True
        else:
            commission_currency = comm_line

        # Generar las lineas de comision por cada factura
        cl_brw.write({
            'pay_date': aml_brw.date,
            'pay_off': aml_brw.credit,
            'pay_inv': aml_brw.credit,
            'inv_date': aml_brw.rec_aml.date,
            'date_start': commission_policy_date_start,
            'date_stop': commission_policy_date_end,
            'days': emission_days,
            'inv_subtotal': (aml_brw.rec_aml.debit / (1 + perc_iva / 100)),
            'perc_iva': perc_iva,
            'rate_number': bardctdsc,
            'timespan': bar_day,
            'baremo_comm': bar_dcto_comm,
            'commission': comm_line,
            'commission_currency': commission_currency,
            'currency_id': aml_brw.currency_id and aml_brw.currency_id.id or
            aml_brw.company_id.currency_id.id,
        })
        return True


class CommissionSalesman(osv.Model):

    """Commission Payment : commission_salesman
    """

    _name = 'commission.salesman'
    _rec_name = 'salesman_id'

    _columns = {
        'commission_id': fields.many2one(
            'commission.payment', 'Commission Document', readonly=True),
        'salesman_id': fields.many2one(
            'res.users', 'Salesman', required=False, readonly=True),
        'comm_total': fields.float(
            'Commission Amount',
            digits_compute=dp.get_precision('Commission'), readonly=True),
        'comm_voucher_ids': fields.one2many(
            'commission.voucher',
            'comm_sale_id', 'Vouchers Affected in this commission',
            required=False),
        'comm_lines_ids': fields.one2many(
            'commission.lines',
            'comm_salespeople_id', 'Salespeople Commission Details',
            required=False),
        'currency_id':
            fields.many2one('res.currency', 'Currency', readonly=True),
        'comm_total_currency': fields.float(
            'Currency Amount',
            digits_compute=dp.get_precision('Commission'), readonly=True),
        'company_id': fields.related(
            'commission_id', 'company_id',
            string='Company',
            relation='res.company',
            type='many2one',
            store=True,
            readonly=True,
            help=('Currency at which this report will be \
                    expressed. If not selected will be used the \
                    one set in the company')),
    }


class CommissionVoucher(osv.Model):

    """Commission Payment : commission_voucher
    """

    _name = 'commission.voucher'
    _order = 'date'
    _rec_name = 'am_id'

    def _get_commission(self, cr, uid, ids, name, args, context=None):
        context = dict(context or {})
        res = {}.fromkeys(ids, 0.0)
        for brw in self.browse(cr, uid, ids, context=context):
            res[brw.id] = sum(
                [ci_brw.commission for ci_brw in brw.comm_invoice_ids])
        return res

    _columns = {
        'commission_id': fields.many2one('commission.payment', 'Commission'),
        'comm_sale_id': fields.many2one('commission.salesman', 'Salesman'),
        'am_id': fields.many2one('account.move', 'Journal Entry'),
        'comm_invoice_ids': fields.one2many(
            'commission.invoice',
            'comm_voucher_id', 'Facturas afectadas en esta comision',
            required=False),
        'date': fields.related('am_id', 'date', string='Date', type='date',
                               store=True, readonly=True),
        'commission': fields.function(
            _get_commission,
            type='float',
            string='Commission Amount',
            digits_compute=dp.get_precision('Commission')),
    }


class CommissionInvoice(osv.Model):

    """Commission Payment : commission_invoice
    """

    _name = 'commission.invoice'
    _order = 'invoice_id'

    def _get_commission(self, cr, uid, ids, name, args, context=None):
        context = dict(context or {})
        res = {}.fromkeys(ids, 0.0)
        for brw in self.browse(cr, uid, ids, context=context):
            res[brw.id] = sum(
                [cl_brw.commission for cl_brw in brw.comm_line_ids])
        return res

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'comm_voucher_id': fields.many2one('commission.voucher', 'Voucher'),
        'invoice_id': fields.many2one('account.invoice', 'Factura'),
        'comm_line_ids': fields.one2many(
            'commission.lines',
            'comm_invoice_id', 'Comision por productos', required=False),
        'pay_inv': fields.float(
            'Abono Fact.',
            digits_compute=dp.get_precision('Commission')),
        'commission': fields.function(
            _get_commission,
            type='float',
            string='Commission Amount',
            digits_compute=dp.get_precision('Commission')),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class CommissionLines2(osv.Model):

    """Commission Payment : commission_lines_2
    """

    _inherit = 'commission.lines'

    _columns = {
        'comm_invoice_id': fields.many2one('commission.invoice',
                                           'Invoice Commission'),
    }


class ResCompany(osv.Model):
    _inherit = "res.company"
    _description = 'Companies'

    _columns = {
        'comm_tax': fields.float('Default Tax for Commissions'),
    }
