from openerp.addons.report.controllers import main
from openerp.addons.web.http import route, request
import simplejson
from bs4 import BeautifulSoup
import xlwt
import StringIO


class ReportController(main.ReportController):

    def get_xls(self, html):
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet 1')
        soup = BeautifulSoup(html)
        row = 0
        for tag_id in ['table_header', 'table_body']:
            table = soup.find("table", id=tag_id)
            rows = table.findAll("tr")
            for tr in rows:
                cols = tr.findAll("td")
                if not cols:
                    continue
                col = 0
                for td in cols:
                    text = "%s" % td.text.encode('ascii', 'ignore')
                    text = text.replace("&nbsp;", " ")
                    text = text.strip()
                    try:
                        ws.row(row).set_cell_number(col, float(text))
                    except ValueError:
                        ws.write(row, col, text)
                    col += 1
                # update the row pointer AFTER a row has been printed
                # this avoids the blank row at the top of your table
                row += 1

        stream = StringIO.StringIO()
        wb.save(stream)
        return stream.getvalue()

    @route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report_obj = request.registry['report']
        cr, uid, context = request.cr, request.uid, request.context

        if docids:
            docids = [int(i) for i in docids.split(',')]
        options_data = None
        if data.get('options'):
            options_data = simplejson.loads(data['options'])
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the one from
            # the webclient *but* if the user explicitely wants to change the
            # lang, this mechanism overwrites it.
            data_context = simplejson.loads(data['context']) or {}

            if data_context.get('lang'):
                del data_context['lang']
            context.update(data_context)

        if not context.get('xls_report'):
            return super(ReportController, self).report_routes(
                reportname, docids=docids, converter=converter, **data)

        html = report_obj.get_html(cr, uid, docids, reportname,
                                   data=options_data, context=context)
        xls_stream = self.get_xls(html)
        xlshttpheaders = [('Content-Type', 'application/vnd.ms-excel'),
                          ('Content-Length', len(xls_stream)),
                          ('filename', 'Report.xls')]
        return request.make_response(xls_stream, headers=xlshttpheaders)
