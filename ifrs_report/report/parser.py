#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#	Module Writen to OpenERP, Open Source Management Solution
#	Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#	All Rights Reserved
###############Credits######################################################
#	Coded by: Katherine Zaoral <katherine.zaoral@vauxoo.com>
#	Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#	Planified by: Humberto Arocha <hbto@vauxoo.com>
#	Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################


import time
from report import report_sxw
import mx.DateTime


class ifrs_report(report_sxw.rml_parse):

	_iter_record = 0
	_total_record = 0
	_period_name = {}
	_title_line = 'Flujo de efectivo por las actividades operativas:'

	def __init__(self, cr, uid, name, context):
		super(ifrs_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'get_lines': self._get_lines,
			'get_hour': self._get_hour,
			'get_time': self._get_time,
			#~ Format method helpers
			'get_total_ifrs_lines': self._get_total_ifrs_lines,
			'get_padding_level' : self._get_padding_level,
			'get_line_color' : self._get_line_color,
			'get_td_format' : self._get_td_format,
			'get_amount_format' : self._get_amount_format,
			#~ Dinamic data
			'get_report_title' : self._get_report_title,
			'get_periods_name' : self._get_periods_name,
			'get_column_name'  : self._get_column_name,
		})
		self.cr = cr
		self.context = context
		self.uid = uid

		print "\n__init__():"
		print "self._iter_record = " + str(self._iter_record)
		print "self._total_record = " + str(self._total_record)
		#~ self.cr.execute("select ifrs_lines_ids from ifrs_ifrs where id=%s", str(uid) )
		#~ print "cr.fetchone() = " + str(cr.fetchone())
		#~ # raro pero me dice que no existe la columna ifrs_lines_ids

	def _get_lines(self, ifrs_brws):
		res = {}

		for ifrs_line in ifrs_brws.ifrs_lines_ids:
			p = ifrs_line.id

			if ifrs_line.type != 'abtract':
				res[p] = {'name':ifrs_line.name,'amount':ifrs_line.amount}

		return (res,)

	def _get_hour(self,float_hour,format='hh:mm:ss'):
		seconds=int(float_hour*3600)
		hours = seconds / 3600
		seconds -= 3600*hours
		minutes = seconds / 60
		seconds -= 60*minutes
		return format=='hh:mm:ss' and "%02d:%02d:%02d" % (hours, minutes, seconds) or "%02d:%02d" % (hours, minutes+round(seconds/60.0))

	def _get_time(self, strtime = time.strftime('%Y-%m-%d %H:%M:%S')):
		t = time.strptime(strtime,'%Y-%m-%d %H:%M:%S')
		t = time.mktime(t)

		return time.strftime('%Y-%m-%d', time.gmtime(t))

	#########################################################################################################################
	#~ Dinamic Data

	def _get_report_title(self, ifrs_doc):
		
		"""devuelve la cadena con el nombre del reporte segun sea la pagina para el caso de imprimir varios reportes"""
		
		print "\n_get_report_title():" + str(ifrs_doc.title)
		#~ hacer iterar en los objetos tomados y devolver consulta de titulo
		return str(ifrs_doc.title)

	def _get_periods_name(self, ifrs_obj):

		"""devuelve el nombre del periodo fiscal"""

		print "\n_get_periods_name():"
		period_dict = {}
		period_dict['0'] = self._title_line

		periods = self.pool.get('account.period')
		periods_ids = ifrs_obj.fiscalyear_id._get_fy_period_ids()
		
		ii=1
		for period_id in periods_ids:
			period_dict[str(ii)] = periods.browse(self.cr, self.uid, period_id).name
			ii+=1

		self._period_name = period_dict
		
		print '_period_name' + str(self._period_name)

	def _get_column_name(self, column_num):

		"""devuelve string con el nombre del periodo que debe titular ese numero de columna"""
		print "\n_get_column_name(columna %s):  " % column_num
		return self._period_name[column_num]

	#########################################################################################################################
	#~ Format method helpers

	def _get_total_ifrs_lines(self, ifrs_brws):
		res = 0
		for ifrs_line in ifrs_brws.ifrs_lines_ids:
			res += 1

		self._total_record = res
		self._iter_record = res
		# otro modo: borrar ultimas 2 lineas y descomentar las siguientes
		# hace la integracion de funciones, pero no funciona
		#~ self._update_total_record(res)
		#~ self._update_iter_record(res)

		# impresion de la comprobacion
		#~ print "2 execute _get_total_ifrs_lines()"
		#~ print "self._total_record = " + str(self._total_record)
		#~ print "self._iter_record = " + str(self._iter_record)
		#~ print "OUT execute _get_total_ifrs_lines()"

		print "\n_get_total_ifrs_lines():"
		print "self._iter_record = " + str(self._iter_record)
		print "self._total_record = " + str(self._total_record)

	#~ # OJO: intente utilizar estos emtodos en el metodo de arriba pero no pude.... no funciona

	#~ def _update_total_record(self, total):
		#~ self._total_record = total
		#~ print "execute _update_total_record()"
	#~
	#~ def _update_iter_record(self, total):
		#~ self._iter_record = total
		#~ print "execute _update_iter_record()"

	def _get_padding_level(self, level):
		return "padding_level_"+str(level)
		#~ OJO::: el level_padding de total es que ¿? cual le pones...
		#~ OJO::: cuidado como se utiliza el level_padding = 0
		#~ HACER: cambio de... ¿?

	def _get_line_color(self):
		res_color = "dark_color"

		if self._total_record % 2:
			par = True
		else:
			par = False

		#~ NOTAK; probar optimizacion
		#~ par = True if self._total_record % 2 else False


		if self._iter_record == self._total_record:
			res_color = "light_color"
		else:
			if par:
				if self._iter_record % 2:
					res_color = "light_color"
				else:
					res_color = "dark_color"
			else:
				if self._iter_record % 2:
					res_color = "dark_color"
				else:
					res_color = "light_color"

		#~ NOTAK; probar optimizacion
		#~ res_color = "light_color" if self._iter_record == self._total_record or par and self._iter_record % 2 or !par and !self._iter_record % 2 else "dark_color"

		self._iter_record-=1
		return res_color

	#~ NOTAK; No la he utilizado todavia
	def _get_amount_format(self, amount):
		#~ """ auto-doc: _get_amount_format() return the format, '(negative amount)' or 'amount' depending of the amount sign """
		if amount < 0.0:
			amount = '('+str(amount)+')'
		return amount

	#~ NOTAK; No la he utilizado todavia
	def _get_td_format(self, ifrsl_type):
		#~ """ auto-doc: _get_td_format() return the style of the cell for amount, total type (with a black thick line below) or simple (dont apply any format) """
		if ifrsl_type in 'total':
			return amount
		else:
			return "simple_amount_data"


report_sxw.report_sxw(
	'report.ifrs',
	'ifrs.ifrs',
	'ifrs_report/report/ifrs_cash_flow_indirect.rml',
	parser=ifrs_report,
	header = False
)

report_sxw.report_sxw(
	'report.ifrs_12',
	'ifrs.ifrs',
	'ifrs_report/report/ifrs_cash_flow_indirect_12.rml',
	parser=ifrs_report,
	header = False
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
