# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Ernesto Garcia Medina (ernesto_gm@vauxoo.com)
#
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

from openerp.tools.translate import _
from openerp.osv import fields, osv


class hr_contract(osv.Model):

    _inherit = "hr.contract"

    _columns = {
        'risk_rank_id': fields.many2one('payroll.risk.rank.contract', 'Payroll Risk Rank', help='key According class in which the patterns must be registered in accordance to the activities they perform their employees, as provided in Article 196 of Regulation in Respect of Membership Classification Companies, collection and fiscal requirement.Catalogue published in the Internet portal of the SAT'),
    }
