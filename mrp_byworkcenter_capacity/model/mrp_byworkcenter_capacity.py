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


class stock_move(osv.Model):
    _inherit = 'stock.move'

    def write(self, cr, uid, ids, values, context=None):
        """
        Overwrite the write() method to update the values dictionary with the
        prodlot_id when creating stock move through the confirmation of the
        manufacturing order. 
        """
        #~ TODO: check the def _make_production_produce_line(self, cr, uid,
        #~ production, context=None) in addons/mrp/mrp.py
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        #~ When confirming a manufacturing order a set of internal move to
        #~ productd to produce are made. this moves need to have a prodlot id
        #~ too. that corresponding to the one given in the production order.
        #~ When move.write() have into the values 'production_id' it means that
        #~ this movement its have been associated to an manufacturing order so
        #~ there is how we go to add that value to the move line.
        if values.get('production_id', False):
            prodlot_id = production_obj.browse(
                cr, uid, values['production_id'],
                context=context).prodlot_id.id
            values.update({'prodlot_id': prodlot_id})
        return super(stock_move, self).write(
            cr, uid, ids, values, context=context)


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

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            _('WorkCenter'),
            required=True,
            help=_('Work Center')),
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

    _sql_constraints = [
        ('operation_prodct_uniq', 'unique (workcenter_id,product_id)',
         'Error! There is already defined capacity for this product in the '
         'current workcenter.')
    ]


