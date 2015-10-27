# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp import models, fields, api, _


class WarehouseReceiptInput(models.TransientModel):

    _name = 'wizard.warehouse.receipt.input'

    name = fields.Char(
        required=True,
        string='Filter Name',
        help='The name that the filter will receive. '
             'With this name, it will be possible make an easy search in order'
             ' to verify old courier receptions in the system.')
    bol = fields.Char(
        string='Bill of Lading',
        help='Number of the container. This is an informative value and'
             ' if it set then will be used a as name prefix.'
             ' Is a document (number) issued by a carrier which details a'
             ' shipment of merchandise and gives title of that shipment to a'
             ' specified party.')
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        required=True,
        string='Purchase Orders',
        help='The orders which will appear in the report. The purchase order'
             ' is the first group level of the report.')
    whr_filter = fields.Boolean(
        string='Generate Filter',
        help='Generates the filter to build the report')
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        help='Source location of the moves to show')
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        help='Destination location of the moves to show')

    @api.multi
    def view_moves(self):
        """
        Will open the filter stock move view.
        """
        name, domain, model, context = self.get_whr_filter_data()
        if self.whr_filter:
            self.create_whr_filter(name, domain, model, context)

        ctx = dict(self._context).copy()
        ctx.update(context)
        return {
            'domain': domain,
            'name': name,
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': model,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    @api.multi
    def get_whr_filter_data(self):
        """
        Return the date to be use as data to create the stock move filter.
        :return: tuple (name, domain, model name)
        """
        name = ''.join([
            _('WHR'), ': ', self.bol and self.bol + ' ' or '',
            self.name])
        model = 'stock.move'
        domain = [
            ('purchase_order_id', 'in', self.purchase_order_ids.mapped('id'))]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        if self.location_dest_id:
            domain.append(('location_dest_id', '=', self.location_dest_id.id))
        context = {'group_by': ['purchase_order_id', 'warehouse_receipt_id']}
        return name, domain, model, context

    @api.multi
    def create_whr_filter(self, name, domain, model, context):
        """ Create filter with the result of the query

        :name: name of the filter
        :domain: stock move domain
        :model: model name
        :context: the context to group the results

        :return: if_filters record created
        """
        filter_obj = self.env['ir.filters']
        irfilter = filter_obj.search([
            ('name', '=', name),
            ('domain', '=', str(domain)),
            ('context', '=', str(context)),
            ('model_id', '=', model),
        ])
        if not irfilter:
            irfilter = filter_obj.create({
                'name': name,
                'domain': domain,
                'context': context,
                'model_id': model})
        return irfilter
