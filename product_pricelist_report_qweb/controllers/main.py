from openerp.addons.controller_report_xls.controllers import main
from openerp.addons.web.http import route


class ReportController(main.ReportController):

    @route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        return super(ReportController, self).report_routes(
            reportname, docids=docids, converter=converter, **data)
