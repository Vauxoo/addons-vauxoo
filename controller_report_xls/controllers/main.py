# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
# #############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.addons.report.controllers import main
from openerp.addons.web.http import route, request  # pylint: disable=F0401
from werkzeug import url_decode  # pylint: disable=E0611
from lxml import etree

from ..controllers.xfstyle import css2excel

import simplejson
import xlwt

import StringIO
import logging
_logger = logging.getLogger(__name__)


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_formatted_number(value, thousands_sep, decimal_point):
    set_sign = set([thousands_sep, decimal_point, '-'])
    set_val = set(list(value))
    if set_val == set():
        return False
    elif any([val.isalpha() or val.isspace() for val in set_val]):
        return False
    elif not all([val.isdigit() for val in set_val - set_sign]):
        return False
    elif value.count('-') > 1:
        return False
    elif '-' in set_val and not value[0] == '-':
        return False

    if value.count(thousands_sep) > 0:
        value = value.replace(thousands_sep, '')
    if decimal_point in value:
        value = value.replace(decimal_point, '.')
    if is_integer(value):
        return True
    elif is_float(value):
        return True

    return False


def unformat_number(value, lang_sep):
    thousands_sep = lang_sep.get('thousands_sep', ',')
    decimal_point = lang_sep.get('decimal_point', '.')

    if not is_formatted_number(value, thousands_sep, decimal_point):
        return value

    set_val = set(list(value))
    sign = 1
    if '-' in set_val:
        sign = -1
        value = value.replace('-', '')

    if value.count(thousands_sep) > 0:
        value = value.replace(thousands_sep, '')
    if decimal_point in value:
        value = value.replace(decimal_point, '.')

    if is_integer(value):
        value = int(value)
    elif is_float(value):
        value = float(value)

    return sign * value


def string_to_number(value, lang_sep, style=None):
    '''
    Features:
        - brute force conversion of thousands separated value into float

        TODO:
        - converted thousands separated value by char into float
        - take the thousands separator from res.lang
        - take the decimal separator from res.lang
        - change style in cell to currency if currency symbol available
    '''
    return unformat_number(value, lang_sep)


def get_css_style(csstext, style):
    cssstyle = ""
    if csstext:
        try:
            import cssutils
            from cssutils import parseString
            cssutils.log.setLevel(logging.CRITICAL)
        except ImportError:
            return ""
        cssnode = parseString(csstext)
        stylesheet = cssnode.cssRules
        for rule in stylesheet:
            if rule.selectorText.replace(".", "") == style:
                cssstyle = str(rule.style.cssText)
    return cssstyle


def get_odoo_style(html, style, node):
    if node.attrib.get('class', False):
        for class_style in node.attrib.get('class', False).split():
            for style_element in html.xpath('//style[@type="text/css"]'):
                styleclass = get_css_style(style_element.text,
                                           class_style)
                style.update(dict(item.split(":") for item in
                             text_adapt(styleclass).split(";") if item != ''))
    if node.attrib.get('style', False):
        style.update(dict(item.split(":") for item in
                     node.attrib.get('style').split(";") if item != ''))
    return style


def write_tables_to_excel(sheet, row, col, tables, html, table_styles,
                          lang_sep):
    for table in tables:
        table_styles = get_odoo_style(html, table_styles, table)
        headers = table.xpath("thead")
        if not headers:
            headers = table.xpath("table_header")
        if headers:
            for header in headers:
                head_style = get_odoo_style(html, table_styles, header)
                rows = header.xpath("tr")
                if rows:
                    row = write_rows_to_excel(sheet, row, col, rows,
                                              html, head_style, lang_sep)
        bodies = table.xpath("tbody")
        if not bodies:
            bodies = table.xpath("table_body")
        if bodies:
            for body in bodies:
                body_style = get_odoo_style(html, table_styles, body)
                rows = body.xpath("tr")
                if rows:
                    row = write_rows_to_excel(sheet, row, col, rows,
                                              html, body_style, lang_sep)
        if not headers and not bodies:
            rows = table.xpath("tr")
            if rows:
                row = write_rows_to_excel(sheet, row, col, rows,
                                          html, table_styles, lang_sep)
        row += 1
    return row


def write_rows_to_excel(sheet, row, col, nodes, html, styles, lang_sep):
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
            row = write_cols_to_excel(sheet, row, col, rowspan, cols,
                                      html, new_styles, lang_sep)
        row += rowspan + 1
    return row


def write_cols_to_excel(sheet, row, col, rowspan, nodes, html, styles,
                        lang_sep):
    for td in nodes:
        new_styles = get_odoo_style(html, styles, td)
        # Check tables in column
        tables = td.xpath("table")
        if tables:
            row = write_tables_to_excel(sheet, row, col, tables,
                                        html, new_styles, lang_sep)
        else:
            new_text = ""
            colspan = 0
            if td.attrib.get('colspan', False):
                colspan = int(td.attrib.get('colspan')) - 1
            text = text_adapt(" ".join([x for x in td.itertext()]))
            new_text = string_to_number(text, lang_sep)
            cell_styles = css2excel(new_styles)
            sheet.write_merge(row, row+rowspan,
                              col, col+colspan,
                              new_text, cell_styles)
            col += colspan + 1
    return row


def text_adapt(text):
    new_text = text.replace('\n', ' ').replace('\r', '')
    new_text = new_text.replace("&nbsp;", " ").replace("  ", "")
    return new_text.replace("; ", ";").replace(": ", ":").strip()


def get_xls(html, lang_sep=None):
    if lang_sep is None:
        # Asume lang = en_US
        lang_sep = {
            'decimal_point': '.',
            'thousands_sep': ',',
        }
    wb = xlwt.Workbook(style_compression=2)
    ws = wb.add_sheet('Sheet 1')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO.StringIO(html), parser)
    root = tree.getroot()
    html = root
    row = 0
    col = 0
    table_styles = {}
    table_styles['background-color'] = '#FFFFFF'
    # Check header tables
    tables = root.xpath("//div[@class=\"header\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles,
                                    lang_sep)
    # Check page tables
    tables = root.xpath("//div[@class=\"page\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles,
                                    lang_sep)
    # Check footer tables
    tables = root.xpath("//div[@class=\"footer\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles,
                                    lang_sep)
    stream = StringIO.StringIO()
    wb.save(stream)
    return stream.getvalue()


def get_lang_sep(req, context):
    """Get Decimal & Thousands separators on Language being used"""
    lang_obj = req.registry['res.lang']
    lang = context.get('lang', 'en_US')
    cur, uid = req.cr, req.uid
    lang_ids = lang_obj.search(cur, uid, [('code', '=', lang)])
    lang_brw = lang_obj.browse(cur, uid, lang_ids[0])
    return {
        'decimal_point': lang_brw.decimal_point,
        'thousands_sep': lang_brw.thousands_sep,
    }


class ReportController(main.ReportController):

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        """This is an override of original method in ReportController class in
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
        xls_stream = get_xls(html, get_lang_sep(request, context))
        xlshttpheaders = [('Content-Type', 'application/vnd.ms-excel'),
                          ('Content-Length', len(xls_stream)),
                          ]
        return request.make_response(xls_stream, headers=xlshttpheaders)
