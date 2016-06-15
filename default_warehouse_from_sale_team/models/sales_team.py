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

    default_warehouse = fields.Many2one('stock.warehouse',
                                        string='Default Warehouse',
                                        help='In this field can be '
                                        'defined a default warehouse for '
                                        'the related users to the sales team.')


class WarehouseDefault(models.Model):

    """If you inherit from this model and add a field called warehouse_id into
    the model itself then the default value for such model will be the one
    setted into the sales team.

    If you inherit from this model and add a field called warehouse_id into
    the model itself then the default value for such the records of that model
    will be filtered taking into account your setted sales team.
    """

    _auto = False
    _name = "default.warehouse"

    @api.model
    def default_get(self, fields_list):
        """Force that if model has a field called warehouse_id the default
        value is the one in the sales team in the user setted
        """
        defaults = super(WarehouseDefault,
                         self).default_get(fields_list)
        res_users_obj = self.env['res.users']
        user_brw = res_users_obj.browse(self._uid)
        warehouse = user_brw.default_section_id.default_warehouse
        if warehouse:
            warehouse_id = warehouse.id
            model_obj = self.env['ir.model']
            fields_obj = self.env['ir.model.fields']
            model_id = model_obj.search([('model', '=', self._model._name)])
            fields_data = fields_obj.search(
                [('model_id', '=', model_id.id),
                 ('relation', '=', 'stock.warehouse'),
                 ('ttype', '=', 'many2one')])
            names_list = list(set([field.name for field in fields_data]))
            defaults.update(
                {name: warehouse_id for name in names_list
                 if defaults.get(name)})
        return defaults

    @api.multi
    def check_access_rule(self, operation):
        """
        POC
        """
        super(WarehouseDefault, self).check_access_rule(operation)

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
        res = super(WarehouseDefault, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        warehouse = self.env.user.default_section_id.warehouse_id

        print ' ------ field_view_get', warehouse
        # import pdb
        # pdb.set_trace()

        return res


class SaleOrder(models.Model):

    _name = "sale.order"
    _inherit = ['sale.order', 'default.warehouse']


class StockPickingType(models.Model):

    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'default.warehouse']

class StockPicking(models.Model):

    _name = "stock.picking"
    _inherit = ['stock.picking', 'default.warehouse']
