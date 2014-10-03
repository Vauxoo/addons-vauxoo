import time
import os
import platform
from openerp.report import report_sxw


class report_webkit_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(
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
                      parser=report_webkit_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
