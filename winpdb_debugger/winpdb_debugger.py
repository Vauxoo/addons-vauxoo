# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP
#    Copyright (C) 2009-TODAY (<http://clearcorp.co.cr>).
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


from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools import config
#~ import pdb;pdb.set_trace()

import rpdb2

"""
ask_form ='''<?xml version="1.0"?>
<form string="Winpdb debugger">
    <label string="Open Winpdb and set the password to the OpenERP server administrator password. Then clic 'Start Winpdb debugger'." colspan="4"/>
    <label string="The system will wait for 5 minutes until you open a connection. If no connection is opened, the server will continue." colspan="4"/>
</form>
'''

finish_form ='''<?xml version="1.0"?>
<form string="Winpdb debugger">
    <label string="Winpdb attached or timeout." colspan="4"/>
</form>
'''
"""
class winpdb_debugger_wizard(osv.osv_memory):
    _name = 'winpdb.debugger.wizard'

    def action_start_debugger(self, cr, uid, data, context):
        rpdb2.start_embedded_debugger(config['admin_passwd'])
        return{}




winpdb_debugger_wizard()


"""
return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'winpdb.debugger.wizard',
            'views': [('winpdb_debugger_close__wizard','form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }


"""
