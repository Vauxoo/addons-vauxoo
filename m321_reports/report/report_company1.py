# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>   #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve            #
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
import time
import pooler
from report import report_sxw
from tools.translate import _

class base_report(report_sxw.rml_parse):
  """
  Description about base_report
  """
  
  def __init__(self, cr, uid, name, context=None):
    """
    Initlize a report parser, add custome methods to localcontext 
    @param cr: cursor to database
    @param user: id of current user
    @param name: name of the reports it self
    @param context: context arguments, like lang, time zone 
    """
    super(base_report, self).__init__(cr, uid, name, context=context)
    self.localcontext.update({
      'time': time,
    })

report_sxw.report_sxw(
  'report.base.report',
  'account.invoice',
  'addons/base_report/report/report_company1.rml',
  parser=base_report
)
  # 1 addons/nombre del modulo/carpeta(report)/nombre del archivo rml
  # 2 A modo didactico vamos a poner que el modulo al que le vamos a poner el reporte es a res.partner
  #   pero podria ser cualquier modulo.
