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
            'mrp.workoder.lot', 'production_id',
            string=_('Work Orders Lots'),
            help=_('Work Orders Lots.')),
    }

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

                # NOTE: the field wc_brw.time_efficiency it does
                # not exist in the model. why this???

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
        wo_lot_obj = self.pool.get('mrp.workoder.lot')
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

    _columns = {
        'wo_lot_id': fields.many2one('mrp.workoder.lot',
                                     _('Work Order Lot')),
        'stage_id': fields.many2one('mrp.workorder.stage',
            string=_('Stage'),
            required=True,
            track_visibility='onchange',
            help=_('The stage permits to manage the state of the work orders'
                   ' in the kanban views tools for visualization of the charge'
                   ' and for planning the manufacturing process.')),
    }

    _defaults = {
        'stage_id': _get_draft_stage_id,
    }


class mrp_workoder_lot(osv.Model):

    _name = 'mrp.workoder.lot'
    _description = "Work Order Lot"

    """
    This model manage the Work Order Lot.
    """

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
        'state': fields.selection(
            [('draft', 'New'),
             ('open', 'In progress'),
             ('done', 'Done'),
             ('pending', 'Pending')],
             string=_('State'),
             help=_('Indicate the state of the Lot.')),
    }

    _defaults = {
        'state': 'draft',
    }