# coding: utf-8
# © 2016 Vauxoo - http://www.vauxoo.comm
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

{
    'name': 'Set Group By Department',
    'version': '8.0.1.0.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'license': 'AGPL-3',
    'category': '',
    'depends': [
        'hr',
    ],
    'data': [
        'security/res_groups.xml',
        'wizard/wizard_department_group_view.xml',
    ],
    'demo': [
        'demo/employees.xml',
    ],
    'test': [],
    'qweb': [],
    'js': [],
    'css': [],
    'installable': True,
}
