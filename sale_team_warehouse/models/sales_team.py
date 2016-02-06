# coding: utf-8

from openerp import api, fields, models
from openerp.models import BaseModel


class InheritedCrmSaseSection(models.Model):

    '''
        inheriting the class to add additional field
    '''
    _inherit = "crm.case.section"

    default_warehouse = fields.Many2one('stock.warehouse',
                                        string='Default Warehouse',
                                        help='In this field can be '
                                        'defined a default warehouse for '
                                        'the related users to the sales team.')

# This code must be solved without any monkey patch.
# look for a more ellegant way.
# @api.model
# def default_get(self, fields_list):
#     '''
#         This method modifies global default_get method
#         using _patch_method that allows Monkey-patch
#         that allows access the original method and get its
#         result. Also is possible restore the original
#         method using _revert_method
#     '''
#     defaults = default_get.origin(self, fields_list)
#     res_users_obj = self.env['res.users']
#     res_users_brw = res_users_obj.browse(self._uid)
#     warehouse_id = hasattr(res_users_brw, 'default_section_id')\
#         and res_users_brw.default_section_id and \
#         res_users_brw.default_section_id.default_warehouse.id
#     if warehouse_id:
#         model_obj = self.env['ir.model']
#         fields_obj = self.env['ir.model.fields']
#         model_id = model_obj.search([('model', '=', self._model._name)])
#         fields_data = fields_obj.search(
#             [('model_id', '=', model_id.id),
#              ('relation', '=', 'stock.warehouse'),
#              ('ttype', '=', 'many2one')])
#         names_list = []
#         [names_list.append(field.name) for field in fields_data if
#          field.name not in names_list]
#         defaults.update({name: warehouse_id for name in names_list if
#                         defaults.get(name)})
#     return defaults

# BaseModel._patch_method('default_get', default_get)
