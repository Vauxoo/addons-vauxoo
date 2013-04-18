# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Vauxoo (<http://www.vauxoo.com>). All Rights Reserved
#    hbto@vauxoo.com / humbertoarocha@gmail.com
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

from osv import osv
from osv import fields
from tools.translate import _
import decimal_precision as dp


class baremo_book(osv.osv):
    def _get_rate(self, cr, uid, rate_brw, rate, context=None):
        if context is None:
            context = {}
        if rate >= rate_brw.porc_rate:
            return rate_brw.porc_rate, rate_brw.porc_com, True
        return 0.0, 0.0, False

    def _calc_comm(self, cr, uid, ids, bid, rate=0.0, timespan=0.0, context=None):
        '''Calculates the commission given these parameters
        '''
        print 'bid', bid
        spn_obj = self.pool.get('baremo.span')
        bar_rat_obj = self.pool.get('baremo.rate')
        if context is None:
            context = {}

        is_discount = context.get('is_discount', False)

        res = {}
        spn_ids = spn_obj.search(cr, uid, [('bar_id', '=', 1)])

        if not spn_ids:
            raise osv.except_osv(_('Be Aware !'), _('There are no time spans  established for the\nBareme: %s\nbeing used.\nPlease Fill this one before using it' % (
                self.browse(cr, uid, bid, context).name)))

        timespan_number = 0.0
        rate_number = 0.0
        rate_comm = 0.0

        for spn_brw in spn_obj.browse(cr, uid, spn_ids):
        # Se busca que el baremo tenga un rango que cubra a timespan
            if timespan <= spn_brw.number:
                timespan_number = spn_brw.number
                rat_ids = bar_rat_obj.search(cr, uid, [
                                             ('span_id', '=', spn_brw.id)])

                if not rat_ids:
                    raise osv.except_osv(_('Be Aware !'),
                                         _('''There are no rates defined for the\n
                        Timespan: %s\n
                        in Bareme: %s\n
                        being used.\n
                        Please Fill this one before using it
                        ''' % (spn_brw.bar_id.name.upper(), spn_brw.name)))
                if not is_discount:
                    rat_ids = rat_ids[::-1]

                for rate_brw in bar_rat_obj.browse(cr, uid, rat_ids):
                    # Se busca que el baremo tenga un rango para el valor de
                    # descuento en producto
                    rate_number, rate_comm, return_break = self._get_rate(
                        cr, uid, rate_brw, rate, context)
                    if return_break:
                        break
                break

        res = {
            'timespan': timespan_number,
            'rate_number': rate_number,
            'rate_comm': rate_comm,
        }
        return res

    def _calc_commission(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        rate = context.get('comm_rate', 0.0)
        timespan = context.get('comm_timespan', 0.0)
        print 'rate', rate
        return self._calc_comm(cr, uid, id, rate, timespan, context)

    _name = 'baremo.book'
    _description = 'Baremo Book: Object that ties the baremo'
    _columns = {
        'name': fields.char('Name', size=254, required=True, readonly=False),
        'notes': fields.text('Notes', required=True, readonly=False),
        'bar_ids': fields.one2many('baremo.span', 'bar_id', 'Emission Days', required=False),
    }
    _defaults = {
        'name': lambda *a: _(
            ''' You must write a note referring the baremo,
This note will be used in the commission report,
e.g., Negative Discounts represent overpricing
made on products to compensate on overdue payments
because of the customer.
'''),
    }
baremo_book()


class baremo(osv.osv):
    """
    OpenERP Model : baremo
    """

    _name = 'baremo.span'
    _order = "number asc"

    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=False, help="Name to the Due Term"),
        'number': fields.integer('Days', help="Days since invoice date", required=True),
        'rate_ids': fields.one2many('baremo.rate', 'span_id', 'Commission by Disc.', required=False, help="Commission x Disc. x Day"),
        'bar_id': fields.many2one('baremo.book', 'Bareme'),
    }
    _defaults = {
        'name': lambda *a: None,
    }
baremo()


class baremo_rate(osv.osv):
    """
    OpenERP Model : baremo_rate
    """

    _name = 'baremo.rate'
    _order = "porc_rate asc"
    _columns = {
        'name': fields.char('name', size=64, required=False, readonly=False,),
        'porc_rate': fields.float('% Disc.', digits_compute=dp.get_precision('Commission'), help="% Disc. by product", required=True),
        'porc_com': fields.float('% Com.', digits_compute=dp.get_precision('Commission'), help="% Comission @ % Disc.", required=True),
        'span_id': fields.many2one('baremo.span', 'baremo.span'),
    }
    _defaults = {
        'name': lambda *a: None,
    }
baremo_rate()
