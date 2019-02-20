# coding: utf-8
##############################################################################
#
#    Account analytic required module for OpenERP
#    Copyright (C) 2011 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#    Developped during the Akretion-Camptocamp code sprint of June 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv


class AccountAccountType(osv.osv):
    _inherit = "account.account.type"

    _columns = {
        'analytic_policy': fields.selection([
            ('optional', 'Optional'),
            ('always', 'Always'),
            ('never', 'Never')
        ], 'Policy for analytic account',
            help=('Set the policy for analytic accounts : if you select '
                  '"Optional", the accountant is free to put an analytic '
                  'account on an account move line with this type of account; '
                  'if you select "Always", the accountant will get an error '
                  'message if there is no analytic account ; if you select '
                  '"Never", the accountant will get an error message if an '
                  'analytic account is present.')),
    }

    _defaults = {
        'analytic_policy': lambda *a: 'optional',
    }
