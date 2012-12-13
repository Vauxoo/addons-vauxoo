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
    _period_info_list = []    #~ [ 0 : period_enumerate, 1 : period_id, 2 : period_name ]
    _title_line = ' '

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
            'get_row_style' : self._get_row_style,
            'get_td_format' : self._get_td_format,
            'get_amount_format' : self._get_amount_format,
            #~ Dinamic data
            'get_report_title' : self._get_report_title,
            'get_periods_name_list' : self._get_periods_name_list,
            'get_column_name'  : self._get_column_name,
            'get_amount_value' : self._get_amount_value,
            'get_fiscalyear_print_info' : self._get_fiscalyear_print_info,
            'get_period_print_info' : self._get_period_print_info,
            'get_partner_detail' : self.get_partner_detail
        })
        self.cr = cr
        self.context = context
        self.uid = uid

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

        """ Return the current IFRS doc name """
        #~ TODO al agregar el campo de codigo en el ifrs concatenar cadena
        return '[' + str(ifrs_doc.code) + '] ' + str(ifrs_doc.title)

    def _get_periods_name_list(self, ifrs_obj,fiscalyear_id):

        """devuelve una lista con la info de los periodos fiscales (numero mes, id periodo, nombre periodo)"""

        period_list = self._period_info_list = []
        period_list.append( ('0', None , self._title_line ) ) 

        fiscalyear_bwr = self.pool.get('account.fiscalyear').browse(self.cr, self.uid, fiscalyear_id)
        
        periods_ids = fiscalyear_bwr._get_fy_period_ids()

        periods = self.pool.get('account.period')
        
        for ii, period_id in enumerate(periods_ids, start=1):
            period_list.append((str(ii), period_id, periods.browse(self.cr, self.uid, period_id).name ))

        self._period_info_list = period_list

    def _get_column_name(self, column_num):

        """devuelve string con el nombre del periodo que debe titular ese numero de columna"""

        return self._period_info_list[column_num][2]

    def _get_amount_value(self, ifrs_line, period_num=None, target_move=None, pd=None):
        
        '''devuelve la cantidad correspondiente al periodo'''

        context = {}
        if period_num:
            period_id = self._period_info_list[period_num][1]
            context = {'period_from': period_id, 'period_to': period_id, 'state': target_move, 'partner_detail':pd}
        else:
            context = {'whole_fy': 'True'} 

        ifrs_l_obj = self.pool.get('ifrs.lines')

        #~ print "\n_get_amount_value():" + str(ifrs_l_obj._get_sum(self.cr, self.uid, ifrs_line.id, context = context))
        return ifrs_l_obj._get_sum(self.cr, self.uid, ifrs_line.id, context = context)

    def _get_fiscalyear_print_info(self, fiscalyear_id):

        ''' Return all the printable information about fiscalyear'''

        fiscalyear = self.pool.get('account.fiscalyear').browse(self.cr, self.uid, fiscalyear_id)
        res = str(fiscalyear.name) + ' [' + str(fiscalyear.code) + ']'
        return res

    def _get_period_print_info(self, period_id, report_type):

        ''' Return all the printable information about period'''

        if report_type == 'all':
            res = 'All Periods of the fiscalyear.'
        else:
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id)
            res = str(period.name) + ' [' + str(period.code) + ']'

        return res

    #########################################################################################################################
    #~ Format method helpers

    def _get_total_ifrs_lines(self, ifrs_brws):

        res = 0
        for ifrs_line in ifrs_brws.ifrs_lines_ids:
            res += 1

        self._total_record = res
        self._iter_record = res

    def _get_padding_level(self, level):
        return "padding_level_"+str(level)
        #~ OJO::: el level_padding de total es que ¿? cual le pones...
        #~ OJO::: cuidado como se utiliza el level_padding = 0
        #~ TODO: remake with new modeling of ifrs.ifrs models

    def _get_row_style(self):

        """ Return the name of the row style (defined at .rml) """

        if self._iter_record == self._total_record:
            res_style = "first"
        else:
            if self._iter_record % 2:
                res_style = "dark_color"
            else:
                res_style = "light_color"

        self._iter_record-=1
        return res_style

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
        
    def get_partner_detail(self, ifrs_l):
        ifrs = self.pool.get('ifrs.lines')
        aml_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        res = []
        if ifrs_l.type =='detail':
            ids2 = [lin.id for lin in ifrs_l.cons_ids]
            ids3 = account_obj._get_children_and_consol(self.cr, self.uid, ids2)
            print ids3,'imprimo ids3'
            self.cr.execute(""" SELECT rp.id
                FROM account_move_line l JOIN res_partner rp ON rp.id = l.partner_id
                WHERE l.account_id IN %s
                GROUP BY rp.id """, ( tuple(ids3), ) 
                )
            dat = self.cr.dictfetchall()
            res = [lins for lins in partner_obj.browse( self.cr, self.uid, [li['id'] for li in dat] )]
            print res,'imprimo res'
        return res and res or [0]

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
