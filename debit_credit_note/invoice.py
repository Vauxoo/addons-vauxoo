# coding: utf-8
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp import api
from openerp.osv import fields, osv


class AccountInvoice(osv.Model):
    _inherit = 'account.invoice'
    _columns = {
        'parent_id': fields.many2one('account.invoice',
                                     'Parent Invoice',
                                     readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     help='This is the main invoice that has '
                                     'generated this credit note'),
        'child_ids': fields.one2many('account.invoice',
                                     'parent_id',
                                     'Debit and Credit Notes',
                                     readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     help='These are all credit and debit '
                                     'to this invoice'),
    }

    @api.one
    def copy(self, default={}):
        """ Allows you to duplicate a record,
        child_ids, nro_ctrl and reference fields are
        cleaned, because they must be unique
        """
        default.update({
            'child_ids': [],
        })
        return super(AccountInvoice, self).copy(default)
