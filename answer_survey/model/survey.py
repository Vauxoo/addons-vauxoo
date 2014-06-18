# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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

import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import strftime
import os

from openerp import netsvc, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _


class survey(osv.Model):
    _inherit = 'survey'

    def fill_survey(self, cr, uid, ids, context=None):
        res = super(survey,self).fill_survey(cr, uid, ids, context)
        res.update( {
            'target': 'inline',
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
