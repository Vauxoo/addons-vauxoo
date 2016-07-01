# coding: utf-8
# © 2016 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

from openerp.tests.common import TransactionCase


class TestSetGroupByDepartment(TransactionCase):
    """In order to test the wizard that removes all created groups and
    according to the department assign the group in question to the employee.
    So, this test does the following:

    1. Takes the employees who will be assigned a new group.
    2. Calls the wizard to set only the new group for the employees.
    3. Do an assertTrue to verify that the new group has been set correctly.
    """

    def setUp(self):
        """Define global variables to test method."""
        super(TestSetGroupByDepartment, self).setUp()
        self.hr_employee_obj = self.env['hr.employee']
        self.users_obj = self.env['res.users']
        self.employee_1 = self.env.ref('set_group_by_department.employee_1')
        self.employee_2 = self.env.ref('set_group_by_department.employee_2')
        self.employee_3 = self.env.ref('set_group_by_department.employee_3')
        self.employee_4 = self.env.ref('set_group_by_department.employee_4')
        self.employee_5 = self.env.ref('set_group_by_department.employee_5')
        self.user_1 = self.env.ref('set_group_by_department.user_employee_1')
        self.user_2 = self.env.ref('set_group_by_department.user_employee_2')
        self.user_3 = self.env.ref('set_group_by_department.user_employee_3')
        self.group_id = self.env.ref('set_group_by_department.'
                                     'res_group_vx_administrative_team')
        self.wiz_obj = self.env['wizard.department.group'].with_context({
            'active_model': 'hr.employee',
            'active_ids': [self.employee_1.id, self.employee_2.id,
                           self.employee_3.id, self.employee_4.id,
                           self.employee_5.id],
        })

    def test_10_set_new_group_and_user_id(self):
        """Set the new group and the user_id if necessary on the employees.
        """
        wiz_id = self.wiz_obj.create({
            'dept_group_id': self.group_id.id,
        })
        wiz_id.set_group()
        # Verify that the new group was set to the employee's user.
        self.assertEqual(self.user_1.groups_id.id, self.group_id.id,
                         'A different group was established.')
        self.assertEqual(self.user_2.groups_id.id, self.group_id.id,
                         'A different group was established.')
        self.assertEqual(self.user_3.groups_id.id, self.group_id.id,
                         'A different group was established.')
        # Verify that the related user_id was set in the employee_3 too.
        self.assertEqual(self.employee_3.user_id.id, self.user_3.id,
                         'A different user_id was established.')
        # For employees 4 and 5 the new group was not established because they
        # don't have their corresponding user.
        # So, I verify that the employees 4 and 5 don't have a related user_id.
        self.assertTrue(self.employee_4.user_id.id is False,
                        'This employee should not have a user_id.')
        self.assertTrue(self.employee_5.user_id.id is False,
                        'This employee should not have a user_id.')
