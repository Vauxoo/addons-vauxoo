# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################


from openerp import api, fields, models


class InheritedCrmSaseSection(models.Model):

    _inherit = "crm.case.section"

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse')


class WarehouseUser(models.Model):

    """If you inherit from this model and add a field called warehouse_id into
    the model itself then the default value for such the records of that model
    will be filtered taking into account your setted sales team.
    """

    _auto = False
    _name = "warehouse.user"

    @api.multi
    def check_access_rule(self, operation):
        """
        POC
        """
        access_rule = super(WarehouseUser, self).check_access_rule(operation)

        # TODO delete this
        print ' ------ check_access_rule'
        # print access_rule
        import pdb
        pdb.set_trace()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """ Can view only the ones for for the warehouse
        """
        res = super(WarehouseUser, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        warehouse = self.env.user.default_section_id.warehouse_id

        print ' ------ field_view_get', warehouse
        # import pdb
        # pdb.set_trace()

        return res


class StockPickingType(models.Model):

    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'warehouse.user']

class StockPicking(models.Model):

    _name = "stock.picking"
    _inherit = ['stock.picking', 'warehouse.user']
