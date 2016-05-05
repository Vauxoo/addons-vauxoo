# coding: utf-8

from openerp import fields, models


class TestGenericModel(models.Model):
    """Generic model to perform tests over the
        sale_team_warehouse module that makes a
        Monkey-patch over  global default_get
        Case: field with default
    """
    _name = 'test.generic.model'
    _description = 'Generic model to perform tests'

    name = fields.Char(string='Reference/Description', index=True,
                       readonly=True)
    character = fields.Char(string='Character', readonly=True,
                            default='Test Default Chart')


class TestDefaultGetModel(models.Model):
    """Generic model to perform tests over the
        sale_team_warehouse module that makes a
        Monkey-patch over  global default_get
        Case: overwriting default_get
    """
    _name = 'test.default.get.model'
    _description = 'Generic model to perform tests'

    name = fields.Char(string='Reference/Description', index=True,
                       readonly=True)
    character = fields.Char(string='Character', readonly=True)

    def default_get(self, cr, uid, fields, context=None):
        """Default get method locally inherited using old api.
        """
        if context is None:
            context = {}
        res = super(TestDefaultGetModel, self).default_get(
            cr, uid, fields, context=context)
        if 'character' in fields:
            res.update(character='Demo Text For Test Purposes')
        return res


class TestDefaultGetWarehouseModel(models.Model):
    """Generic model to perform tests over the
        sale_team_warehouse module that makes a
        Monkey-patch over  global default_get
        Case: testing warehouse_id global default
    """
    _name = 'test.default.get.warehouse.model'
    _description = 'Generic model to perform tests'

    def _default_warehouse(self):
        user = self.env['res.users'].browse(self._uid)
        res = self.env['stock.warehouse'].search([('company_id', '=',
                                                  user.company_id.id)],
                                                 limit=1)
        return res and res[0] or False

    name = fields.Char(string='Reference/Description', index=True,
                       readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   default=_default_warehouse)
