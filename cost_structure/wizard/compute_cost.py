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

from openerp.osv import osv, fields
import openerp.tools as tools
from openerp.tools.translate import _

from tools import config
import openerp.netsvc as netsvc
from openerp.addons.decimal_precision import decimal_precision as dp
from DateTime import DateTime
import time
import datetime
invo_cost = {}


class compute_cost(osv.TransientModel):

    _name = 'compute.cost'
    _columns = {
        'product_ids': fields.many2many('product.product', 'product_rel',
            'product1', 'product2', 'Product',
            help="Select the product to compute cost"),
        'product': fields.boolean('Product',
            help="To select compute by product"),
        'categ': fields.boolean('Category',
            help="To select compute by category"),
        'bolfili': fields.boolean('Boolean FIFO LIFO'),
        'categ_ids': fields.many2many('product.category', 'categ_rel',
            'categ1', 'categ2', 'Product Category',
            help="Select the category to compute cost"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year',
            help="Fiscal Year to search invoice between indicated period"),
        'period_id': fields.many2one('account.period', 'Period',
            help="Period to search invoice between indicated period"),
        'all': fields.boolean('ALL', help="To compute cost for all products"),
        'fifo': fields.boolean('FIFO',
            help="To compute cost FIFO for products"),
        'lifo': fields.boolean('LIFO',
            help="To compute cost LIFO for products"),

    }

    def compute_cost_fifo(self, cr, uid, dic_comp, dic_vent, dic_nc_com, dic_nc_vent, context={}):
        '''
        Method that performs the actual FIFO cost, receiving the dictionaries of every movement,
        to perform the calculations for caesarean
        @param dic_comp Dictionary with all moves of purchase order of the products
        @param dic_vent Dictionary with all moves of sale order of the products
        @param dic_nc_com Dictionary with all moves of N/C purchase order of the products
        @param dic_nc_vent Dictionary with all moves of N/C sale order of the products
        These dictionaries are composed of lists of tuples, where quecada tuple is a line in their respective invoice
        '''
        invoice_obj = self.pool.get('account.invoice')
        rec_com = {}
        rec_vent = {}
        [rec_com.update({invoice_obj.browse(cr, uid, e[-1],
                            context=context).parent_id.id:e[0]})
                            for i in dic_nc_com for e in dic_nc_com.get(i)]
        [rec_vent.update({invoice_obj.browse(cr, uid, h[-1],
                            context=context).parent_id.id:h[0]})
                            for g in dic_nc_vent for h in dic_nc_vent.get(g)]
        cont = 0
        cont_qty = 0
        price = 0
        for i in dic_comp:
            aux = (d for d in dic_comp.get(i, False))
            try:
                fifo = aux and aux.next()
            except:
                raise osv.except_osv(_('Invalid action !'), _(
                    "Impossible to calculate FIFO not have invoices\
                    in this period  "))
            qty_aux = fifo and fifo[0] in rec_com.keys() and fifo[
                3] - rec_com.get(fifo[0], False) or fifo[3]
            cost_aux = fifo and fifo[1]

            for d in dic_vent.get(i):
                cont = d[-1] in rec_vent.keys() and\
                                            (cont + d[0]) - rec_vent.get(d[-1],
                                            False) or cont + d[0]

                if cont <= qty_aux:
                    price = (d[0] * cost_aux) + price
                else:
                    rest = cont - d[0]
                    rest = qty_aux - cont
                    price = rest > 0 and (rest * cost_aux) + price
                    fifo = aux.next()
                    cont_qty = cont + cont_qty
                    cont = 0
                    qty_aux = fifo and fifo[0] in rec_com.keys() and fifo[
                        3] - rec_com.get(fifo[0], False) or fifo[3]
                    cost_aux = fifo and fifo[1]
        cont_qty = cont + cont_qty
        if price and cont_qty or cont:

            cost = price / (cont_qty > 0 and cont_qty or cont > 0 and cont)
        return True

    def search_invoice(self, cr, uid, ids, dict, type, period, company, date,
                        context=None):
        '''
        Return a list of invoices ids that have products sended in the dict
        #~ ('period_id','=',period),
        '''
        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')
        if date:
            invo_ids = invo_obj.search(
                cr, uid, [(
                    'invoice_line.product_id', 'in', tuple(dict.keys())),
                    ('type', '=', type),
                    ('company_id',
                     '=', company),
                    ('date_invoice', '>=', date)],
                order='date_invoice')

        else:
            invo_ids = invo_obj.search(
                cr, uid, [(
                    'invoice_line.product_id', 'in', tuple(dict.keys())),
                    ('type', '=', type),
                    ('state', 'in', (
                     'open', 'paid')),
                    ('company_id', '=', company)],
                order='date_invoice')
        return invo_ids

    def compute_actual_cost(self, cr, uid, ids, dic_comp, dic_vent, dic_nc_com,
                                                    dic_nc_vent, context={}):
        '''
        Method that performs the actual average cost, receiving the dictionaries of every movement,
        to perform the calculations for caesarean
        @param dic_comp Dictionary with all moves of purchase order of the products
        @param dic_vent Dictionary with all moves of sale order of the products
        @param dic_nc_com Dictionary with all moves of N/C purchase order of the products
        @param dic_nc_vent Dictionary with all moves of N/C sale order of the products
        These dictionaries are composed of lists of tuples, where quecada tuple is a line in their respective invoice
        '''
        product_obj = self.pool.get('product.product')
        invoice_obj = self.pool.get('account.invoice')
        aux = {}
        dat = DateTime()
        for i in dic_comp:
            #~ print "dic_nc_com.get(i)",dic_nc_com.get(431)
            #~ print " dic_nc_vent.get(i)", dic_nc_vent.get(431)
            #~ print " dic_comp.get(i)", dic_comp.get(431)
            #~ print " dic_vent.get(i)", dic_vent.get(431)
            product_brw = product_obj.browse(cr, uid, i, context=context)
            if dic_comp.get(i, False) and len(dic_comp[i]) > 0:
                qty = (sum([a[3] for a in dic_comp.get(i)])) - \
                      (sum([a[3] for a in dic_nc_com.get(i)])) + \
                      (sum([a[0] for a in dic_nc_vent.get(i)])) - \
                      (sum([a[1] for a in dic_vent.get(i)]))
                price = (sum([a[2] for a in dic_comp.get(i)])) - \
                        (sum([a[2] for a in dic_nc_com.get(i)])) + \
                        (sum([a[1] for a in dic_nc_vent.get(i)])) - \
                        (sum([a[2] for a in dic_vent.get(i)]))

                if qty > 0:
                    cost = price / qty
                    aux.update({i: [price, qty, cost and
                                    cost, dic_comp[i] and
                                    dic_comp[i][0] and dic_comp[i][0][4] or []]})
                    date = dic_comp.get(i)[-1] and dic_comp.get(i)[-1][0] and \
                        invoice_obj.browse(cr, uid, dic_comp.get(
                                           i)[-1][0], context=context).date_invoice
                    date = date and date.split('-') or False
                    time = date and date[2].split(' ')
                    time = time and time[1].split(":")
                    date = date and time and datetime.datetime(
                                                        int(date[0]),
                                                        int(date[1]),
                                                        int(date[2][0:2]),
                                                        int(time[0]),
                                                        int(time[1]),
                                                        int(time[2])) or False
                    date = date and date + datetime.timedelta(
                        seconds=1) or dat.strftime('%Y/%m/%d %H:%M:%S')

                    if context.get('not_write', False):
                        pass
                    else:
                        if context.get('invoice_cancel', False):
                            product_obj.write(cr, uid, [product_brw.id],
                                              {'cost_ult': cost,
                                               'date_cost_ult': date,
                                               'qty_ult': aux.get(i)
                                               and aux.get(i)[1],
                                               'ult_om': aux.get(i)[-1] or [],
                                               'date_ult_om': date},
                                              context=context)

                        if product_brw.property_cost_structure and\
                        product_brw.cost_ult > 0:
                            product_obj.write(cr, uid, [product_brw.id],
                                  {'cost_ult': cost,
                                   'date_cost_ult': date,
                                   'qty_ult': aux.get(i)
                                   and aux.get(i)[1],
                                   'cost_ant': product_brw.cost_ult,
                                   'qty_ant': product_brw.qty_ult,
                                   'date_cost_ant': product_brw.date_cost_ult,
                                   'ult_om': aux.get(i)[-1] or [],
                                   'date_ult_om': date,
                                   'ant_om': product_brw.ult_om
                                   and product_brw.ult_om.id
                                   or [],
                                   'date_ant_om': product_brw.date_ult_om},
                                  context=context)
                        else:
                            product_obj.write(cr, uid, [product_brw.id],
                                              {'cost_ult': cost,
                                               'date_cost_ult': date,
                                               'qty_ult': aux.get(i)
                                               and aux.get(i)[1],
                                               'ult_om': aux.get(i)[-1] or [],
                                               'date_ult_om': date},
                                                            context=context)
        return aux

    def update_dictionary(self, cr, uid, ids, dict, inv_ids, purchase,
                            context=None):
        '''
        Update a dict send with move all this product
        '''

        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')
        if purchase:
            [dict[line.product_id.id].append((invo.id, line.price_unit,
                                              line.price_subtotal,
                                              line.quantity, line.uos_id and
                                              line.uos_id.id, invo.date_invoice,
                                              line.id, line.aux_financial,
                                              line.aux_qty, invo.cancel_check))
                for invo in invo_obj.browse(cr, uid, inv_ids, context=context)
                for line in invo.invoice_line if line and
                line.product_id and
                line.product_id.id in dict and
                type(dict[line.product_id.id]) is list]

        else:

            [dict[line.product_id.id].append((invo.id, line.price_unit,
                                              line.price_subtotal, line.quantity,
                                              line.uos_id and line.uos_id.id,
                                              invo.date_invoice))
                for invo in invo_obj.browse(cr, uid, inv_ids, context=context)
             for line in invo.invoice_line if line and
                line.product_id and
                line.product_id.id in dict and
                type(dict[line.product_id.id]) is list]

        return dict

    def compute_actual_cost_purchase(self, cr, uid, ids, dic_comp, dic_vent,
                                    dic_nc_com, dic_nc_vent, context={}):
        '''
        Method that performs the actual average cost, receiving the dictionaries of every movement,
        to perform the calculations for caesarean
        @param dic_comp Dictionary with all moves of purchase order of the products
        @param dic_vent Dictionary with all moves of sale order of the products
        @param dic_nc_com Dictionary with all moves of N/C purchase order of the products
        @param dic_nc_vent Dictionary with all moves of N/C sale order of the products
        These dictionaries are composed of lists of tuples, where quecada tuple is a line in their respective invoice
        '''
        product_obj = self.pool.get('product.product')
        invoice_line_obj = self.pool.get('account.invoice.line')
        aux = {}
        dat = DateTime()
        list = []
        for i in dic_comp:
            aux.update({i: []})
            product_brw = product_obj.browse(cr, uid, i, context=context)
            date = False
            evalu = 'DateTime(a[5]) <= DateTime(aux2[5])'
            if dic_comp.get(i, False) and len(dic_comp[i]) > 0:
                d = 0
                gene = (e for e in dic_comp.get(i))

                while d != len(dic_comp.get(i)):
                    aux2 = gene.next()

                    qty = (sum([a[3] for a in dic_comp.get(i) if eval(evalu) ])) - \
                          (sum([a[3] for a in dic_nc_com.get(i) if eval(evalu)])) + \
                          (sum([a[0] for a in dic_nc_vent.get(i) if eval(evalu)] )) - \
                          (sum([a[1] for a in dic_vent.get(
                              i) if eval(evalu)]))

                    price = (sum([a[2] for a in dic_comp.get(i) if eval(evalu) ])) - \
                            (sum([a[2] for a in dic_nc_com.get(i) if eval(evalu) ])) + \
                            (sum([a[1] for a in dic_nc_vent.get(i) if eval(evalu) ])) - \
                            (sum([date and (cost * a[1]) or a[
                             2] for a in dic_vent.get(i) if eval(evalu)]))

                    if d == 0:
                        cost = qty > 0 and price/qty
                        date = aux2[5]
                        qty_aux = cost and qty
                        price_aux = cost and price
                        aux[i].append((cost, aux2[5], qty))
                        list.append((cost, aux2[5]))
                        aux2[6] and invoice_line_obj.write(cr, uid, aux2[6],
                                                           {'aux_financial': cost*qty,
                                                            'aux_qty': qty},
                                                           context=context)
                        evalu = 'DateTime(a[5]) > DateTime(date) and  \
                                 DateTime(a[5]) <= DateTime(aux2[5])'
                        d = d + 1

                    else:
                        qty = qty + qty_aux
                        price = price + price_aux
                        cost = qty > 0 and price/qty
                        date = aux2[5]
                        qty_aux = cost and qty
                        price_aux = cost and price
                        aux[i].append((cost, aux2[5], qty))
                        list.append((cost, aux2[5]))
                        aux2[6] and invoice_line_obj.write(cr, uid, aux2[6],
                                           {'aux_financial': cost*qty,
                                            'aux_qty': qty}, context=context)

                        evalu = 'DateTime(a[5]) > DateTime(date) and  \
                                DateTime(a[5]) <= DateTime(aux2[5])'

                        d = d + 1

        return aux

    def list_cost(self, cr, uid, cicle, ids_inv, product_id, company_id, context={}):
        '''
        Method that allocates the cost of each sale or note of credit history looking product movement
        @param cicle Dictionary that contains the ID of the product and its line that generated the movement, to know their numbers and only assign the corresponding cost
        @param ids_inv Dictionary consisting of the date of purchase and cost to find its corresponding cost based on their date
        '''
        lista = []
        global invo_cost
        for d in cicle:
            invoice_obj = self.pool.get('account.invoice')
            invoice_line_obj = self.pool.get('account.invoice.line')
            invo_brw = invoice_obj.browse(cr, uid, d[0], context={})
            if invo_brw.type == 'out_refund' and \
               invo_brw.parent_id and invo_brw.parent_id.id in invo_cost:
                lista.append(
                    (d[3], d[3] * invo_cost.get(invo_brw.parent_id.id),
                     invo_cost.get(invo_brw.parent_id.id) or 0, d[4], d[0], d[5]))
                invoice_line_obj.write(cr, uid, d[6],
                                       {'aux_financial': invo_cost.get(
                                        invo_brw.parent_id.id)},
                                       context=context)
                return lista

            if invo_brw.type == 'out_refund' \
                    and invo_brw.parent_id and invo_brw.parent_id.id \
                    not in invo_cost:
                inv_ids = invoice_obj.search(
                    cr, uid, [('invoice_line.product_id', '=', product_id),
                              ('type', '=',
                               'in_invoice'),
                              ('company_id',
                               '=', company_id),
                                ('date_invoice', '<', invo_brw.parent_id.date_invoice)],
                                order='date_invoice')

                inv_ids and [lista.append((d[3],
                                 line.aux_qty and (d[3] * (
                                     line.aux_financial/line.aux_qty)),
                                 line.aux_qty and (
                                     line.aux_financial/line.aux_qty),
                                 d[4], d[0], d[5]))
                 for invo in invoice_obj.browse(cr, uid, [inv_ids[-1]],
                     context=context)
                     for line in invo.invoice_line if line and
                         line.product_id and
                         line.product_id.id == product_id]
                #~ lista and invoice_line_obj.write(cr,uid,d[6],{'aux_financial':lista and lista[2]},context=context)
                return lista

            order_date = ids_inv.keys()
            order_date.sort(reverse=True)
            for date in order_date:
                date1 = DateTime(date)
                date2 = DateTime(d[5])
                if date2 >= date1:
                    cost = ids_inv[date]
                    break
            try:
                lista.append((d[0], d[3], d[
                             3] * cost, cost and cost or 0, d[4], d[5]))
                if invo_brw.type == 'out_invoice':
                    invo_cost.update({d[0]: cost})
            except:
                pass
                #~ raise osv.except_osv(_('Invalid action !'),_("Impossible to calculate the actual cost, because the invoice '%s' \
                                                             #~ does not have a valid date format, to place its cost at \
                                                            #~ the time of sale ")% (invo_brw.id))
        return lista

    def compute_cost(self, cr, uid, ids, context=None, products=False,
                            period=False, fifo=False, lifo=False, date=False):
        '''
        Method to compute coste from porduct invoice from a wizard or called from other method

        @param products IDS list of products to compute cost from invoices
        @param period ids of period to give range to compute cost
        @param ids ids of wizard for method call
        @param fifo booblean to compute cost method fifo
        @param lifo booblean to compute cost method lifo
        @param date field type date to have a point start
        '''
        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')
        invo_line_obj = self.pool.get('account.invoice.line')
        global invo_cost
        cost_obj = self.pool.get('cost.structure')
        product_obj = self.pool.get('product.product')
        wz_brw = products or ids and self.browse(
            cr, uid, ids and ids[0], context=context)
        product_True = products or wz_brw and hasattr(
            wz_brw, 'all') and wz_brw.product
        period_id = products and period or wz_brw and hasattr(
            wz_brw, 'all') and wz_brw.period_id.id
        products = products or wz_brw and hasattr(
            wz_brw, 'all') and wz_brw.product_ids
        if hasattr(wz_brw, 'all') and wz_brw.all:
            products = product_obj.search(cr, uid, [], context=context)
            products = product_obj.browse(cr, uid, products, context=context)
        if products and type(products[0]) is int:
            products = product_obj.browse(cr, uid, products, context=context)
        fifo_true = fifo or hasattr(wz_brw, 'fifo') and wz_brw.fifo
        lifo_true = lifo or hasattr(wz_brw, 'lifo') and wz_brw.lifo
        company_id = self.pool.get('res.users').browse(
            cr, uid, [uid], context=context)[0].company_id.id
        if product_True or hasattr(wz_brw, 'all') and wz_brw.all:
            dic_comp = {}
            dic_vent = {}
            aux_dic_vent = {}
            aux_dic_nc_vent = {}
            dic_nc_com = {}
            dic_nc_vent = {}
            aux_cancel = False
            [(dic_comp.update({i.id: []}), dic_vent.update({i.id: []}),
              dic_nc_com.update({i.id: []}), aux_dic_vent.update({i.id: []}),
              aux_dic_nc_vent.update({i.id: []}), dic_nc_vent.update({i.id: []})) for i in products]

            product_brw = product_obj.browse(
                cr, uid, dic_comp.keys(), context=context)
            date_aux = [i.date_cost_ult for i in product_brw if i.cost_ult > 0]
            date_aux.sort(reverse=True)
            products_date = date_aux and date \
                            and DateTime(date) < DateTime(date_aux[-1]) \
                            and [date] or date_aux \
                            and DateTime(date_aux[-1]) < DateTime(date) \
                            and [date_aux[-1]] or [date]
            products_date.sort(reverse=True)
            #~  Select quantity and cost of product from supplier invoice
            if not context.get('invoice_cancel'):
                [dic_comp[i.id].append((False, i.cost_ult,
                                       (i.cost_ult * i.qty_ult),
                                       i.qty_ult, i.ult_om and
                                       i.ult_om.id, i.date_cost_ult, False, 0, 0))
                    for i in product_brw if i.cost_ult > 0
                    and DateTime(products_date[-1]) >= DateTime(i.date_cost_ult)]

            #~ -------------------------- Search invoices with products selecte
            invo_com_ids = self.search_invoice(cr, uid, ids, dic_comp,
                                               'in_invoice', period_id,
                                               company_id, products_date
                                               and products_date[0]
                                               or False, context=context)

            invo_ven_ids = self.search_invoice(cr, uid, ids, dic_vent,
                                               'out_invoice', period_id,
                                               company_id, products_date
                                               and products_date[0]
                                               or False, context=context)

            invo_nc_com_ids = self.search_invoice(cr, uid, ids, dic_nc_com,
                                                  'in_refund', period_id,
                                                  company_id, products_date
                                                  and products_date[0]
                                                  or False, context=context)

            invo_nc_ven_ids = self.search_invoice(cr, uid, ids, dic_nc_vent,
                                                  'out_refund', period_id,
                                                  company_id, products_date
                                                  and products_date[0]
                                                  or False, context=context)

            #~ -------------  Generate a dict with line values of invoices by p

            dic_comp =  invo_com_ids and \
                        self.update_dictionary(cr, uid, ids, dic_comp,
                                               invo_com_ids, True,
                                               context=context) or dic_comp

            dic_vent = invo_ven_ids and \
                       self.update_dictionary(cr, uid, ids, dic_vent,
                               invo_ven_ids, False, context=context) or dic_vent

            aux_dic_vent = invo_ven_ids and \
                           self.update_dictionary(cr, uid, ids, aux_dic_vent,
                            invo_ven_ids, False, context=context) or aux_dic_vent

            dic_nc_com = invo_nc_com_ids and \
                         self.update_dictionary(cr, uid, ids, dic_nc_com,
                           invo_nc_com_ids, False, context=context) or dic_nc_com

            dic_nc_vent = invo_nc_ven_ids and \
                          self.update_dictionary(cr, uid, ids, dic_nc_vent,
                           invo_nc_ven_ids, True, context=context) or dic_nc_vent

            aux_dic_nc_vent = invo_nc_ven_ids and \
                              self.update_dictionary(cr, uid, ids,
                                      aux_dic_nc_vent, invo_nc_ven_ids,
                                       True, context=context) or aux_dic_nc_vent

            for i in dic_comp:  # Ciclo por cada uno de los productos
                if dic_comp.get(i, False):  # Validar valores en la compras
                    ids_inv = {}
                    if context.get('invoice_cancel'):
                        dic_comp[i] and dic_comp[i][0] \
                                and (dic_comp[i][0][7] - dic_comp[i][0][2]) >= 0 and \
                                dic_comp[i].insert(0, (False,
                                ((dic_comp[i][0][7] - dic_comp[i][0][2]) /
                                ((dic_comp[i][0][8] - dic_comp[i][0][3]) > 0
                                and (
                                    dic_comp[
                                        i][0][8] - dic_comp[i][0][3]) or 1)),
                                 (dic_comp[i][0][7] - dic_comp[i][0][2]),
                                 (dic_comp[i][0][8] - dic_comp[i][0][3]),
                                  dic_comp[i][0][4], dic_comp[i][0][5], False, 0, 0))

                        len(dic_comp[i]) > 1 and  \
                                invo_line_obj.write(
                                    cr, uid, [dic_comp[i][1][6]],
                               {'aux_financial': (dic_comp[i][1][7] - dic_comp[i][1][2]),
                                'aux_qty': (dic_comp[i][1][8] - dic_comp[i][1][3])},
                                 context=context)

                        print "dic_comp[i]", dic_comp[i]
                        len(dic_comp[
                            i]) > 1 and invo_obj.write(
                                cr, uid, [dic_comp[i][1][0]],
                                        {'cancel_check': True}, context=context) or invo_obj.write(cr, uid, [dic_comp[i][0][0]],
                                        {'cancel_check': True}, context=context)
                        len(dic_comp[i]) > 1 and dic_comp[i].pop(
                            1)  # Grabo en la factura que ya fue cancelada

                    dic_comp[i][0][0] is not False and dic_comp[i][0][9] and dic_comp[i][0][7] > 0 and \
                    dic_comp[i].insert(
                        0, (False, (dic_comp[
                            i][0][7]/dic_comp[i][0][8]), dic_comp[i][0][7], dic_comp[i][0][8], dic_comp[i][0][4],
                                          dic_comp[i][0][5], 0.0, 0.0))  # Inserto en la lista de la compra el calculo del costo anterior porque la factura fue cancelada

                    if dic_comp[i][0][0] is not False and not dic_comp[i][0][9] and dic_comp[i][0][7] <= 0:
                        inv_ids = invo_obj.search(
                            cr, uid, [('invoice_line.product_id', '=', i),
                                                    ('type', '=',
                                                     'in_invoice'),
                                                    ('company_id',
                                                     '=', company_id),
                                                    ('date_invoice', '<', dic_comp[i][0][5])],
                                                    order='date_invoice')
                        inv_ids and [dic_comp[i].insert(
                            0, (invo.id, line.aux_qty and (line.aux_financial/line.aux_qty), line.aux_financial,
                                                      line.aux_qty, line.uos_id and
                                                      line.uos_id.id, invo.date_invoice, line.id, line.aux_financial, line.aux_qty, invo.cancel_check))

                for invo in invo_obj.browse(cr, uid, [inv_ids[-1]], context=context) for line in invo.invoice_line if line and
                line.product_id and
                line.product_id.id == i]

                    [ids_inv.update({h[5]:h[1]}) for h in dic_comp[i]]

                    if dic_vent.get(i, False) and len(dic_vent.get(i, [])) > 0:
                        lista = self.list_cost(cr, uid, dic_vent.get(
                            i), ids_inv, i, company_id)
                        dic_vent.update({i: lista})

                    if dic_nc_vent.get(i, False) and len(dic_nc_vent.get(i, [])) > 0:
                        lista = self.list_cost(cr, uid, dic_nc_vent.get(
                            i), ids_inv, i, company_id)
                        dic_nc_vent.update({i: lista})

            invo_cost = {}
            if fifo_true or lifo_true:
                fifo = self.compute_cost_fifo(cr, uid, dic_comp, dic_vent,
                                              dic_nc_com, dic_nc_vent)

            cost_acc = self.compute_actual_cost_purchase(cr, uid, ids,
                                                         dic_comp, dic_vent,
                                                         dic_nc_com, dic_nc_vent)

            for i in dic_comp:
                ids_inv = {}
                [ids_inv.update({h[1]:h[0]}) for h in cost_acc[i]]
                if aux_dic_vent.get(i, False) and len(aux_dic_vent.get(i, [])) > 0:
                        lista = self.list_cost(cr, uid, aux_dic_vent.get(
                            i), ids_inv, i, company_id)
                        aux_dic_vent.update({i: lista})

                if aux_dic_nc_vent.get(i, False) and len(aux_dic_nc_vent.get(i, [])) > 0:
                    lista = self.list_cost(cr, uid, aux_dic_nc_vent.get(
                        i), ids_inv, i, company_id)
                    aux_dic_nc_vent.update({i: lista})

            cost = self.compute_actual_cost(cr, uid, ids, dic_comp,
                                            aux_dic_vent, dic_nc_com,
                                            aux_dic_nc_vent)
        return (cost, cost_acc)

