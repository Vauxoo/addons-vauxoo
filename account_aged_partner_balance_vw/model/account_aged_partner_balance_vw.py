# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
############################################################################
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
import openerp.tools as tools
from openerp.tools.translate import _

import openerp.netsvc as netsvc
import time
import os


class account_aged_partner_balance_vw(osv.TransientModel):
    _name = 'account.aged.partner.balance.vw'
    _rec_name = 'partner_id'
    _order = 'partner_id.name'

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner'),
        'total': fields.float(u'Total'),
        'not_due': fields.float(u'Not Due'),
        'days_due_01to30': fields.float(u'01/30'),
        'days_due_31to60': fields.float(u'31/60'),
        'days_due_61to90': fields.float(u'61/90'),
        'days_due_91to120': fields.float(u'91/120'),
        'days_due_121togr': fields.float(u'+121'),
        'company_id': fields.many2one('res.company', u'Company'),
        'currency_company_id': fields.many2one('res.currency', u'Company Currency'),
    }
