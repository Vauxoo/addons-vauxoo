import time
import os
import platform
from openerp.report import report_sxw


class report_webkit_variation_group(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_webkit_variation_group, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'os': os,
            'platform': platform,
            'this_self': self,
            'this_context': context
        })

report_sxw.report_sxw('report.webkitmrp.production_variation_group',
                      'mrp.production',
                      'addons/mrp_report_webkit_wizard/report/report_webkit_variation_group.mako',
                      parser=report_webkit_variation_group)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
