# -*- encoding: utf-8 -*-
from . import xfstyle
from xfstyle import css2excel

from openerp.addons.report.controllers import main
from openerp.addons.web.http import route, request  # pylint: disable=F0401
from werkzeug import url_decode  # pylint: disable=E0611
import simplejson
import lxml.html
from lxml import etree
from lxml.html import clean

import xlwt
import StringIO

import logging
_logger = logging.getLogger(__name__)


def get_odoo_style(style, node):
    style['background-color'] = 'rgb(0, 0, 0)'
    if node.attrib.get('style', False):
        style.update(dict(item.split(":") for item in
                     node.attrib.get('style').split(";") if item != ''))
    return style


def text_adapt(text):
    new_text = text.strip().replace('\n', ' ').replace('\r', '')
    return new_text.replace("&nbsp;", " ").replace("  ", "")


def get_xls(html):
    wb = xlwt.Workbook(style_compression=2)
    ws = wb.add_sheet('Sheet 1')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO.StringIO(html), parser)
    root = tree.getroot()
    row = 0
    tables = root.xpath("//table")
    if tables:
        for table in tables:
            heads = table.xpath("thead")
            if not heads:
                heads = table.xpath("table_header")
            if heads:
                for tag_id in heads:
                    rows = tag_id.xpath("tr")
                    if rows:
                        for tr in rows:
                            odoo_styles = get_odoo_style({}, tr)
                            rowspan = 0
                            if tr.attrib.get('rowspan', False):
                                rowspan = int(td.attrib.get('rowspan')) - 1
                            cols = tr.xpath("td")
                            if not cols:
                                cols = tr.xpath("th")
                            if not cols:
                                continue
                            if cols:
                                odoo_styles.update(get_odoo_style(odoo_styles,
                                                                  cols[0]))
                            for k, v in odoo_styles.items():
                                odoo_styles[k] = v.replace(' ', '')
                            new_style = css2excel(odoo_styles)

                            col = 0
                            for td in cols:
                                text = text_adapt(
                                    " ".join([x for x in td.itertext()]))
                                colspan = 0
                                if td.attrib.get('colspan', False):
                                    colspan = int(td.attrib.get('colspan')) - 1
                                try:
                                    ws.write_merge(row, row + rowspan, col,
                                                   col + colspan, float(text),
                                                   new_style)
                                except ValueError:
                                    ws.write_merge(row, row + rowspan, col,
                                                   col + colspan, text,
                                                   new_style)
                                col += colspan + 1
                            # update the row pointer AFTER a row has been
                            # printed this avoids the blank row at the top
                            #  of your table
                            row += rowspan + 1
            body = table.xpath("tbody")
            if not body:
                body = table.xpath("table_body")
            if body:
                for tag_id in body:
                    rows = tag_id.xpath("tr")
                    if rows:
                        for tr in rows:
                            odoo_styles = get_odoo_style({}, tr)
                            rowspan = 0
                            if tr.attrib.get('rowspan', False):
                                rowspan = int(td.attrib.get('rowspan')) - 1
                            cols = tr.xpath("td")
                            if not cols:
                                cols = tr.xpath("th")
                            if not cols:
                                continue
                            if cols:
                                if cols[0].attrib.get('style', False):
                                    odoo_styles = get_odoo_style(odoo_styles,
                                                                 td)
                                for el in cols[0].iterdescendants():
                                    if el.tag == 'span':
                                        if el.attrib.get('style', False):
                                            odoo_styles.update(
                                                get_odoo_style(odoo_styles,
                                                               el))
                            for k, v in odoo_styles.items():
                                odoo_styles[k] = v.replace(' ', '')
                            new_style = css2excel(odoo_styles)

                            col = 0
                            for td in cols:
                                text = text_adapt(
                                    " ".join([x for x in td.itertext()]))
                                colspan = 0
                                if td.attrib.get('colspan', False):
                                    colspan = int(td.attrib.get('colspan')) - 1
                                try:
                                    ws.write_merge(row, row + rowspan, col,
                                                   col + colspan, float(text),
                                                   new_style)
                                except ValueError:
                                    ws.write_merge(row, row + rowspan, col,
                                                   col + colspan, text,
                                                   new_style)
                                col += colspan + 1
                            # update the row pointer AFTER a row has been
                            # printed this avoids the blank row at the top
                            #  of your table
                            row += rowspan + 1
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
