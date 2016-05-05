# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################


import time
from openerp.report import report_sxw


class ProjectTaskWorkReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ProjectTaskWorkReport, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
            'get_time': self._get_time,
            'get_hour': self._get_hour,
        })

    def _get_hour(self, float_hour, format='hh:mm:ss'):
        """This method takes a floating
        and returns it in  time format 'hh:mm:ss' or 'hh:mm'
        This Method was taken from
        http://stackoverflow.com/questions/775049/python-time-seconds-to-hms
        """
        seconds = int(float_hour * 3600)
        hours = seconds / 3600
        seconds -= 3600 * hours
        minutes = seconds / 60
        seconds -= 60 * minutes
        return format == 'hh:mm:ss' and "%02d:%02d:%02d" % (hours, minutes, seconds) or "%02d:%02d" % (hours, minutes + round(seconds / 60.0))

    def _get_time(self, strtime=time.strftime('%Y-%m-%d %H:%M:%S')):
        """This method take strtime in the format '%Y-%m-%d %H:%M:%S'
        and returns it in the format '%Y-%m-%d'
        """
        t = time.strptime(strtime, '%Y-%m-%d %H:%M:%S')
        t = time.mktime(t)

        return time.strftime('%Y-%m-%d', time.gmtime(t))

    def _get_lines(self, ptw_brws):
        res = {}

        for ptw in ptw_brws:

            prt, p = ptw.partner_id or False, ptw.partner_id and ptw.partner_id.id or False
            pjt, j = ptw.project_id or False, ptw.project_id and ptw.project_id.id or False
            iss, i = ptw.issue_id or False, ptw.issue_id and ptw.issue_id.id or False

            #~ Llenar los partners en el diccionario
            if res.get(p):
                res[p]['t'] += ptw.hours
            else:
                res[p] = {'o': prt, 'd': {}, 't': ptw.hours}

            #~ Llenar los proyectos en el diccionario
            if not res[p]['d'].get(j):
                res[p]['d'][j] = {'o': pjt, 'd': {}}

            #~ Llenar las incidencias en el diccionario
            if res[p]['d'][j]['d'].get(i):
                res[p]['d'][j]['d'][i]['d'].append(ptw)
            else:
                res[p]['d'][j]['d'][i] = {'o': iss, 'd': [ptw]}
        return (res,)


report_sxw.report_sxw(
    'report.project_task_work',
    'project.task.work',
    'addons/project_task_work/report/project_task_work.rml',
    parser=ProjectTaskWorkReport,
    header=False
)
