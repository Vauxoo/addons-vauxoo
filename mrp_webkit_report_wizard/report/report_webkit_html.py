# coding: utf-8
import time
import os
import platform
from openerp.report import report_sxw


class ReportWebkitHtml(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportWebkitHtml, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'os': os,
            'platform': platform
        })

report_sxw.report_sxw('report.webkitmrp.production_variation',
                      'mrp.production',
                      'addons/mrp_report_webkit_wizard/report/report_webkit_html.mako',
                      parser=ReportWebkitHtml)
