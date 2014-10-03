# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
# Credits######################################################
#    Coded by: author Miguel Delgado <miguel@openerp.com.ve>               #
#    Planified by: Nhomar Hernandez                                        #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################

from openerp.osv import osv, fields
import time


class wizard_price_list_sequence_report(osv.TransientModel):
    _name = "wizard.project.issue.report"

    _columns = {
        'task': fields.boolean('Task?', help="Select this option if you want to see task in the report", select=True,),
    }

    def print_report(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['task'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'project.issuereport',
            'datas': datas
        }

