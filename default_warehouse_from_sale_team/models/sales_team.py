# coding: utf-8

from openerp import api, fields, models


class InheritedCrmSaseSection(models.Model):

    _inherit = "crm.case.section"

    default_warehouse = fields.Many2one('stock.warehouse',
                                        string='Default Warehouse',
                                        help='In this field can be '
                                        'defined a default warehouse for '
                                        'the related users to the sales team.')

    @api.multi
    def update_users_sales_teams(self):
        """ This method will review the users every time a sale team is create
        / write to:

        - if add a member and this one has not default sale team then set the
          current team as the new default sale team
        - if remove a member of the sale team and this one has as default the
          current sale team then will update the user to set default sale teams
          to False
        - if they are just added or remove from the sale team we need to make
          a dummy write in order to update the user sales_team_wh_ids and this
          way the filtering rule will works to show the records only related to
          the real user current sale teams configured warehouses.
        """
        for team in self:

            # Add default team to users without default
            wo_default_team = team.member_ids.filtered(
                lambda user: not user.default_section_id)
            for user in wo_default_team:
                user.write({'default_section_id': team.id})

            # Remove default team for users that are not longer in the current
            # team
            default_current_team = self.env['res.users'].search(
                [('default_section_id', '=', team.id)])
            remove_default_team = default_current_team - team.member_ids
            for user in remove_default_team:
                user.write({'default_section_id': False})

            # Dummy write to update the m2m user.sale_teams in order to be
            # capable of rendering the ir.rules properly.
            for member in team.member_ids:
                member.write({})

        return True


class WarehouseDefault(models.Model):
    """If you inherit from this model and add a field called warehouse_id into
    the model itself then the default value for such model will be the one
    setted into the sales team.
    """

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
