# Copyright 2020 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class InheritedCrmSaseSection(models.Model):
    _inherit = "crm.team"

    default_warehouse = fields.Many2one('stock.warehouse',
                                        string='Default Warehouse',
                                        help='In this field can be '
                                        'defined a default warehouse for '
                                        'the related users to the sales team.')
    journal_team_ids = fields.One2many(
        'account.journal', 'section_id', string="Journal's sales teams",
        help="Choose the Journals that user with this sale team can see")
    journal_stock_id = fields.Many2one(
        'account.journal', 'Journal stock valuation',
        help='It indicates journal to be used when move line is created with'
        'the warehouse of this sale team')

    @api.multi
    def write(self, vals):
        """The workers cache is cleared when the `journal_team_ids` field is modified to reflect the changes when the
        following domain is called:
        * `rule_default_warehouse_journal`
        """
        if vals.get("journal_team_ids"):
            self.clear_caches()
        return super(InheritedCrmSaseSection, self).write(vals)

    @api.model
    def create(self, values):
        """The workers cache is cleared to reflect the changes when the following domain is called:
        * `rule_default_warehouse_journal`
        """
        if values.get("journal_team_ids"):
            self.clear_caches()
        return super(InheritedCrmSaseSection, self).create(values)

    @api.multi
    def unlink(self):
        """The workers cache is cleared when a record it's deleted,
        """
        self.clear_caches()
        return super(InheritedCrmSaseSection, self).unlink()

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
        warehouse = user_brw.sale_team_id.default_warehouse
        if warehouse:
            warehouse_id = warehouse.id
            model_obj = self.env['ir.model']
            fields_obj = self.env['ir.model.fields']
            model_id = model_obj.search([('model', '=', self._name)])
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
    def read(self, fields_list=None, load='_classic_read'):
        """This method is overwrite because we need to propagate SUPERUSER_ID
        when picking are chained in another warehouse without access to read"""
        if self.env.user.has_group('default_warehouse_from_sale_team.'
                                   'group_limited_default_warehouse_sp'):
            # we need to change to SUPERUSER_ID to allow access to read
            self = self.sudo()
        return super(WarehouseDefault, self).read(fields_list, load)

    @api.model
    def create(self, vals):
        sequence_obj = self.env['ir.sequence']
        pick_type_obj = self.env['stock.picking.type']
        if vals.get('warehouse_id', 'picking_type_id'):
            code = self._name
            if code == 'purchase.requisition':
                code = 'purchase.order.requisition'
            pick_warehouse_id = pick_type_obj.browse(
                vals.get('picking_type_id')).warehouse_id.id
            warehouse_id = vals.get('warehouse_id', pick_warehouse_id)
            section_id = self.env['crm.team'].search(
                [('default_warehouse', '=', warehouse_id)], limit=1)
            sequence_id = sequence_obj.search(
                [('section_id', '=', section_id.id),
                 ('code', '=', code)], limit=1)
            if sequence_id:
                vals['name'] = sequence_id.next_by_id()
        return super(WarehouseDefault, self).create(vals)
