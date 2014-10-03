# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
# Credits######################################################
#    Coded by: Miguel Delgado <miguel@openerp.com.ve>                      #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: Corporacion AMD                                           #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _

from openerp.addons.decimal_precision import decimal_precision as dp


class stock_production_lot(osv.Model):

    def _serial_identification(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        spl_brw = self.browse(cr, uid, ids, context=context)

        for spl in spl_brw:
            if spl.check_serial and spl.stock_available != 0:
                return False
        return True

    _inherit = 'stock.production.lot'

    _columns = {
        'check_serial': fields.boolean('Check Serial'),
        'ref': fields.char('Internal Reference', size=256,
                           help="""Internal reference number in case it
                                   differs from the manufacturer's
                                   serial number""")
    }

    _constraints = [
        (_serial_identification, _('Check this picking problem with serial'),
         ['Check Serial (check_serial)', 'Stock Available (stock_available)']),
    ]

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ret = []
        res = super(stock_production_lot, self).name_get(
            cr, uid, ids, context=context)
        for i in res:
            ret.append((i[0], i[1].split(' ')[0]))
        return ret


class stock_picking(osv.Model):
    _inherit = "stock.picking"

    def test_serial(self, cr, uid, ids):
        ok = True
        spl_obj = self.pool.get('stock.production.lot')
        for pick in self.browse(cr, uid, ids):
            for move in pick.move_lines:
                if move.product_id.track_serial_incoming and not \
                        move.prodlot_id and pick.type == 'in':
                    raise osv.except_osv(_('Error !'), _(
                        'This product %s should be serialized') %
                        move.product_id.name)
                if move.product_id.track_serial_outgoing and not \
                        move.prodlot_id and pick.type == 'out':
                    raise osv.except_osv(_('Error !'), _(
                        'This product %s should be serialized') %
                        move.product_id.name)

                if move.product_id.track_serial_incoming and \
                    move.product_id.track_serial_outgoing and\
                        pick.type == 'out':
                    spl_ids = spl_obj.search(cr, uid, [(
                        'product_id', '=', move.product_id.id),
                        ('name', '=', move.prodlot_id.name)])
                    if len(spl_ids) < 1:
                        raise osv.except_osv(_('Error !'), _(
                            'This serial %s is not exist') %
                            move.prodlot_id.name)
        return ok
