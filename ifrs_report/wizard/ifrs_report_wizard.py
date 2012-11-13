# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from osv import fields, osv
from tools.translate import _
import netsvc

class ifrs_report_wizard(osv.osv_memory):

    """ Wizard que permite al usuario elegir que periodo quiere imprimir del año fiscal """

    _name = 'ifrs.report.wizard'
    _description = 'IFRS Report'
    _columns = {
       'period': fields.many2one('account.period', 'Force period', help='Fiscal period to assign to the invoice. Keep empty to use the period of the current date.'),
    }

    def _get_period(self, cr, uid, context={}):

        """ Return default account period value """

        account_period_obj = self.pool.get('account.period')
        ids = account_period_obj.find(cr, uid, context=context)
        period_id = False
        if ids:
            period_id = ids[0]
        return period_id

    def print_report(self, cr, uid, context={}):

        """ Llama a imprimir el reporte """
        #~ NOTAK; Pendientes... TODO averiguar como hacer para que el boton mande a imprimir el reporte
        return True

ifrs_report_wizard()


#~ class cfd_print(wizard.interface):
        #~ states = {
        #~ 'init': {
            #~ 'actions': [],
            #~ 'result': {
                #~ 'type': 'print',
                #~ 'report': 'ifrs_report',
                #~ 'state': 'end',
            #~ }
        #~ },
    #~ }
#~ cfd_print("cfd.wizard.cfd.print")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
