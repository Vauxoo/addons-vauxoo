# coding: utf-8
# © 2016 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

from openerp import api, fields, models


class WizardDepartmentGroup(models.TransientModel):
    """Adds a wizard to remove all created groups and according to the
    department assign the group in question to the employee.
    """

    _name = 'wizard.department.group'

    dept_group_id = fields.Many2one(
        'res.groups',
        string="Select the Vauxoo Group that do you want to add.",
        ondelete='set null',
    )

    def _brw_active_employees(self):
        return self.env['hr.employee'].browse(
            self._context.get('active_ids'))

    @api.multi
    def set_group(self):
        users_obj = self.env['res.users']
        for record in self._brw_active_employees():
            if record.user_id:
                users_obj = users_obj + record.user_id
            else:
                work_email = record.work_email
                users_id = users_obj.search(
                    [('login', '=', work_email)])
                users_obj = users_obj + users_id
                record.write({
                    'user_id': users_id.id,
                })
        users_obj.write({
            'groups_id': [(6, 0, [self.dept_group_id.id])]
        })
        return False