class mrp_workcenter_operation_product_quantity(osv.Model):

    _name = 'mrp.workcenter.operation.product.quantity'
    _description = 'Work Center Operation Product Quantity'

    _columns = {
        'operation_id': fields.many2one(
            'mrp.routing.workcenter',
            _('Operation'),
            required=True,
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

    _sql_constraints = [
        ('operation_prodct_uniq', 'unique (operation_id,product_id)',
         'Error! There is already defined capacity for this product in the '
         'current operation.')
    ]


class mrp_routing_workcenter(osv.Model):

    _inherit = 'mrp.routing.workcenter'
    _columns = {
        'product_ids': fields.one2many(
            'mrp.workcenter.operation.product.quantity',
            'operation_id',
            _('Products Needed'),
            help=_('Products needed to the operation')),
    }


class mrp_production(osv.Model):

    _inherit = 'mrp.production'
    _columns = {
        'wo_lot_ids': fields.one2many(
            'mrp.workorder.lot', 'production_id',
            string=_('Work Orders Lots'),
            help=_('Work Orders Lots.')),
        'prodlot_id': fields.many2one(
            'stock.production.lot',
            _('Serial Number'),
            help=_('Production Serial Number (Lot)\n This is the Serial Number'
                   ' that will receives the stock move from Virtual Production'
                   ' Location to the Destination Physical Stock Location.'
                   ' This is a formalism to use the Track Manufacturing Lots'
                   ' funcionality that requires that every stock move for your'
                   ' manufacturing product need to have a Serial Number'
                   ' associated')),
    }

    def write(self, cr, uid, ids, values, context=None, update=False):
        """
        Overwrite the write() method to check first if the serial number is
        or is not a required field taking into account the manufacturing
        order product configuration (Lots and Tracks Options).
        """
        context = context or {}
        product_obj = self.pool.get('product.product')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        fields_to_review = ['product_id', 'prodlot_id']
        error_msg = str()

        if isinstance(values, (dict,)):
            for production_brw in self.browse(cr, uid, ids, context=context):
                field_data = {}.fromkeys(fields_to_review)
                for field in fields_to_review:
                    field_data.update({field:
                        values.get(field, 'undefined') == 'undefined' 
                        and getattr(production_brw, field).id
                        or values.get(field)})
                product_brw = field_data['product_id'] and product_obj.browse(
                    cr, uid, field_data['product_id'], context=context)
                if (product_brw.track_production
                    and not field_data['prodlot_id']):
                    error_msg += _('You have Activated the Track Manufacturing'
                                   ' Lots in the product of your manufacturing'
                                   ' order so its required that you set a'
                                   ' Serial number to manage internal moves'
                                   ' for this product in the production'
                                   ' process. Or, you can uncheck the Track'
                                   ' Manufacturing Lost option at the'
                                   ' Inventory tab in the Product Form.\n')
                #~ TODO: guess what do the product_obj track_incoming and
                #~ track_outgoing fields to add the exceptions necesarry to be
                #~ manage here.
        else:
            error_msg += _('Programing Error. Cants process the write from'
                           ' of manufacturing order from another model.')

        if error_msg:
            raise osv.except_osv(_('Invalid Procedure'), error_msg)

        res = super(mrp_production, self).write(
            cr, uid, ids, values, context=context)
        return res
                
    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """
        Overwrite action_compute() method to delete regular work orders
        creation and improve the process by taking into account the workcenter
        capacities to split the manufacturing order work orders in lots.
        (Workcenter capacities are mesuare in process capacity - per cycle - or
        by income products max capacity - manufacturing order raw material).
        """
        context = context or {}
        properties = properties or []
        wo_obj = self.pool.get('mrp.production.workcenter.line')

        # normal process of confirm
        res = super(mrp_production, self).action_compute(
            cr, uid, ids, properties=properties, context=context)

        for production in self.browse(cr, uid, ids, context=context):

            # delete the just created regular wo and older wo.
            wo_ids = wo_obj.search(
                cr, uid, [('production_id', '=', production.id)],
                context=context)
            wo_obj.unlink(cr, uid, wo_ids, context=context)

            #~ create work orders by wc capacity and work order lots
            wo_dict_list = self.create_wo_dict(
                cr, uid, [production.id], context=context)
            wo_dict_list and self.write(
                cr, uid, [production.id],
                {'workcenter_lines': map(lambda x: (0, 0, x), wo_dict_list)},
                context=context)

        return res

    #~ TODO: development in progress
    def get_wc_capacity(self, cr, uid, ids, rounting_id, context=None):
        """
        It calculate every workcenters capacity in the rounting_id.
        @param rounting_id: routing id.
        @return a tupla with the the rorunting capacity like (split_nbr,
        product_qty, product_id)]
        """
        context = context or {}
        routing_obj = self.pool.get('mrp.routing')
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        routing_brw = routing_obj.browse(cr, uid, rounting_id, context=context)
        production = self.browse(cr, uid, ids, context=context)

        #~ print _('\n...Extracting Manufacturing Order Raw Material Needed'
                   #~ ' Information')
        production_rm = dict()
        for bom in production.bom_id.bom_lines:
            production_rm[bom.product_id.id] = \
                {'name': bom.product_id.name,
                 'qty': bom.product_qty * production.product_qty,
                 'uom': bom.product_uom.id}

        #~ print 'production_rm'
        #~ pprint.pprint(production_rm)

        #~ print _('...Extractiong Work Centers Information: Product Capacity'
                #~ ' and Operations')
        wc_brws = [operation.workcenter_id
                   for operation in routing_brw.workcenter_lines]
        wc_brws = list(set(wc_brws))
        wc_dict = {}.fromkeys(wc.id for wc in wc_brws)
        for wc in wc_brws:
            wc_dict[wc.id] = {
                'name': wc.name, 'capacity': {},
                'operations': [], 'bottleneck': []}
            for product_id in production_rm.keys():
                wc_dict[wc.id]['capacity'].update({product_id: False})
        for wc in wc_brws:
            pc_lines = [product_line
                        for product_line in wc.product_capacity_ids
                        if product_line.product_id.id in production_rm.keys()]
            for pc_line in pc_lines:
                wc_dict[wc.id]['capacity'].update({
                    pc_line.product_id.id: uom_obj._compute_qty(
                        cr, uid, pc_line.uom_id.id, pc_line.qty,
                        production_rm[pc_line.product_id.id]['uom'])
                    })
        wc_operation = [(operation.id, operation.workcenter_id.id)
                        for operation in routing_brw.workcenter_lines]

        for item in wc_operation:
            wc_dict[item[1]]['operations'] += [item[0]]

        #~ print 'wc_dict'
        #~ pprint.pprint(wc_dict)

        #~ print _('...Extracting Routing Operations Products Quantity Needed')
        wc_ope_product_qty = dict()
        for wc_ope in routing_brw.workcenter_lines:
            wc_ope_product_qty[wc_ope.id] = dict()

        for wc_ope in routing_brw.workcenter_lines:
            for product in wc_ope.product_ids:
                wc_ope_product_qty[wc_ope.id].update(
                    {product.product_id.id:
                        uom_obj._compute_qty(
                            cr, uid, product.uom_id.id,
                            product.qty * production.product_qty,
                            production_rm[product.product_id.id]['uom'])})

        #~ print 'wc_ope_product_qty', wc_ope_product_qty

        #~ print _('...Checking that Operation Quantities are <= to '
                #~ 'Manufacturing Order Quantities')
        routing_qty_error = str()
        routing_qty = {}.fromkeys(production_rm.keys(), 0.0)

        for operation in wc_ope_product_qty.keys():
            for product_id in wc_ope_product_qty[operation].keys():
                routing_qty[product_id] += \
                    wc_ope_product_qty[operation][product_id]
        #~ TODO: Ask rotuing qty will be the max of
        #~ wc_ope_product_qty[operation][product_id] or the summatory of all?

        #~ print 'routing_qty', routing_qty

        #~ for product_id in routing_qty.keys():
            #~ if routing_qty[product_id] > production_rm[product_id]['qty']:
                #~ routing_qty_error += \
                    #~ _('\n - It Needs at least %s %s of %s and only %s %s is'
                      #~ ' given.') % (
                        #~ routing_qty[product_id],
                        #~ uom_obj.browse(
                            #~ cr, uid, production_rm[product_id]['uom'],
                            #~ context=context).name,
                        #~ product_obj.browse(
                            #~ cr, uid, product_id, context=context).name,
                        #~ production_rm[product_id]['qty'],
                        #~ uom_obj.browse(
                            #~ cr, uid, production_rm[product_id]['uom'],
                            #~ context=context).name,
                    #~ )
        if routing_qty_error:
            raise osv.except_osv(
                _('Error!'),
                _('There is a problem with the definition of the routing'
                  ' quantities. The operations requires more product quantity'
                  ' that the one is given in themanufacturing order:\n'
                  + str(routing_qty_error)))

        #~ print _('...Cheking the Work Center Capacity with the Work Center'
                #~ ' Operation quantities (Calculate Bottleneck)')
        #~ print "(wc, operation, product_id, capacty, qty)"
        for wc_id in wc_dict:
            for op_id in wc_dict[wc_id]['operations']:
                for (product_id, product_qty) in \
                wc_ope_product_qty[op_id].iteritems():
                    #~ print (wc_id, op_id, product_id,
                           #~ wc_dict[wc_id]['capacity'][product_id],
                           #~ product_qty)
                    if wc_dict[wc_id]['capacity'][product_id] and \
                       wc_dict[wc_id]['capacity'][product_id] < product_qty:
                            div, mod = \
                                divmod(product_qty,
                                       wc_dict[wc_id]['capacity'][product_id])
                            split_size = int(div + (mod and 1 or 0))
                            wc_dict[wc_id]['bottleneck'] += \
                                [(split_size,
                                  wc_dict[wc_id]['capacity'][product_id],
                                  product_id)]

        #~ print 'wc_dict'
        #~ pprint.pprint(wc_dict)

        bottleneck_list = list()
        for wc_id in wc_dict:
            bottleneck_list.extend(wc_dict[wc_id]['bottleneck'])
        bottleneck_list.sort(reverse=True)
        #~ print 'bottleneck_list', bottleneck_list

        return bottleneck_list and bottleneck_list[0] or False

    def create_wo_dict(self, cr, uid, ids, context=None):
        """
        Generate a dictionary of work orders to create when confirming a
        manufacturing order, taking into account the operations of the
        rounting plus the the capacity of the work centers.
        @ return: List of dictionaries containing work orders to
        create.
        """

        #~ import pprint
        #~ print "\n"*3, 'create_wo_dict()'

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
            lot_list = False

            # for every routing operation
            for wc_op in routing_brw.workcenter_lines:
                wc_brw = wc_op.workcenter_id
                cycle = wc_op.cycle_nbr
                product_qty = production.product_qty

                if batch_mode == 'max_cost':
                    wc_capacity = wc_brw.capacity_per_cycle
                    d, m = divmod(factor, wc_capacity)
                    mult = int(d + (m and 1.0 or 0.0))
                elif batch_mode == 'bottleneck':
                    mult, wc_capacity, critic_product_id = \
                        self.get_wc_capacity(
                            cr, uid, production.id, routing_brw.id,
                            context=context) or (1, product_qty, False)
                    d, m = divmod(factor, wc_capacity)

                if critic_product_id:
                    critic_product_income_qty = \
                        [rm_bom.product_qty * product_qty
                         for rm_bom in production.bom_id.bom_lines
                         if rm_bom.product_id.id == critic_product_id]
                    critic_product_income_qty = critic_product_income_qty[0]
                    #~ TODO: need to manage here product_uom too?
                else:
                    critic_product_income_qty = 100.0

                percentage = {}.fromkeys(m and ['d', 'm'] or ['d'])
                percentage['d'] = \
                    (wc_capacity/critic_product_income_qty) * 100.0
                percentage['m'] = m and (m/critic_product_income_qty) * 100.0 \
                    or percentage['d']

                # create wo lots
                lot_list = lot_list and lot_list or \
                    self.create_wo_lot(cr, uid, ids, mult, percentage,
                                       context=context)

                process_qty = 0
                for new_wo in xrange(mult):
                    level += 10
                    qty = product_qty - process_qty > wc_capacity \
                        and wc_capacity or product_qty - process_qty
                    process_qty += qty

                    #~ print '(process_qty, qty)', (process_qty, qty)

                    result.append({
                        'name':
                        tools.ustr(wc_op.name) + ' - ' +
                        tools.ustr(production.bom_id.product_id.name) +
                        ' (%s/%s)' % (new_wo+1, mult),
                        'workcenter_id': wc_brw.id,
                        'sequence': level+(wc_op.sequence or 0),
                        'wo_lot_id': lot_list[new_wo],
                        'qty': qty,
                        'cycle': cycle,
                        'hour': self.get_wo_hour(
                            cr, uid,
                            op_hours=wc_op.hour_nbr,
                            op_cycle=cycle,
                            wc_capacity=wc_capacity,
                            wc_time_start=wc_brw.time_start,
                            wc_time_stop=wc_brw.time_stop,
                            wc_time_cycle=wc_brw.time_cycle,
                            wc_time_efficiency=wc_brw.time_efficiency,
                            context=context),
                    })

                #~ print 'result'
                #~ pprint.pprint(result)

        return result

    #~ TODO: This calculation needs to be check. I think that is retorning a
    #~ incorrect value
    def get_wo_hour(self, cr, uid, op_hours, op_cycle, wc_capacity,
                     wc_time_start=0.0, wc_time_stop=0.0, wc_time_cycle=0.0,
                     wc_time_efficiency=1.0, context=None):
        """
        @param op_hours: Operation number of hours
        @param op_cycle: Operation number of cycle repetition
        @param wc_capacity: work center capacity
        @param wc_time_start: work center time star
        @param wc_time_stop: work center time stop
        @param wc_time_cycle: work center time in hour per cycle
        @return the number of hours need to complete the work order job.
        """
        res = float(
            op_hours * wc_capacity +
            (wc_time_start + wc_time_stop + op_cycle * wc_time_cycle)
            * (wc_time_efficiency)
        )
        return res

    def create_wo_lot(self, cr, uid, ids, mult, percentage, context=None):
        """
        Create the records for the wo lots. Only the records, in a posterior
        process will add the wo corresponding to every lot.
        @param mult: number of lots to produce.
        @return: a list of created lot ids
        """
        context = context or {}
        res = []
        wo_lot_obj = self.pool.get('mrp.workorder.lot')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for production in self.browse(cr, uid, ids, context=context):
            for item in range(mult):
                values = {
                    'name': '%s/WOLOT/%05i' % (production.name, item+1, ),
                    'number': '%05i' % (item+1,),
                    'production_id': production.id,
                    'percentage': (item != mult-1) and percentage['d']
                    or percentage['m']
                }
                res += [wo_lot_obj.create(cr, uid, values, context=context)]
        return res

    def check_first_wol_validity(self, cr, uid, wol_id, context=None):
        """
        Check work order lot validity
        @param wol_id: the id of work order lot to check.
        """
        context = context or {}
        if wol_id:
            if len(wol_id) > 1:
                raise osv.except_osv(
                    _('Error'),
                    _('There are two work order lots for the same'
                      ' production order with the same number.'))
        else:
            raise osv.except_osv(
                _('Error'),
                _('The Create More Work Order Lots function can be apply.'
                  ' You are trying to create a new work order lot but you'
                  ' dont have create the first one yet.'))
        return True

    def get_first_work_order(self, cr, uid, ids, context=None):
        """
        This method return the id of the first work order lot for the
        specific production order. The first work order lot is the one
        that have de 00001 number.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = {}.fromkeys(ids)
        for production in self.browse(cr, uid, ids, context=context):
            wol_id = wol_obj.search(
                cr, uid, [('production_id', '=', production.id),
                ('number', '=', '00001')], context=context)
            self.check_first_wol_validity(cr, uid, wol_id, context=context)
            wol_id = wol_id[0]
            res.update({production.id: wol_id})
        return len(res.keys()) > 1 and res or res.values()[0]

    def create_orphan_wol(self, cr, uid, ids, fwol_id, wo_values, context=None):
        """
        This method create a new work order lot that is a duplicate one
        from the first work order lot. This method is used to create
        more work order lots when there is needed to process 'Products
        to Consume' that are left.

        Note: This method only can recieve one id. for a list of production ids
        please do a map() function.

        @param fwol_id: the id of the first work order lot for the
                        specified production order
        @param wo_values: list of dictionary values to duplicate the first work
                          order lot work orders.
        @return: the id of the new work order created.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        res = list()
        if not isinstance(ids, (int, long)):
            raise osv.except_osv(
                _('Programming Error'),
                _('You are trying to use the create_orphan_wol() method for'
                  ' more than one production order. This fuction only can'
                  ' process one production order at time so do a map() if you'
                  ' needed for a list of production orders. Thank you.'))
        production = self.browse(cr, uid, ids, context=context)
        fwol_brw = wol_obj.browse(cr, uid, fwol_id, context=context)
        lot_nbr = len(production.wo_lot_ids)
        values = {
            'name': '%s/WOLOT/%05i' % (production.name, lot_nbr + 1),
            'number': '%05i' % (lot_nbr + 1,),
            'production_id': production.id,
            'percentage': fwol_brw.percentage,
            'wo_ids': map(lambda x: (0, 0, x), wo_values),
        }
        new_wol_id = wol_obj.create(cr, uid, values, context=context)
        return new_wol_id

    def get_dict_duplicate_wo(self, cr, uid, ids, fwo_ids, context=None):
        """
        This method create a list of dictonaries that hold the values to create
        in new work orders that are a duplicate copy of the work orders that
        belongs to the first work order lot for the production order.            

        Note: This method only can recieve one id. for a list of production ids
        please do a map() function.

        @param fwo_ids: work order ids of the first work lot.
        @return: list of dictionary (values) to duplicate the work
                 orders.
        """
        context = context or {}
        if not isinstance(ids, (int, long)):
            raise osv.except_osv(
                _('Programming Error'),
                _('You are trying to use the get_dict_duplicate_wo() method for'
                  ' more than one production order. This fuction only can'
                  ' process one production order at time so do a map() if you'
                  ' needed for a list of production orders. Thank you.'))
        wo_fields_to_cp = ['cycle', 'hour', 'product', 'production_id',
                           'qty', 'uom', 'wo_lot_id', 'workcenter_id']
        wo_obj = self.pool.get('mrp.production.workcenter.line')
        res = list()
        sequence = 15

        production = self.browse(cr, uid, ids, context=context)
        lot_nbr = len(production.wo_lot_ids)

        for wo_brw in wo_obj.browse(cr, uid, fwo_ids, context=context):
            values = {}
            for wo_field in wo_fields_to_cp:
                value = getattr(wo_brw, wo_field)
                values.update({wo_field: getattr(value, 'id', value)})
            values.update({
                'name': getattr(wo_brw, 'name').replace(
                    '(1/%s)' % (lot_nbr), '(%s/%s)' % (
                        lot_nbr + 1, lot_nbr)),
                'sequence': sequence,
            })
            res += [values]
            sequence += 15
        return res

    def button_create_wol(self, cr, uid, ids, context=None):
        """
        Create new Work Order Lot to conitue consuming products. It take into
        account the firts work order lot for the production order.
        @return: True
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        wo_obj = self.pool.get('mrp.production.workcenter.line')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for production in self.browse(cr, uid, ids, context=context):
            #~ get first work order lot id and its belongs work orders ids.
            fwol_id = self.get_first_work_order(
                cr, uid, production.id, context=context)
            fwo_ids = [wo_brw.id
                       for wo_brw in wol_obj.browse(
                            cr, uid, fwol_id, context=context).wo_ids]
            #~ create new work order lot
            wo_values = self.get_dict_duplicate_wo(
                cr, uid, production.id, fwo_ids, context=context)
            new_wol_id = self.create_orphan_wol(
                cr, uid, production.id, fwol_id, wo_values, context=context)
        return True

class mrp_workorder_stage(osv.Model):

    _name = 'mrp.workorder.stage'
    _description = 'Work Order Stage'
    _inherit = ['mail.thread']
    _order = 'sequence'

    """
    Manage the change of states of the work orders in kaban views. 
    """

    def _get_wo_state(self, cr, uid, context=None):
        """
        """
        context = context or {}
        wo_obj = self.pool.get('mrp.production.workcenter.line')
        states = wo_obj.fields_get(cr, uid, ['state'], context=context)
        states = states['state']['selection']
        return states

    _columns = {
        'sequence': fields.integer(_('Sequence')),
        'name': fields.char(
            _('Stage Name'),
            required=True,
            size=64,
            translate=True),
        'description': fields.text(_('Description')),
        'state': fields.selection(
            _get_wo_state,
            _('Related Status'),
            required=True,
            help=_('The status of your document is automatically changed'
                   ' regarding the selected stage. For example, if a stage is'
                   ' related to the status \'Close\', when your document'
                   ' reaches this stage, it is automatically closed.')),
        'fold': fields.boolean(
            _('Folded by Default'),
            help=_('This stage is not visible, for example in status bar or'
                   ' kanban view, when there are no records in that stage to'
                   ' display.')),
    }

    _defaults = {
        'sequence': 1,
        'state': 'draft',
        'fold': False,
    }


class mrp_production_workcenter_line(osv.Model):

    _inherit = 'mrp.production.workcenter.line'

    def _get_draft_stage_id(self, cr, uid, context=None):
        """
        """
        context = context or {}
        wos_obj = self.pool.get('mrp.workorder.stage')
        wos_id = \
            wos_obj.search(cr, uid, [('state', '=', 'draft')], context=context)
        return wos_id and wos_id[0]

    def _update_active_lot(self, cr, uid, ids, file_name, arg, context=None):
        """
        Update the work orders active lot field. If a work order lot change its
        state then the work orders associated to that lot will change its
        active lot state too to True or False whatever the case is.
        Note: The Work Order Lot its 'active' when is in open or pendding
        state.
        """
        context = context or {}
        res = {}.fromkeys(ids)
        wol_obj = self.pool.get('mrp.workorder.lot')
        open_wol_ids = wol_obj.search(
            cr, uid, [('state', 'in', ['open','pending'])], context=context)
        for wo_brw in self.browse(cr, uid, ids, context=context):
            res[wo_brw.id] = \
                (wo_brw.wo_lot_id.id in open_wol_ids) and True or False
        return res

    def _get_wo_ids_to_update(self, cr, uid, ids, context=None):
        """
        This method monitors the Work Order Lots that have been change of state
        and return the corresponding work orders associated ids who active_lot
        state need to be updated.
        """
        context = context or {}
        wo_obj = self.pool.get('mrp.production.workcenter.line')
        wo_ids = wo_obj.search(cr, uid, [('wo_lot_id', 'in', ids)],
                               context=context)
        return wo_ids

    _columns = {
        'wo_lot_id': fields.many2one('mrp.workorder.lot',
                                     _('Work Order Lot')),
        'stage_id': fields.many2one('mrp.workorder.stage',
            string=_('Stage'),
            required=True,
            track_visibility='onchange',
            help=_('The stage permits to manage the state of the work orders'
                   ' in the kanban views tools for visualization of the charge'
                   ' and for planning the manufacturing process.')),
        'active_lot': fields.function(
            _update_active_lot,
            type='boolean',
            store={
                'mrp.workorder.lot': (_get_wo_ids_to_update, ['state'], 10),
            },
            string=_('Status by Lot'),
            help=_('If a Work Order Lot is active, then the Work Order is take'
                  ' like active to')),
    }

    _defaults = {
        'stage_id': _get_draft_stage_id,
    }

    def _group_by_full_state(self, cr, uid, ids, domain, read_group_order=None,
                             access_rights_uid=None, context=None):
        """
        Return a tuple of 
        """
        context = context or {}
        wos_obj = self.pool.get('mrp.workorder.stage')
        wos_ids = wos_obj.search(cr, uid, [], context=context)
        wos_brws = wos_obj.browse(cr, uid, wos_ids, context=context)
        res = list()
        for wos in wos_brws:
            res.append((wos.id, wos.name))
        visible = dict([(wos.id, wos.fold) for wos in wos_brws])
        return res, visible

    _group_by_full = {
        'stage_id': _group_by_full_state,
    }

    def write(self, cr, uid, ids, values, context=None, update=True):
        """
        Overwrite the write method to ensure that a work order can change
        state if is not in an active work order lot.
        """
        context = context or {}
        wos_obj = self.pool.get('mrp.workorder.stage')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wo_ids = list()
        troble_wo = dict()
        for wo_brw in self.browse(cr, uid, ids, context=context):
            # Check if Work Orders are new (Without a wol or with a draft wol)
            if ((wo_brw.wo_lot_id and wo_brw.wo_lot_id.state == 'draft')
                or not wo_brw.wo_lot_id):
                wo_ids += [wo_brw.id]
            else:
                if isinstance(values, dict):
                    if wo_brw.wo_lot_id.state in ['open', 'pending']:
                        wo_ids += [wo_brw.id]
                    else:
                        troble_wo.update({wo_brw.id: {
                            'name': wo_brw.name,
                            'state': wo_brw.state,
                            'lot_name': wo_brw.wo_lot_id.name,
                            'lot_state': wo_brw.wo_lot_id.state,
                        }})
                else:
                    raise osv.except_osv(
                        _('Error!'),
                        _('This type of write is not implemented in the'
                          ' mrp_byworkcenter_capacity module yet.'))

        if troble_wo:
            error_by_wo = \
                _('- %s Work Order can be update to %s state because its'
                  ' %s Work Order Lot is in %s state.\n\n')
            raise osv.except_osv(
                _('Error!'),
                _('This operation is no valid. You can\'t change the work'
                  ' order state because it associated lot is no active.\n\n'
                  ' %s' % (
                    [error_by_wo % (
                        troble_wo[trb]['name'],
                        troble_wo[trb]['state'],
                        troble_wo[trb]['lot_name'],
                        troble_wo[trb]['lot_state'])
                     for trb in troble_wo])
                ))

        #~ manage changes in the kanban view
        if values.get('stage_id', False):
            wos_brw = wos_obj.browse(cr, uid, values.get('stage_id'), context=context)
            values.update({'state': wos_brw.state})
        if values.get('state', False):
            values.update({'stage_id': wos_obj.search(
                cr, uid, [('state', '=', values.get('state'))],
                context=context)[0]})

        res = super(mrp_production_workcenter_line, self).write(
            cr, uid, wo_ids, values, context=context, update=update)

        return res


class mrp_workorder_lot(osv.Model):

    _name = 'mrp.workorder.lot'
    _description = "Work Order Lot"

    """
    This model manage the Work Order Lot.
    """

    def _get_lot_state(self, cr, uid, ids, field_name, arg, context=None):
        """
        This method update the work order lot state taking into account the
        state of the work orders associated. This is the logic:
          - work orders 'done' -> work order lot change to 'done' (finished).
          - one work order in 'pause' -> work order lot change to 'pending'.
          - one work order in 'cancel' -> work order lot change to 'pending'
        When the lot work orders are in 'draft' and 'startworking' the state
        of the lot is not affected
        """
        context = context or {}
        res = {}.fromkeys(ids)
        for wol_brw in self.browse(cr, uid, ids, context=context):
            wol_state = wol_brw.state
            wo_states = list(set([wo_brw.state for wo_brw in wol_brw.wo_ids]))

            if wol_state in ['draft', 'picking', 'ready', 'done', 'cancel']:
                res[wol_brw.id] = wol_state
            elif wol_state in ['open', 'pending']:
                if wo_states.count('cancel') or wo_states.count('pause'):
                    res[wol_brw.id] = 'pending'
                elif wo_states.count('done') == len(wo_states):
                    res[wol_brw.id] = 'ready'
                elif wo_states.count('cancel') == len(wo_states):
                    res[wol_brw.id] = 'cancel'
                elif (not wo_states.count('cancel') and
                      not wo_states.count('pause')):
                    res[wol_brw.id] = 'open'
        return res

    def _get_wol_id_to_update(self, cr, uid, ids, context=None):
        """
        @param ids: work order ids list.
        @return: a list of Work Order Lots who Work Workorders state have been
        change.
        """
        context = context or {}
        wo_obj = self.pool.get('mrp.production.workcenter.line')
        res = [wo_brw.wo_lot_id.id
               for wo_brw in wo_obj.browse(cr, uid, ids, context=context)]
        res = list(set(res))
        return res

    def _set_lot_state(self, cr, uid, id, field, value, arg, context=None):
        """
        Write the field state in Work Order Lot.
        """
        context = context or {}
        wol_brw = self.browse(cr, uid, id, context=context)
        if ((wol_brw.production_id and wol_brw.production_id.state not in
             ['in_production','draft']) or not wol_brw.production_id):
            raise osv.except_osv(
                _('Error'),
                _('Trying to set the state of a Work Order Lot (WOL) that have'
                  ' not associated producction order or wich production order'
                  ' is not in \'Production Started\' state.'))
        if value:
            cr.execute(
                "UPDATE mrp_workorder_lot set state='%s' WHERE id=%d" % (
                    value, id))
        return True

    _columns = {
        'name': fields.char(
            _('Ref'),
            size=192,
            help=_('Lot Reference Name.')),
        'number': fields.char(
            _('Number'),
            size=192,
            help=_('Lot Serial Number')),
        'wo_ids': fields.one2many(
            'mrp.production.workcenter.line', 'wo_lot_id',
            string=_('Work Orders'),
            help=_('Work Orders that belogns to this Lot.')),
        'production_id': fields.many2one(
            'mrp.production',
            string=_('Manufacturing Order'),
            help=_('The Manufacturing Order were this Work Order Lot'
                   ' belongs.')),
        'percentage': fields.float(
            _('Percentage'),
            help=_('Percentage of the Raw Material to processs in the Lot.')),
        'state': fields.function(
            _get_lot_state,
            fnct_inv=_set_lot_state,
            type='selection',
            selection=[('draft', 'New'),
                       ('picking', 'Ready to Picking'),
                       ('open', 'In progress'),
                       ('pending', 'Pending'),
                       ('ready', 'Ready to Finish'),
                       ('done', 'Done'),
                       ('cancel', 'Cancel')],
            required=True,
            store={'mrp.production.workcenter.line': (
               _get_wol_id_to_update, ['state'], 10)},
            string=_('State'),
            help=_('Indicate the state of the Lot.')),
    }

    _defaults = {
        'state': 'draft',
    }