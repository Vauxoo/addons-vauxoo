# -*- coding: utf-8 -*-

from ..controllers.xfstyle import css2excel

from openerp.addons.report.controllers import main
from openerp.addons.web.http import route, request  # pylint: disable=F0401
from werkzeug import url_decode  # pylint: disable=E0611
import simplejson
from lxml import etree
import cssutils
from cssutils import parseString
import xlwt
import StringIO


import logging
cssutils.log.setLevel(logging.CRITICAL)
_logger = logging.getLogger(__name__)


def get_css_style(csstext, style):
    cssstyle = ""
    if csstext:
        cssnode = parseString(csstext)
        stylesheet = cssnode.cssRules
        for rule in stylesheet:
            if rule.selectorText.replace(".", "") == style:
                cssstyle = str(rule.style.cssText)
    return cssstyle


def get_odoo_style(html, style, node):
    if node.attrib.get('class', False):
        for style_element in html.xpath('//style[@type="text/css"]'):
            styleclass = get_css_style(style_element.text,
                                       node.attrib.get('class'))
            style.update(dict(item.split(":") for item in
                         text_adapt(styleclass).split(";") if item != ''))
    if node.attrib.get('style', False):
        style.update(dict(item.split(":") for item in
                     node.attrib.get('style').split(";") if item != ''))
    return style


def write_rows_to_excel(ws, row, nodes, html, styles):
    for tr in nodes:
        new_styles = get_odoo_style(html, styles, tr)
        rowspan = 0
        if tr.attrib.get('rowspan', False):
            rowspan = int(tr.attrib.get('rowspan')) - 1
        cols = tr.xpath("td")
        if not cols:
            cols = tr.xpath("th")
        if not cols:
            continue
        if cols:
            write_cols_to_excel(ws, row, rowspan, cols, html, new_styles)
        row += rowspan + 1
    return row


def write_cols_to_excel(ws, row, rowspan, nodes, html, styles):
    col = 0
    for td in nodes:
        new_styles = get_odoo_style(html, styles, td)
        colspan = 0
        if td.attrib.get('colspan', False):
            colspan = int(td.attrib.get('colspan')) - 1
        text = text_adapt(" ".join([x for x in td.itertext()]))
        try:
            new_text = float(text)
        except ValueError:
            new_text = text
        cell_styles = css2excel(new_styles)
        ws.write_merge(row, row+rowspan,
                       col, col+colspan,
                       new_text, cell_styles)
        col += colspan + 1
    return True


def text_adapt(text):
    new_text = text.strip().replace('\n', ' ').replace('\r', '')
    new_text = new_text.replace("&nbsp;", " ").replace("  ", "")
    return new_text.replace("; ", ";").replace(": ", ":")


def write_cell_to_excel(ws, row, rowspan, col, colspan, node, styles):
    # Should implement if column have many classes with different styles,
    # but write_rich_text doesn't support write to multiple rows and columns
    # taken from rowspan and colspan
    cell_styles = css2excel(styles)
    rich_text = []
    for line in node.iter():
        text = text_adapt(" ".join([x for x in line.itertext()]))
        try:
            new_text = float(text)
        except ValueError:
            new_text = text
        new_style = get_odoo_style(styles, line)
        if new_text:
            rich_text.append(new_text)
            text_style = css2excel(new_style)
            rich_text.append(text_style)
    ws.write_rich_text(row, col, tuple(rich_text), cell_styles)
    return True


def get_xls(html):
    wb = xlwt.Workbook(style_compression=2)
    ws = wb.add_sheet('Sheet 1')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO.StringIO(html), parser)
    root = tree.getroot()
    html = root
    row = 0
    tables = root.xpath("//table")
    if tables:
        for table in tables:
            table_styles = {}
            table_styles['background-color'] = '#FFFFFF'
            table_styles = get_odoo_style(html, table_styles, table)
            headers = table.xpath("thead")
            if not headers:
                headers = table.xpath("table_header")
            if headers:
                for header in headers:
                    head_style = get_odoo_style(html, table_styles, header)
                    rows = header.xpath("tr")
                    if rows:
                        row = write_rows_to_excel(ws, row, rows,
                                                  html, head_style)
            bodies = table.xpath("tbody")
            if not bodies:
                bodies = table.xpath("table_body")
            if bodies:
                for body in bodies:
                    body_style = get_odoo_style(html, table_styles, body)
                    rows = body.xpath("tr")
                    if rows:
                        row = write_rows_to_excel(ws, row, rows,
                                                  html, body_style)
            if not headers and not bodies:
                rows = table.xpath("tr")
                if rows:
                    row = write_rows_to_excel(ws, row, rows,
                                              html, table_styles)
            row += 1
    stream = StringIO.StringIO()
    wb.save(stream)
    return stream.getvalue()


class ReportController(main.ReportController):

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        """
        This is an override of original method in ReportController class in
        report module
        What is intended here is to properly assign to the extension to XLS
        """
        response = super(ReportController, self).report_download(data, token)
        context = request.context
        if response is None:
            return response

        requestcontent = simplejson.loads(data)
        url = requestcontent[0]

        # decoding the args represented in JSON
        url_split = url.split('?')
        index = len(url_split) > 1 and 1 or 0
        new_data = url_decode(url_split[index]).items()

        new_data = dict(new_data)
        if new_data.get('context'):
            context = simplejson.loads(new_data['context']) or {}

        if not context.get('xls_report'):
            return response

        reportname = url.split('/report/pdf/')[1].split('?')[0]
        # As headers have been implement as as list there are no unique headers
        # adding them just result into duplicated headers that are not
        # unique will convert them into dict update the required header and
        # then will be assigned back into headers
        headers = dict(response.headers.items())
        headers.update(
            {'Content-Disposition':
                'attachment; filename=%s.xls;' % reportname})
        response.headers.clear()
        for key, value in headers.iteritems():
            response.headers.add(key, value)
        return response

    @route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report_obj = request.registry['report']
        cr, uid, context = request.cr, request.uid, request.context
        origin_docids = docids
        if docids:
            docids = [int(idx) for idx in docids.split(',')]
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
                reportname, docids=origin_docids, converter=converter, **data)

        html = report_obj.get_html(cr, uid, docids, reportname,
                                   data=options_data, context=context)
        xls_stream = get_xls(html)
        xlshttpheaders = [('Content-Type', 'application/vnd.ms-excel'),
                          ('Content-Length', len(xls_stream)),
                          ]
        return request.make_response(xls_stream, headers=xlshttpheaders)
