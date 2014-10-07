# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
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
from openerp.osv import osv, fields


class ir_action_report_xml(osv.Model):

    _inherit = "ir.actions.report.xml"

    _columns = {
        'active': fields.boolean('Active'),
        'sequence': fields.integer('Sequence'),
        'company_id': fields.many2one('res.company', 'Company'),
    }

    _order = 'sequence'

    _defaults = {
        'active': 1,
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.company')._company_default_get(cr, uid,
                                            'ir.actions.report.xml', context=c),
    }
