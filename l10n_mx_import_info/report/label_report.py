# -*- encoding: utf-8 -*-
import time
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp import pooler, tools


class label_report(report_sxw.rml_parse):
    def __init__(self, cr, user, name, context):
        super(label_report, self).__init__(cr, user, name, context=context)
        self.localcontext.update({
            'time': time,
            'getAdd': self._getAdd,
        })

    def _getAdd(self, obj):
        """
    Custom method that process obj and return required data to report
    @param obj: parameter to method
        """
        print 'DEDEDEED'
        return 'ESTA ES LA DIRECCION Y EL TELEELFONO (52)222333444'


report_sxw.report_sxw(
    'report.label.report.import.info',
    'import.info',
    'addons/l10n_mx_import_info/report/label_report.rml',
    parser=label_report
)
