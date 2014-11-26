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

from openerp.addons.decimal_precision import decimal_precision as dp


class cost_structure(osv.Model):

    _name = 'cost.structure'
    _columns = {
        'description': fields.char('Description', size=128,
            help="Product Description"),
        'type': fields.selection([('v', 'Venta'), ('C', 'Compra')],
            'Type', help="Structure cost type for this Product"),
        'serial': fields.boolean('Serial', help="If Product have a Serial"),
        'date_reg': fields.datetime('Registr Date',
            help="Date of registre creation"),
        'cost_ult': fields.float('Ult Cost',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Actual cost compute for this product"),
        'qty_ult': fields.float('Last Qty',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Last Qty with compute the actual cost"),
        'cost_prom': fields.float('Prom Cost',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Avarage Cost for this product"),
        'cost_suppler': fields.float('Supplier Cost',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Supplier Cost"),
        'cost_ant': fields.float('Ant Cost',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Cost above, I had this product before the new calculation"),
        'qty_ant': fields.float('Ant Qty', 'Qty',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Quantity above, I had this product before the\
                new calculation"),
        'ult_om': fields.many2one('product.uom', 'Last UOM',
            help='Measuring unit of this product obtained in the invoice\
                from cost compute'),
        'prom_om': fields.many2one('product.uom', 'Avg UOM',
            help='Measuring unit average in move all'),
        'ant_om': fields.many2one('product.uom', 'Prev UOM',
            help='Measuring unit above of this product obtained in the\
                invoice from cost compute'),
        'date_cost_ult': fields.datetime('Date',
            help="Date of last change to last cost"),
        'date_ult_om': fields.datetime('Date',
            help="Date of last change to last UOM"),
        'date_cost_prom': fields.datetime('Date',
            help="Date of last change\to avarage cost"),
        'date_prom_om': fields.datetime('Date',
            help="Date of last change to avarage UOM"),
        'date_cost_suppler': fields.datetime('Date',
            help="Date of last change to Supplier cost"),
        'date_ant_om': fields.datetime('Date',
            help="Date of last change to ant UOM"),
        'date_cost_ant': fields.datetime('Date',
            help="Date of last change to ant cost"),
        'date_cost_to_price': fields.datetime('Date',
            help="Date of last change to selection cost"),
        'min_margin': fields.float('% Margin',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Porcent Margin Min"),
        'amount': fields.float('Amount',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Amount"),
        'cost_to_price': fields.selection([
            ('cost_ult', 'Ultimo Costo'),
            ('cost_prom', 'Costo Promedio'),
            ('cost_suppler', 'Costo Proveedor'),
            ('cost_ant', 'Costo Anterior')], 'Type Cost', help="Product type"),
        'method_cost_ids': fields.one2many('method.price', 'cost_structure_id',
            'Cost Method'),
        'company_id': fields.many2one('res.company', 'Company'),

    }
    _rec_name = 'description'

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').
        _company_default_get(cr, uid, 'cost.structure', context=c),
    }


class method_price(osv.Model):

    def default_get(self, cr, uid, fields, context=None):
        '''
        Default_get overwritten the method to select the cost structure and then generate the calculation of the margin from the cost structure

        '''
        if context is None:
            context = {}
        res = super(method_price, self).default_get(
            cr, uid, fields, context=context)
        if context.get('property_cost_structure', False):
            res.update({'reference_cost_structure_id': context.get(
                'property_cost_structure', False)})

        return res

    def name_get(self, cr, uid, ids, context):
        if not len(ids):
            return []
        reads = self.browse(cr, uid, ids, context)
        res = []
        for r in reads:
            name = 'Price %d %s' % (r.sequence, repr(round(r.unit_price, 2)))
            res.append((r.id, name))
        return res

    _name = 'method.price'
    _columns = {
        'cost_structure_id': fields.many2one('cost.structure',
            'Cost Structure'),
        'reference_cost_structure_id': fields.many2one('cost.structure',
            'Cost Structure2'),
        'sequence': fields.integer('Sequence',
            help="Sequence that determines the type of sales\
                price, dependediendo customer type (Type 1, Type 2 ...)"),
        'unit_price': fields.float('Price Unit',
            digits_compute=dp.get_precision('Sale Price'),
            help="Price Unit to sale"),
        'date': fields.date('Creation date'),
        'date_prom_begin': fields.date('Date Prom', help="Compute Date Prom"),
        'date_prom_end': fields.date('Date End',
            help="Compute Date Prom with end"),
        'margin': fields.float('Margin',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Price Margin"),
        'arancel': fields.float('% Arancel',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Porcent Arancel"),
        'min_margin': fields.float('% Margin',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Porcent Margin Min"),
        'price_referen': fields.float('Price Reference',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Price Reference"),
        'margin_reference': fields.float('Margin',
            digits_compute=dp.get_precision('Cost Structure'),
            help="Price Margin"),
        'company_id': fields.many2one('res.company', 'Company'),
        'default_cost': fields.boolean('Default Cost to report',
            help='This field define cost by default to report cost'),
    }

    _rec_name = 'unit_price'

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company').
        _company_default_get(cr, uid, 'cost.structure', context=c),

    }
    _order = 'sequence'

    def onchange_marginprice(self, cr, uid, ids, unit_price, margin_reference,
                            cost_structure_id, context=None):
        '''
        Compute margin of gain to cost return price or percent gain
        '''
        if context is None:
            context = {}
        res = {'value': {}}
        cost_obj = self.pool.get('cost.structure')
        if cost_structure_id:
            cost_brw = cost_obj.browse(
                cr, uid, cost_structure_id, context=context)
            margin_reference and cost_brw.cost_ult and\
                res['value'].update({'unit_price': (
                    ((float(margin_reference) / 100) * cost_brw.cost_ult) +
                    cost_brw.cost_ult)})
            unit_price and cost_brw.cost_ult\
                and res['value'].update({'margin_reference':
                    ((unit_price - cost_brw.cost_ult) / cost_brw.cost_ult) * 100})
        return res
