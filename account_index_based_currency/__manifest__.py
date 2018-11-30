# © 2018 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'author': 'Vauxoo',
    'category': 'Accounting & Finance',
    'demo_xml': [],
    'depends': ['account'],
    'installable': True,
    'name': 'Account Index Based Currency',
    'test': [],
    'data': [
        'views/invoice_view.xml',
        'views/res_company_view.xml',
    ],
    'version': '12.0.1.0.0',
    'website': 'www.vauxoo.com',
    'pre_init_hook': 'pre_init_hook',
    'license': 'AGPL-3'
}
