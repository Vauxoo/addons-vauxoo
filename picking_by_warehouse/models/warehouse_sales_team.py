# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################


from openerp import api, fields, models, SUPERUSER_ID


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

    _name = "warehouse.user"

    @api.model
    def get_from_my_warehouses(self):
        """ Review current users sales teams/warehouse and return the ids
        sub-groups that match to the warehouses

        :return: list of ids that match with the user warehouses
        """
        res = []
        user = self.env.user
        cursor = self.env.cr

        # Current user sales teams
        cursor.execute("SELECT DISTINCT section_id FROM sale_member_rel"
                       " WHERE member_id = '%s'" % user.id)
        records = cursor.dictfetchall()
        sale_teams = [record.get('section_id', False) for record in records]
        # user_sale_teams = self.env['crm.case.section'].search([]).filtered(
        #     lambda team: user in team.member_ids)
        if not sale_teams:
            return res

        # Get the related Warehouses. The users could belong to a several sale
        # teams but this teams could not have warehouse defined. Need to be
        # careful to
        where_clause = "IN " + str(tuple(sale_teams)) if len(sale_teams) > 1 \
            else '= ' + str(sale_teams[0])
        cursor.execute("SELECT DISTINCT warehouse_id FROM crm_case_section"
                       " WHERE id " + where_clause +
                       " AND warehouse_id IS NOT NULL")
        records = cursor.dictfetchall()
        warehouses = set([
            record.get('warehouse_id', False) for record in records])
        # warehouse_ids = user_sale_teams.mapped('warehouse_id').mapped('id')
        if not warehouses:
            return res

        if self and warehouses:
            where_clause = "IN " + str(tuple(warehouses)) \
                if len(warehouses) > 1 else '= ' + str(warehouses.pop())
            cursor.execute(
                "SELECT id FROM " + self._table +
                " WHERE warehouse_id " + where_clause)
            records = cursor.dictfetchall()
            res = [record.get('id', False) for record in records]
        return res

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """ Filter the stock.pickings related to the current user
        """
        if self.env.user.id == SUPERUSER_ID:
            return
        ids = self.browse(self.get_from_my_warehouses())
        self = self & ids
        return super(WarehouseUser, self).check_access_rights(operation)


class StockPickingType(models.Model):

    _name = "stock.picking.type"
    _inherit = ['stock.picking.type', 'warehouse.user']


# class StockPicking(models.Model):

#     _name = "stock.picking"
#     _inherit = ['stock.picking', 'warehouse.user']
