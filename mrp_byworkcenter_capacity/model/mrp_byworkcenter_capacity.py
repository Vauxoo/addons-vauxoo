#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral      <kathy@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools

def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

class mrp_workcenter(osv.Model):

    _inherit = 'mrp.workcenter'
    _columns = {
        'product_capacity_ids': fields.one2many(
            'mrp.workcenter.product.capacity',
            'workcenter_id',
            _('Products Maxime Capacity'),
            help=_('Workcenter capacities by product')),
    }

class mrp_workcenter_product_capacity(osv.Model):

    _name = 'mrp.workcenter.product.capacity'
    _description = 'Workcenter Product Capacity'

    #~ TODO: this method for constraint is not working like it supposed.
    def _check_uniqueness(self, cr, uid, ids, context=None):
        """
        Check if a product capacity is already defined in a workcenter
        @return True if there is unique, False if already exist
        """
        context = context or {}
        wc_obj = self.pool.get('mrp.workcenter')
        product_obj = self.pool.get('product.product')
        wcpc_brw = self.browse(cr, uid, ids, context=context)[0]

        product_capacity = self.search(
            cr, uid, [('product_id', '=', wcpc_brw.product_id.id),
            ('workcenter_id', '=', wcpc_brw.workcenter_id.id)],
            context=context)

        #~ print '\n'*4
        #~ print '_check_uniqueness()'
        #~ print 'wcpc_brw', wcpc_brw
        #~ print 'product_capacity', product_capacity
        #~ print '\n'*4

        return product_capacity and True or False 

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            _('WorkCenter'),
            required=True,
            help=_('Work Center')),
        'operation_id': fields.many2one(
            'mrp.routing.workcenter',
            _('Operation'),
            help=_('Operation')),
        'product_id': fields.many2one(
            'product.product',
            _('Product'),
            required=True,
            help=_('Product')),
        'qty': fields.float(
            _('Capacity'),
            required=True,
            help=_('Quantity')),
        'uom_id': fields.many2one(
            'product.uom',
            _('Unit of Measure'),
            required=True,
            help=_('Unit of Measure')),
    }

    _constraints = {
        (_check_uniqueness,
         _('Error! There is already defined capacity for this product in the '
           'current workcenter'),
         'product_id')
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This method loads the workcenter_id extracted from the
        workcenter operation wizard and added to the current product capacity
        line. It garantee that the wor center is set.   
        """
        context = context or {}
        res = super(mrp_workcenter_product_capacity, self).default_get(
            cr, uid, fields, context)

        res['workcenter_id'] = context.get('workcenter_id', False)
        return res


class mrp_routing_workcenter(osv.Model):

    _inherit = 'mrp.routing.workcenter'
    _columns = {
        'product_ids': fields.one2many(
            'mrp.workcenter.product.capacity',
            'operation_id',
            _('Products Needed'),
            help=_('Products needed to the operation')),
    }

class mrp_production(osv.Model):

    _inherit = 'mrp.production'
    _columns = {
        'swo_ids': fields.one2many(
            'mrp.scheduled.workorders', 'production_id',
            string=_('Scheduled Work Orders'),
            help=_('Scheduled Work Orders'),
        )
    }

    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """
        Overwrite method to take into a count the workcenter capacities to
        split the manufacturing order workorders in batch. This batch is based
        on raw materials capacity per workcenter.  
        """
        context = context or {}
        properties = properties or []
        wo_obj = self.pool.get('mrp.production.workcenter.line')
        swo_obj = self.pool.get('mrp.scheduled.workorders')

        # normal process of confirm
        res = super(mrp_production, self).action_compute(
            cr, uid, ids, properties=properties, context=context)

        # delete work orders and create scheduled work orders
        for production in self.browse(cr, uid, ids, context=context):

            # delete created work orders and old scheduled work orders
            wo_models = [wo_obj, swo_obj]
            for my_wo_obj in wo_models:
                wo_ids = my_wo_obj.search(
                    cr, uid, [('production_id', '=', production.id)],
                    context=context)
                my_wo_obj.unlink(cr, uid, wo_ids, context=context)

            #~ create scheduled work orders
            swo_dict_list = self.create_swo_dict(
                cr, uid, [production.id], context=context)
            swo_dict_list and self.write(
                cr, uid, [production.id], {'swo_ids':
                map(lambda x: (0, 0, x), swo_dict_list) }, context=context)

        return res

    #~ TODO: development in progress
    def get_wc_capacity(self, cr, uid, ids, rounting_id, context=None):
        """
        It calculate every workcenters capacity in the rounting_id.
        @return the rorunting capacity (the minimun workcenter max capacity)
        """
        context = context or {}
        routing_obj = self.pool.get('mrp.routing')
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        routing_brw = routing_obj.browse(cr, uid, rounting_id, context=context)
        production = self.browse(cr, uid, ids, context=context)

        # Manufacturing Order Raw Material Needed
        print '\n'
        print '...Manufacturing Order Raw Material Needed'
        production_rm = dict()
        product_qty = production.product_qty
        for bom in production.bom_id.bom_lines:
            production_rm[bom.product_id.id] = \
                {'name': bom.product_id.name, 'qty': bom.product_qty, 'uom': bom.product_uom.id}
        #~ TODO: this production_rm['qty'] * product_qty

        # print debug data
        import pprint
        print 'product_qty', product_qty
        print 'production_rm'
        pprint.pprint(production_rm)

        # Work Centers Product Capacity
        print '...Work Centers: Product Capacity and Operations'
        wc_brws = [operation.workcenter_id for operation in routing_brw.workcenter_lines]
        wc_brws = list(set(wc_brws))
        wc_dict = {}.fromkeys(wc.id for wc in wc_brws)
        for wc in wc_brws:
            wc_dict[wc.id] = {'name': wc.name, 'capacity': {}, 'operations': [], 'bottleneck': []}
            for product_id in production_rm.keys():
                wc_dict[wc.id]['capacity'].update({product_id: False})
        for wc in wc_brws:
            for pc_brw in wc.product_capacity_ids:
                wc_dict[wc.id]['capacity'].update({
                    pc_brw.product_id.id:
                        uom_obj._compute_qty(cr, uid, pc_brw.uom_id.id, pc_brw.qty,
                                             production_rm[pc_brw.product_id.id]['uom'])
                    })
        wc_operation = [(operation.id, operation.workcenter_id.id)
                        for operation in routing_brw.workcenter_lines]

        for item in wc_operation:
            wc_dict[item[1]]['operations'] += [item[0]]

        # Routing Operations Raw Material Needed
        print '...Routing Operations Raw Material Needed'
        wc_ope_product_qty = dict()
        for wc_ope in routing_brw.workcenter_lines:
            wc_ope_product_qty[wc_ope.id] = dict()

        for wc_ope in routing_brw.workcenter_lines:
            for product in wc_ope.product_ids:
                wc_ope_product_qty[wc_ope.id].update(
                    {product.product_id.id:
                        uom_obj._compute_qty(cr, uid, product.uom_id.id, product.qty,
                                             production_rm[product.product_id.id]['uom'])})

        print 'wc_ope_product_qty', wc_ope_product_qty

        # Checking that operations product quantites are less or equal to the manufacturing order
        # product quantities given.

        routing_qty_error = str()
        routing_qty = {}.fromkeys(production_rm.keys(), 0.0)

        for operation in wc_ope_product_qty.keys():
            for product_id in wc_ope_product_qty[operation].keys():
                routing_qty[product_id] += wc_ope_product_qty[operation][product_id]

        print 'routing_qty', routing_qty

        for product_id in routing_qty.keys():
            if routing_qty[product_id] > production_rm[product_id]['qty']:
                routing_qty_error += '\n - It Needs at least %s %s of %s and only %s %s is given.' % (
                    routing_qty[product_id],
                    uom_obj.browse(cr, uid, production_rm[product_id]['uom'], context=context).name,
                    product_obj.browse(cr, uid, product_id, context=context).name,
                    production_rm[product_id]['qty'],
                    uom_obj.browse(cr, uid, production_rm[product_id]['uom'], context=context).name,
                )

        if routing_qty_error:
            raise osv.except_osv(
                _('Error!'),
                _('There is a problem with the definition of the routing quantities.'
                  ' The operations requires more product quantity that the one is given in the'
                  ' manufacturing order:\n' + str(routing_qty_error)))

        # Cheking the Work Center Capacity with the Work Center Operation quantities.
        print "...Cheking the Work Center Capacity with the Work Center Operation quantities"
        print "(wc, operation, product_id, capacty, qty)"
        for wc_id in wc_dict:
            for operation_id in wc_dict[wc_id]['operations']:
                for product_id in wc_ope_product_qty[operation_id]:
                    print (wc_id, operation_id, product_id,
                           wc_dict[wc_id]['capacity'][product_id],
                           wc_ope_product_qty[operation_id][product_id])

                #~ for (product_id, product_qty) in wc_ope_product_qty[operation_id].iteritems():
                    #~ print (wc_id, operation_id, product_id, product_qty, wc_dict[wc]['capacity'][product_id])
#~ 
                    #~ print '(capacity, qty)',  wc_dict[wc]['capacity'][product_id], product_qty
                    #~ if wc_dict[wc]['capacity'][product_id] and \
                       #~ wc_dict[wc]['capacity'][product_id] < product_qty:
                            #~ print  'soy menor'
                            #~ wc_dict[wc]['bottleneck'] = (product_id, product_qty)

        print '\n'
        print '\n'
        print '\n'
        print 'wc_dict'
        pprint.pprint(wc_dict)


        print '\n'*3
        raise osv.except_osv(
            _('Warining'),
            _('This functionality is on development.'))

        wc_capacity = {}
        wc_capacity[operation.workcenter_id] = []

        #~ 'move_lines': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Products to Consume',
            #~ domain=[('state','not in', ('done', 'cancel'))], readonly=True, states={'draft':[('readonly',False)]}),
#~ 

        #~ import pprint
        #~ print '\n'*3
        #~ print 'get_wc_capacity', get_wc_capacity
        #~ print 'wc_capacity'
        #~ pprint.pprint(wc_capacity)
        #~ print '\n'*3

        return  0

    def create_swo_dict(self, cr, uid, ids, context=None):
        """
        Generate a dictionary of scheduled work orders to create when
        confirming a manufacturing order, take in count the operations of the
        rounting plus the the capacity of the work centers.
        @ return: List of dictionaries containing scheduled work orders to
        create.
        """

        #~ import pprint
        #~ print "\n"*3, 'create_swo_dict()'

        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        routing_obj = self.pool.get('mrp.routing')
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        result = []

        for production in self.browse(cr, uid, ids, context=context):

            #~ calculate factor
            factor = uom_obj._compute_qty(
                cr, uid, production.product_uom.id, production.product_qty,
                production.bom_id.product_uom.id)
            factor = factor / (production.bom_id.product_efficiency or 1.0)
            factor = rounding(factor, production.bom_id.product_rounding)
            if factor < production.bom_id.product_rounding:
                factor = production.bom_id.product_rounding
            factor = factor / production.bom_id.product_qty
            level = 0

            routing_brw = production.routing_id or \
                production.bom_id.routing_id or False

            if not routing_brw:
                return result

            batch_mode = production.company_id.batch_type

            # for every routing operation
            for wc_op in routing_brw.workcenter_lines:
                wc_brw = wc_op.workcenter_id

                if batch_mode == 'max_cost':
                    wc_capacity = wc_brw.capacity_per_cycle
                elif batch_mode == 'bottleneck':
                    wc_capacity = self.get_wc_capacity(
                        cr, uid, production.id, routing_brw.id,
                        context=context)
                    
                product_qty = production.product_qty
                d, m = divmod(factor, wc_capacity)
                mult = int(d + (m and 1.0 or 0.0))
                cycle = wc_op.cycle_nbr

                #~ print "\n"*2
                #~ print "factor", factor, "wc_capacity", wc_capacity
                #~ print '(d, m)', (d, m)
                #~ print 'mult', mult
                #~ print 'cycle', cycle

                process_qty = 0
                for new_swo in xrange(mult):
                    level += 10
                    qty = product_qty - process_qty > wc_capacity \
                          and wc_capacity or product_qty - process_qty
                    process_qty += qty

                    #~ print '(process_qty, qty)', (process_qty, qty)

                    result.append({
                        'name':
                            tools.ustr(wc_op.name) + ' - '  +
                            tools.ustr(production.bom_id.product_id.name) +
                            ' (%s/%s)' % (new_swo+1, mult),
                        'workcenter_id': wc_brw.id,
                        'sequence': level+(wc_op.sequence or 0),
                        'qty': qty,
                        'cycle': cycle,
                        'hour':
                            float(wc_op.hour_nbr*wc_capacity +
                            ((wc_brw.time_start or 0.0) +
                             (wc_brw.time_stop or 0.0) +
                             cycle * (wc_brw.time_cycle or 0.0)) *
                            (wc_brw.time_efficiency or 1.0)),
                        # TODO check is tis hours are well calculated with an
                        # test case
                        # NOTE: the field wc_brw.time_efficiency it does not
                        # exist in the model. why this???
                    })

                #~ print 'result'
                #~ pprint.pprint(result)

        return result


class mrp_scheduled_workorders(osv.Model):

    _name = 'mrp.scheduled.workorders'
    _inherit = 'mrp.production.workcenter.line'
    _description= _('Sheluded Work Order')

    """
    This is a prototype inheritance of work orders model
    """
