# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#                Miguel Delgado          <miguel@openerp.com.ve>
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
###############################################################################
from osv import osv
from osv import fields

class print_account_invoice_report(osv.osv_memory):
    """
    OpenERP Wizard : print.account.invoice.report
    """
    _name = "print.account.invoice.report"

    def _get_company(self, cr, uid, ids, context=None):
        pass

    def _get_report(self, cr, uid, ids, context=None):
        pass

    _columns = {
        'company': fields.char('Company', 64, readonly=True, requied=True),
        'report_format': fields.binary("Report", readonly=True, required=True)
    }

    _defaults = {
        'company': _get_company,
        'report_format': _get_report,
    }
print_account_invoice_report()
