# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.comm
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

# This module eventually depends from
# l10n_pa_localization to add township
# (corregimiento) to field name, because
# it is a requirement.

# TODO
# Modify display_address to use context
# in this module base and not depends
# from panama localization.
# The localization modules have to override
# this module to get from address_format
# another required fields like township.

{
    'name': 'Partner Long Name',
    'version': '1.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'license': 'AGPL-3',
    'category': '',
    'depends': [
        'base',
        'l10n_pa_localization',
    ],
    'data': [
    ],
    'demo': [
    ],
    'test': [],
    'qweb': [],
    'js': [],
    'css': [],
    'installable': True,
}
