from openerp.osv import osv, fields
import mx.DateTime
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp
import datetime

COMMISSION_STATES = [
    ('draft', 'Draft'),
    ('open', 'In Progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
]

COMMISSION_TYPES = [
    ('partial_payment', 'Based on Partial Payments'),
    ('fully_paid_invoice', 'Based on Fully Paid Invoices'),
]

COMMISSION_SCOPES = [
    ('whole_invoice', 'Based on Whole Invoice'),
    ('product_invoiced', 'Based on Invoiced Products '),
]


def tTime(dt):
    '''
    Trims time from "%Y-%m-%d %H:%M:%S" to "%Y-%m-%d"
    '''
    dt = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    dt = datetime.date(dt.year, dt.month, dt.day)
    return dt.strftime("%Y-%m-%d")


class commission_payment(osv.Model):

    """
    OpenERP Model : commission_payment
    """

    _name = 'commission.payment'
    _description = __doc__

    _columns = {
        'name': fields.char(
            'Commission Concept', size=256, required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'bar_id': fields.many2one(
            'baremo.book', 'Baremo', required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'date_start': fields.date(
            'Date Start', required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'date_stop': fields.date(
            'Date End', required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'total_comm': fields.float(
            'Total Commission',
            digits_compute=dp.get_precision('Commission'),
            readonly=True, states={'write': [('readonly', False)]}),
        'ret_notes': fields.text(
            'Notas para las Retenciones', readonly=True,
            states={'draft': [('readonly', False)],
                    'open': [('readonly', False)]}),
        'uninvoiced_ids': fields.one2many(
            'commission.uninvoiced',
            'commission_id', 'Transacciones sin Facturas', readonly=True,
            states={'write': [('readonly', False)]}),
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
        'saleman_ids': fields.one2many(
            'commission.saleman', 'commission_id',
            'Total de Comisiones por Vendedor', readonly=True,
            states={'write': [('readonly', False)]}),
        'user_ids': fields.many2many(
            'res.users', 'commission_users',
            'commission_id', 'user_id', 'Vendedores', required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_ids': fields.many2many(
            'account.invoice', 'commission_account_invoice', 'commission_id',
            'invoice_id', 'Invoices', readonly=True,
            states={'draft': [('readonly', False)]}),
        'voucher_ids': fields.many2many(
            'account.voucher', 'commission_account_voucher', 'commission_id',
            'voucher_id', 'Vouchers', readonly=True,
            states={'draft': [('readonly', False)]}),
        'comm_voucher_ids': fields.one2many(
            'commission.voucher',
            'commission_id', 'Vouchers afectados en esta comision',
            readonly=True, states={'write': [('readonly', False)]}),
        'comm_invoice_ids': fields.one2many(
            'commission.invoice',
            'commission_id', 'Facturas afectadas en esta comision',
            readonly=True, states={'write': [('readonly', False)]}),
        'comm_retention_ids': fields.one2many(
            'commission.retention',
            'commission_id', 'Facturas con Problemas de Retencion',
            readonly=True, states={'write': [('readonly', False)]}),
        'state': fields.selection(COMMISSION_STATES, 'Estado', readonly=True),
        'commission_type': fields.selection(
            COMMISSION_TYPES,
            string='Commission Basis', required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'commission_scope': fields.selection(
            COMMISSION_SCOPES,
            string='Commission Scope', required=False,
            readonly=True,
            states={'draft': [('readonly', False)]}),
    }
    _defaults = {
        'name': lambda *a: None,
        'total_comm': lambda *a: 0.00,
        'state': lambda *a: 'draft',
        'ret_notes': lambda *a: 'Las Facturas que se mencionan ya tienen un\
            pago registrado, pero presentan problemas con una o mas de las\
            retenciones que se indican en el cuadro, se ha tratado bajo los\
            medios existentes de identificar cuales son los porcentajes de\
            retenciones pero no ha sido posible, para generar la comision\
            sobre el pago de las mismas, es necesario el conocimiento de estos\
            valores, por lo que le increpamos a que contacte a sus asociados\
            para obtener esta informacion, su falta no afectara el calculo de\
            la comision pero retardara su ejecucion. Si considera que ha\
            habido un error por favor hable sobre el tema con el personal\
            Administrativo y de Sistemas para determinar las causas del mismo\
            y encontrar una solucion. De otra forma haga caso omiso de este\
            mensaje y su contenido',
    }

    def _prepare_based_on_payments(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        av_obj = self.pool.get('account.voucher')

        for comm_brw in self.browse(cr, uid, ids, context=context):
            invoice_ids = [(3, x.id) for x in comm_brw.invoice_ids]
            if invoice_ids:
                comm_brw.write({'invoice_ids': invoice_ids})

            date_start = comm_brw.date_start
            date_stop = comm_brw.date_stop

            # En esta busqueda restringimos que el voucher se haya
            # contabilizado y que sea un cobro bancario y este dentro de la
            # fecha estipulada
            voucher_ids = av_obj.search(
                cr, uid, [('state', '=', 'posted'),
                          ('type', '=', 'receipt'),
                          ('date', '>=', date_start),
                          ('date', '<=', date_stop)])

            comm_brw.write({
                'voucher_ids': [(6, comm_brw.id, voucher_ids)]})

        return True

    def _prepare_based_on_invoices(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        av_obj = self.pool.get('account.voucher')

        for comm_brw in self.browse(cr, uid, ids, context=context):
            comm_brw.write({'voucher_ids': []})
            date_start = comm_brw.date_start
            date_stop = comm_brw.date_stop

            # En esta busqueda restringimos que la factura de cliente se haya
            # pagado y que  este dentro de la fecha estipulada
            invoice_ids = inv_obj.search(
                cr, uid, [('state', '=', 'paid'),
                          ('type', '=', 'out_invoice'),
                          ('date_last_payment', '>=', date_start),
                          ('date_last_payment', '<=', date_stop)])

            comm_brw.write({
                'invoice_ids': [(6, comm_brw.id, invoice_ids)]})

            comm_brw.refresh()

            am_ids = [aml_brw.move_id.id for inv_brw in comm_brw.invoice_ids
                      for aml_brw in inv_brw.payment_ids]

            av_ids = av_obj.search(cr, uid, [('move_id', 'in', am_ids)],
                                   context=context)
            if av_ids:
                comm_brw.write({'voucher_ids': [(6, comm_brw.id, av_ids)]})

        return True

    def _get_commission_rate(self, cr, uid, ids, pay_date, inv_date, dcto=0.0,
                             bar_brw=None, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        # Determinar dias entre la emision de la factura del producto y el pago
        # del mismo
        pay_date = mx.DateTime.strptime(pay_date, '%Y-%m-%d')
        inv_date = mx.DateTime.strptime(inv_date, '%Y-%m-%d')
        emission_days = (pay_date - inv_date).day

        # Teniendose dias y descuento por producto se procede a buscar en el
        # baremo el correspondiente valor de comision para el producto en
        # cuestion. se entra con el numero de dias

        # Esta busqueda devuelve los dias ordenadados de menor a mayor dia, de
        # acuerdo con lo estipulado que se ordenaria en el modulo baremo
        bar_day_ids = bar_brw and bar_brw.bar_ids or comm_brw.bar_id.bar_ids

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
                    if (dcto - dcto_id.porc_disc) <= 0.01:
                        bardctdsc = dcto_id.porc_disc
                        if bardctdsc == 0.0:
                            # cuando el descuento en baremo es cero (0) no
                            # aparece reflejado, forzamos a que sea un cero (0)
                            # string.
                            bardctdsc = 0.0
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

    def _get_commission_payment_on_invoice_line(self, cr, uid, ids, pay_id,
                                                context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)

        avl_obj = self.pool.get('account.voucher.line')
        prod_prices = self.pool.get('product.historic.price')
        sale_noids = self.pool.get('commission.sale.noid')
        noprice_ids = self.pool.get('commission.noprice')
        comm_line_ids = self.pool.get('commission.lines')

        payment_brw = avl_obj.browse(cr, uid, pay_id, context=context)
        if not payment_brw.amount:
            return True

        # Si esta aqui dentro es porque esta linea tiene una id valida
        # de una factura.
        inv_brw = payment_brw.move_line_id.invoice

        # Obtener el vendedor del partner
        saleman = inv_brw.partner_id.user_id

        # Revision de cada linea de factura (productos)
        for inv_lin in inv_brw.invoice_line:

            # Verificar si tiene producto asociado
            if inv_lin.product_id:
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
                    if inv_brw.date_invoice >= tTime(prod_prices_brw.name):
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
                    if list_price:
                        dcto = round((list_price - price_unit) * 100 /
                                     list_price, 1)
                    rate_item = dcto

                    commission_params = self._get_commission_rate(
                        cr, uid, comm_brw.id,
                        payment_brw.voucher_id.date,
                        inv_brw.date_invoice, dcto=0.0,
                        bar_brw=inv_brw.partner_id.baremo_id)

                    bar_day = commission_params['bar_day']
                    bar_dcto_comm = commission_params['bar_dcto_comm']
                    bardctdsc = commission_params['bardctdsc']
                    emission_days = commission_params['emission_days']

                    #############################################
                    # CALCULO DE COMISION POR LINEA DE PRODUCTO #
                    #############################################

                    penbxlinea = payment_brw.amount * (
                        inv_lin.price_subtotal /
                        inv_brw.amount_untaxed)
                    fact_sup = 1 - 0.0 / 100 - 0.0 / 100
                    fact_inf = 1 + (0.0 / 100) * (1 - 0.0 / 100) - \
                        0.0 / 100 - 0.0 / 100

                    comm_line = penbxlinea * fact_sup * (
                        bar_dcto_comm / 100) / fact_inf

                    # Generar las lineas de comision por cada producto
                    comm_line_ids.create(
                        cr, uid, {
                            'commission_id': comm_brw.id,
                            'voucher_id': payment_brw.voucher_id.id,
                            'name':
                            payment_brw.voucher_id.number and
                            payment_brw.voucher_id.number or '/',
                            'pay_date': payment_brw.voucher_id.date,
                            'pay_off': payment_brw.voucher_id.amount,
                            'concept': payment_brw.id,
                            'invoice_id':
                            payment_brw.move_line_id.invoice.id,
                            'invoice_num': inv_brw.number,
                            'partner_id': inv_brw.partner_id.id,
                            'saleman_name': saleman and saleman.name,
                            'saleman_id': saleman and saleman.id,
                            'pay_inv': payment_brw.amount,
                            'inv_date': inv_brw.date_invoice,
                            'days': emission_days,
                            'inv_subtotal': inv_brw.amount_untaxed,
                            'item': inv_lin.name,
                            'product_id': inv_lin.product_id.id,
                            'price_unit': price_unit,
                            'price_subtotal': inv_lin.price_subtotal,
                            'price_list': list_price,
                            'price_date': list_date,
                            'rate_item': rate_item,
                            'rate_number': bardctdsc,
                            'timespan': bar_day,
                            'baremo_comm': bar_dcto_comm,
                            'commission': comm_line,
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

    def _get_commission_payment_on_invoice(self, cr, uid, ids, pay_id,
                                           context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)

        avl_obj = self.pool.get('account.voucher.line')
        comm_line_ids = self.pool.get('commission.lines')

        payment_brw = avl_obj.browse(cr, uid, pay_id, context=context)
        if not payment_brw.amount:
            return True

        # Si esta aqui dentro es porque esta linea tiene una id valida
        # de una factura.
        inv_brw = payment_brw.move_line_id.invoice

        # Obtener el vendedor del partner
        saleman = inv_brw.partner_id.user_id

        commission_params = self._get_commission_rate(
            cr, uid, comm_brw.id,
            payment_brw.voucher_id.date,
            inv_brw.date_invoice, dcto=0.0,
            bar_brw=inv_brw.partner_id.baremo_id)

        bar_day = commission_params['bar_day']
        bar_dcto_comm = commission_params['bar_dcto_comm']
        bardctdsc = commission_params['bardctdsc']
        emission_days = commission_params['emission_days']

        #############################################
        # CALCULO DE COMISION POR LINEA DE PRODUCTO #
        #############################################

        penbxlinea = payment_brw.amount * (
            inv_brw.amount_untaxed /
            inv_brw.amount_untaxed)
        fact_sup = 1 - 0.0 / 100 - 0.0 / 100
        fact_inf = 1 + (0.0 / 100) * (1 - 0.0 / 100) - \
            0.0 / 100 - 0.0 / 100

        comm_line = penbxlinea * fact_sup * (
            bar_dcto_comm / 100) / fact_inf

        # Generar las lineas de comision por cada producto
        comm_line_ids.create(
            cr, uid, {
                'commission_id': comm_brw.id,
                'voucher_id': payment_brw.voucher_id.id,
                'name':
                payment_brw.voucher_id.number and
                payment_brw.voucher_id.number or '/',
                'pay_date': payment_brw.voucher_id.date,
                'pay_off': payment_brw.voucher_id.amount,
                'concept': payment_brw.id,
                'invoice_id':
                payment_brw.move_line_id.invoice.id,
                'invoice_num': inv_brw.number,
                'partner_id': inv_brw.partner_id.id,
                'saleman_name': saleman and saleman.name,
                'saleman_id': saleman and saleman.id,
                'pay_inv': payment_brw.amount,
                'inv_date': inv_brw.date_invoice,
                'days': emission_days,
                'inv_subtotal': inv_brw.amount_untaxed,
                'rate_number': bardctdsc,
                'timespan': bar_day,
                'baremo_comm': bar_dcto_comm,
                'commission': comm_line,
            }, context=context)

        return True

    def _get_commission_payment(self, cr, uid, ids, pay_id, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        if comm_brw.commission_scope == 'product_invoiced':
            self._get_commission_payment_on_invoice_line(cr, uid, ids, pay_id,
                                                         context=context)
        elif comm_brw.commission_scope == 'whole_invoice':
            self._get_commission_payment_on_invoice(cr, uid, ids, pay_id,
                                                    context=context)

        return True

    def _commission_based_on_payments(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}

        uninvoiced_pays = self.pool.get('commission.uninvoiced')
        avl_obj = self.pool.get('account.voucher.line')

        for comm_brw in self.browse(cr, uid, ids, context=context):
            # Desvincular lineas existentes, si las hubiere
            comm_brw.unlink()

            # Obtener la lista de asesores/vendedores a los cuales se les hara
            # el calculo de comisiones
            user_ids = []
            user_ids = [line.id for line in comm_brw.user_ids]

            payment_ids = []
            uninvoice_payment_ids = []

            for av_brw in comm_brw.voucher_ids:
                # Leer cada una de las lineas de los vouchers
                for avl_brw in av_brw.line_cr_ids:
                    pay_line_vendor = avl_brw.partner_id.user_id and \
                        avl_brw.partner_id.user_id.id or False
                    if pay_line_vendor in user_ids:

                        # Verificar si esta linea tiene factura y la comision
                        # del pago no se ha pagado
                        if avl_brw.move_line_id and \
                                avl_brw.move_line_id.invoice and not \
                                avl_brw.paid_comm:
                            payment_ids.append(avl_brw.id)
                        else:
                            uninvoice_payment_ids.append(avl_brw.id)

            for pay_id in payment_ids:
                # se procede con la preparacion de las comisiones.
                self._get_commission_payment(cr, uid, ids, pay_id,
                                             context=context)

            for payment_brw in avl_obj.browse(cr, uid, uninvoice_payment_ids,
                                              context=context):
                # Si esta aqui dentro es porque esta linea (transaccion) no
                # tiene factura valida, se escribe entonces una linea en una
                # vista donde se muestran las transacciones que no tienen
                # factura asociada para su correccion si aplica. tampoco se ha
                # pagado la comision del mismo solo se incluiran pagos que sean
                # de cuentas cobrables, puesto que las de otra naturaleza, no
                # tienen sentido mostrarlas aqui.
                if payment_brw.account_id.type == 'receivable':
                    uninvoiced_pays.create(cr, uid, {
                        'commission_id': comm_brw.id,
                        'payment_id': payment_brw.id,
                    }, context=context)
        return True

    def _commission_based_on_invoices(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}

        for comm_brw in self.browse(cr, uid, ids, context=context):
            # Desvincular lineas existentes, si las hubiere
            comm_brw.unlink()

            # Obtener la lista de asesores/vendedores a los cuales se les hara
            # el calculo de comisiones
            user_ids = [line.id for line in comm_brw.user_ids]
            invoice_ids = [inv_brw.id for inv_brw in comm_brw.invoice_ids]
            payment_ids = []

            for av_brw in comm_brw.voucher_ids:
                # Leer cada una de las lineas de los vouchers
                for avl_brw in av_brw.line_cr_ids:
                    pay_line_vendor = avl_brw.partner_id.user_id and \
                        avl_brw.partner_id.user_id.id or False
                    if pay_line_vendor in user_ids:

                        # Verificar si esta linea tiene factura y la comision
                        # del pago no se ha pagado
                        if avl_brw.move_line_id and \
                                avl_brw.move_line_id.invoice and \
                                avl_brw.move_line_id.invoice.id in invoice_ids\
                                and not avl_brw.paid_comm:
                            payment_ids.append(avl_brw.id)

            for pay_id in payment_ids:
                # se procede con la preparacion de las comisiones.
                self._get_commission_payment(cr, uid, ids, pay_id,
                                             context=context)
        return True

    def _post_processing(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        user = uid
        comm_line_ids = self.pool.get('commission.lines')
        saleman_ids = self.pool.get('commission.saleman')
        # users_ids = self.pool.get ('commission.users')
        comm_voucher_ids = self.pool.get('commission.voucher')
        comm_invoice_ids = self.pool.get('commission.invoice')

        # habiendo recorrido todos los vouchers, mostrado todos los elementos
        # que necesitan correccion se procede a agrupar las comisiones por
        # vendedor para mayor facilidad de uso

        # recargando las lineas que se han creado
        saleman_ids = self.pool.get('commission.saleman')
        comm_voucher_ids = self.pool.get('commission.voucher')

        for commission in self.browse(cr, user, ids, context=context):

            # recoge todos los vendedores y suma el total de sus comisiones
            sale_comm = {}
            # ordena en un arbol todas las lineas de comisiones de producto
            criba = {}
            for comm_line in commission.comm_line_ids:
                vendor_id = comm_line.saleman_id.id
                voucher_id = comm_line.voucher_id.id
                invoice_id = comm_line.invoice_id.id
                comm_line_id = comm_line.id

                if vendor_id not in sale_comm.keys():
                    sale_comm[vendor_id] = [comm_line.saleman_name, 0.0]
                sale_comm[vendor_id][1] += comm_line.commission

                if vendor_id not in criba.keys():
                    criba[vendor_id] = {}

                if voucher_id not in criba[vendor_id].keys():
                    criba[vendor_id][voucher_id] = [comm_line.pay_date, {}]

                if invoice_id not in criba[vendor_id][voucher_id][1].keys():
                    criba[vendor_id][voucher_id][1][invoice_id] = {}

                if len(criba[vendor_id][voucher_id][1][invoice_id]) == 0:
                    criba[vendor_id][voucher_id][1][invoice_id] = [
                        [], comm_line.pay_inv, comm_line.perc_ret_iva,
                        comm_line.perc_ret_islr, comm_line.perc_ret_im]

                criba[vendor_id][voucher_id][1][
                    invoice_id][0].append(comm_line_id)

            # escribir el total para cada vendedor encontrado
            total_comm = 0
            for vendor_key in criba.keys():
                vendor_id = saleman_ids.create(cr, user, {
                    'commission_id': commission.id,
                    'saleman_id': vendor_key,
                    'saleman_name': sale_comm[vendor_key][0],
                    'comm_total': sale_comm[vendor_key][1],
                }, context=context)

                total_comm += sale_comm[vendor_key][1]

                for voucher_key in criba[vendor_key].keys():
                    voucher_id = comm_voucher_ids.create(cr, user, {
                        'commission_id': commission.id,
                        'comm_sale_id': vendor_id,
                        'voucher_id': voucher_key,
                        'date': criba[vendor_key][voucher_key][0],
                    }, context=context)

                    for inv_key in criba[vendor_key][voucher_key][1].keys():
                        invoice_id = comm_invoice_ids.create(cr, user, {
                            'commission_id': commission.id,
                            'comm_voucher_id': voucher_id,
                            'invoice_id': inv_key,
                            'pay_inv':
                            criba[vendor_key][voucher_key][1][inv_key][1],
                            'ret_iva':
                            criba[vendor_key][voucher_key][1][inv_key][2],
                            'ret_islr':
                            criba[vendor_key][voucher_key][1][inv_key][3],
                            'ret_im':
                            criba[vendor_key][voucher_key][1][inv_key][4],
                        }, context=context)

                        for idx in \
                                criba[vendor_key][voucher_key][1][inv_key][0]:
                            comm_line_ids.write(cr, user, idx, {
                                'comm_invoice_id': invoice_id,
                            }, context=context)

            self.write(cr, user, ids, {
                'total_comm': total_comm,
            })
        return True

    def prepare(self, cr, user, ids, context=None):
        """
        Este metodo recorre los elementos de account_voucher y verifica al
        menos tres (3) caracteristicas primordiales para continuar con los
        vouchers: estas caracteristicas son:
        - bank_rec_voucher: quiere decir que el voucher es de un deposito
        bancario (aqui aun no se ha considerado el trato que se le da a los
        cheques devueltos).
        - posted: quiere decir que el voucher ya se ha contabilizado, condicion
        necesaria pero no suficiente.
        - move_ids: si la longitud de estos es distinto de cero es porque este
        voucher es por completo valido, es decir, realmente tiene asientos
        contables registrados.

        Si estas tres (3) condiciones se cumplen entonces se puede proceder a
        realizar la revision de las lineas de pago.


        @param cr: cursor to database
        @param user: id of current user
        @param ids: list of record ids to be process
        @param context: context arguments, like lang, time zone

        @return: return a result
        """
        uid = user
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        comm_brw = self.browse(cr, uid, ids[0], context=context)
        if comm_brw.commission_type == 'partial_payment':
            self._prepare_based_on_payments(cr, uid, ids, context=context)
            self._commission_based_on_payments(cr, uid, ids, context=context)
        elif comm_brw.commission_type == 'fully_paid_invoice':
            self._prepare_based_on_invoices(cr, uid, ids, context=context)
            self._commission_based_on_invoices(cr, uid, ids, context=context)

        self._post_processing(cr, uid, ids, context=context)

        self.write(cr, user, ids, {
            'state': 'open',
        })
        return True

    def pre_process(self, cr, user, ids, context=None):
        commissions = self.browse(cr, user, ids, context=None)
        for commission in commissions:
            self.prepare(cr, user, ids, context=None)

            if commission.comm_line_ids:
                self.write(cr, user, ids, {
                    'state': 'decide',
                })
            else:
                raise osv.except_osv(
                    _('Atencion !'),
                    _('No Existen Lineas de Comision x Producto que procesar \
                      !!!'))

            if not commission.noprice_ids:
                self.write(cr, user, ids, {
                    'state': 'decide',
                })
            else:
                raise osv.except_osv(_('Atencion !'), _(
                    'Debe primero solucionar el asunto de los Productos sin \
                    Listas de Precio para las fechas especificadas antes de \
                    continuar'))
        return True

    def delete(self, cr, user, ids, context=None):

        self.unlink(cr, user, ids, context=None)
        self.write(cr, user, ids, {
            'state': 'draft',
            'total_comm': None,
        })
        return True

    def unlink(self, cr, user, ids, context=None):

        ids = isinstance(ids, (int, long)) and [ids] or ids

        uninvoiced_pays = self.pool.get('commission.uninvoiced')
        sale_noids = self.pool.get('commission.sale.noid')
        noprice_ids = self.pool.get('commission.noprice')
        comm_line_ids = self.pool.get('commission.lines')
        saleman_ids = self.pool.get('commission.saleman')
        # users_ids = self.pool.get ('commission.users')
        comm_voucher_ids = self.pool.get('commission.voucher')
        comm_invoice_ids = self.pool.get('commission.invoice')
        comm_retention_ids = self.pool.get('commission.retention')

        for commission in self.browse(cr, user, ids, context=None):
            ###
            # Desvincular todos los elementos que esten conectados a este
            # calculo de comisiones
            # * Desvinculando los pagos sin facturas
            uninvoiced_pays.unlink(
                cr, user, [line.id for line in commission.uninvoiced_ids])
            # * Desvinculando los articulos sin id
            sale_noids.unlink(cr, user, [
                              line.id for line in commission.sale_noids])
            # * Desvinculando los productos sin fecha
            noprice_ids.unlink(cr, user, [
                               line.id for line in commission.noprice_ids])
            # * Desvinculando las lineas de comisiones
            comm_line_ids.unlink(
                cr, user, [line.id for line in commission.comm_line_ids])
            # * Desvinculando los totales por vendedor
            saleman_ids.unlink(
                cr, user, [line.id for line in commission.saleman_ids])
            # * Desvinculando los vendedores
            # users_ids.unlink(cr, user, [line.id for line in
            # commission.users_ids])
            # * Desvinculando los vouchers afectados
            comm_voucher_ids.unlink(
                cr, user, [line.id for line in commission.comm_voucher_ids])
            # * Desvinculando los vouchers afectados
            comm_invoice_ids.unlink(
                cr, user, [line.id for line in commission.comm_invoice_ids])
            # * Desvinculando las facturas con problemas de retenciones
            comm_retention_ids.unlink(
                cr, user, [line.id for line in commission.comm_retention_ids])
            ###

    def decide(self, cr, user, ids, context=None):
        commissions = self.browse(cr, user, ids, context=None)
        avl = self.pool.get('account.voucher.line')
        # escribir en el avl el estado buleano de paid_comm a True para indicar
        # que ya esta comision se esta pagando
        for commission in commissions:
            avl.write(cr, user, [line.concept.id for line in
                                 commission.comm_line_ids],
                      {'paid_comm': True})

        self.write(cr, user, ids, {
            'state': 'done',
        })

    def going_back(self, cr, user, ids, context=None):
        self.write(cr, user, ids, {
            'state': 'open',
        })
        return True


class commission_uninvoiced(osv.Model):

    """
    Commission Payment Uninvoiced : commission_uninvoiced
    """

    _name = 'commission.uninvoiced'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'payment_id': fields.many2one(
            'account.voucher.line', 'Descripcion de Transaccion'),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class commission_sale_noid(osv.Model):

    """
    Commission Payment : commission_sale_noid
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


class commission_noprice(osv.Model):

    """
    Commission Payment : commission_sale_noid
    """

    _name = 'commission.noprice'
    _order = 'product_id'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'date': fields.date('Fecha'),
        'invoice_num': fields.char('Invoice Number', size=256),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class commission_lines(osv.Model):

    """
    Commission Payment : commission_lines
    """

    _name = 'commission.lines'
    _order = 'saleman_id'

    _columns = {
        'commission_id': fields.many2one(
            'commission.payment', 'Comision', required=True),
        'name': fields.char('Transaccion', size=256, required=True),
        'pay_date': fields.date('Fecha', required=True),
        'pay_off': fields.float(
            'Pago',
            digits_compute=dp.get_precision('Commission')),

        'voucher_id': fields.many2one('account.voucher', 'Voucher'),

        'concept': fields.many2one('account.voucher.line', 'Concepto'),
        'invoice_id': fields.many2one('account.invoice', 'Doc.'),
        'invoice_num': fields.char('Doc.', size=256),
        'partner_id': fields.many2one('res.partner', 'Empresa'),
        'saleman_name': fields.char('Vendedor', size=256, required=True),
        'saleman_id': fields.many2one('res.users', 'Vendedor', required=True),
        'pay_inv': fields.float(
            'Abono Fact.',
            digits_compute=dp.get_precision('Commission')),

        'inv_date': fields.date('Fecha Doc.'),
        'days': fields.float(
            'Dias',
            digits_compute=dp.get_precision('Commission')),

        'inv_subtotal': fields.float(
            'SubTot. Doc.',
            digits_compute=dp.get_precision('Commission')),

        'item': fields.char('Item', size=256, required=False),
        'product_id': fields.many2one('product.product', 'Item'),
        'price_unit': fields.float(
            'Prec. Unit.',
            digits_compute=dp.get_precision('Commission')),
        'price_subtotal': fields.float(
            'SubTot. Item',
            digits_compute=dp.get_precision('Commission')),

        'price_list': fields.float(
            'Precio Lista',
            digits_compute=dp.get_precision('Commission')),
        'price_date': fields.date('Fecha Lista'),

        'perc_ret_islr': fields.float(
            'Ret ISLR (%)',
            digits_compute=dp.get_precision('Commission')),
        'perc_ret_im': fields.float(
            'Ret IM (%)',
            digits_compute=dp.get_precision('Commission')),
        'perc_ret_iva': fields.float(
            'Ret IVA (%)',
            digits_compute=dp.get_precision('Commission')),
        'perc_iva': fields.float(
            'IVA (%)',
            digits_compute=dp.get_precision('Commission')),

        'rate_item': fields.float(
            'Dcto. (%)',
            digits_compute=dp.get_precision('Commission')),

        'rate_number': fields.float(
            'Bar. Rate (%)',
            digits_compute=dp.get_precision('Commission')),
        'timespan': fields.float(
            'Bar. Dias',
            digits_compute=dp.get_precision('Commission')),
        'baremo_comm': fields.float(
            'Baremo %Comm.',
            digits_compute=dp.get_precision('Commission')),
        'commission': fields.float(
            'Comm. / Item',
            digits_compute=dp.get_precision('Commission')),
    }

    _defaults = {
        'name': lambda *a: None,
    }


class commission_saleman(osv.Model):

    """
    Commission Payment : commission_saleman
    """

    _name = 'commission.saleman'
    _order = 'saleman_name'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'saleman_name': fields.char('Vendedor', size=256, required=True),
        'saleman_id': fields.many2one('res.users', 'Vendedor', required=True),
        'comm_total': fields.float(
            'Comision a pagar',
            digits_compute=dp.get_precision('Commission')),
        'comm_voucher_ids': fields.one2many(
            'commission.voucher',
            'comm_sale_id', 'Vouchers afectados en esta comision',
            required=False),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class commission_voucher(osv.Model):

    """
    Commission Payment : commission_voucher
    """

    _name = 'commission.voucher'
    _order = 'date'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'comm_sale_id': fields.many2one('commission.saleman', 'Vendedor'),
        'voucher_id': fields.many2one('account.voucher', 'Voucher'),
        'comm_invoice_ids': fields.one2many(
            'commission.invoice',
            'comm_voucher_id', 'Facturas afectadas en esta comision',
            required=False),
        'date': fields.date('Fecha'),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class commission_invoice(osv.Model):

    """
    Commission Payment : commission_invoice
    """

    _name = 'commission.invoice'
    _order = 'invoice_id'

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
        'ret_iva': fields.float(
            '% Ret. IVA', digits_compute=dp.get_precision('Commission')),
        'ret_islr': fields.float(
            '% Ret. ISLR', digits_compute=dp.get_precision('Commission')),
        'ret_im': fields.float('% Ret. IM',
                               digits_compute=dp.get_precision('Commission')),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class commission_lines_2(osv.Model):

    """
    Commission Payment : commission_lines_2
    """

    _inherit = 'commission.lines'

    _columns = {
        'comm_invoice_id': fields.many2one('commission.invoice',
                                           'Factura Relacional Interna'),
    }


class commission_retention(osv.Model):

    """
    Commission Payment : commission_retention
    """

    _name = 'commission.retention'
    _order = 'invoice_id'

    _columns = {
        'name': fields.char('Comentario', size=256),
        'commission_id': fields.many2one('commission.payment', 'Comision'),
        'invoice_id': fields.many2one('account.invoice', 'Factura'),
        'voucher_id': fields.many2one('account.voucher', 'Pagado con...'),
        'date': fields.date('Fecha'),
        'ret_iva': fields.boolean('Ret. IVA'),
        'ret_islr': fields.boolean('Ret. ISLR'),
        'ret_im': fields.boolean('Ret. IM'),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class VoucherLines(osv.Model):
    _inherit = 'account.voucher.line'

    _columns = {
        'paid_comm': fields.boolean('Comision Pagada?'),
        'partner_id': fields.related('voucher_id', 'partner_id',
                                     type='many2one', relation='res.partner',
                                     string='Partner', store=True),
    }
    _defaults = {
        'paid_comm': lambda *a: False,
    }


class account_invoice(osv.Model):

    def _date_last_payment(self, cr, uid, ids, fieldname, arg, context=None):
        res = {}.fromkeys(ids, None)
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if inv_brw.type != 'out_invoice':
                continue
            date_last_payment = inv_brw.date_last_payment
            for aml_brw in inv_brw.payment_ids:
                if aml_brw.journal_id.type in ('bank', 'cash'):
                    date_last_payment = aml_brw.date > date_last_payment and \
                        aml_brw.date or date_last_payment

            res[inv_brw.id] = date_last_payment
        return res

    def _get_related_date(self, cr, uid, ids, context=None):
        res = set([])
        aml_obj = self.pool.get('account.move.line')
        for aml_brw in aml_obj.browse(cr, uid, ids, context=context):
            if aml_brw.invoice:
                res.add(aml_brw.invoice.id)
        return list(res)

    _inherit = "account.invoice"
    _columns = {
        'date_last_payment': fields.function(
            _date_last_payment, string='Last Payment Date', type="date",
            store={
                _inherit: (lambda s, c, u, ids, cx: ids, ['residual'], 15),
                'account.move.line': (_get_related_date, None, 20),
            }),
    }
