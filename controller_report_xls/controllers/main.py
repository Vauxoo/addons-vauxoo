# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import cssutils
from cssutils import parseString

from werkzeug import url_decode  # pylint: disable=E0611
from lxml import etree


import json
import xlwt

from io import StringIO
from io import BytesIO

from odoo.addons.report_xlsx.controllers.main import ReportController
from odoo.http import route, request  # pylint: disable=F0401
from ..controllers.xfstyle import css2excel

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

_logger = logging.getLogger(__name__)

cssutils.log.setLevel(logging.CRITICAL)


def get_value(value):
    """Returns a value in its proper intended type:
        if value is '-77' it will return -77 of type integer
        if value is '-77.7' it will return -77.7 of type float
        if value is '-7.7.-' it will return '-7.7.-' of type string"""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def is_number(value):
    """Tries to determine if value is a numeric value"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_string(value, thousands_sep=',', decimal_point='.'):
    """Tries to determine if value is not a numeric value, i.e. int or float"""
    set_sign = set([thousands_sep, decimal_point, '-'])
    set_val = set(list(value))

    is_text = False
    if any([val.isalpha() or val.isspace() for val in set_val]):
        is_text = True
    elif not all([val.isdigit() for val in set_val - set_sign]):
        is_text = True
    elif value.count('-') > 1:
        is_text = True
    elif value.count(decimal_point) > 1:
        is_text = True
    elif '-' in set_val and not value[0] == '-':
        is_text = True

    return is_text


def is_formatted_number(value, thousands_sep=',', decimal_point='.'):
    """Determines if value string was previously a float or integer and was
    converted into a formatted number"""
    res = True
    if is_string(value, thousands_sep, decimal_point):
        res = False
    else:
        value = value.replace(thousands_sep, '')
        value = value.replace(decimal_point, '.')
        res = is_number(value)
    return res


def unformat_number(value, lang_sep):
    """Converts a formatted number into a integer, firstly, or a float,
    otherwise it will return original value provided by taking into account
    language separators provided, i.e.,
    for en_US, thousands_separator = ',' and decimal_point = '.' then
        if value is '-7,777.7' it will return -7777.7 of type float
        if value is '-77' it will return -77 of type integer
        if value is '-7.7.-' it will return '-7.7.-' of type string
    for es_ES, thousands_separator = '.' and decimal_point = ',' then
        if value is '-7.777,7' it will return -7777.7 of type float
        if value is '-77' it will return -77 of type integer
        if value is '-7,7.-' it will return '-7,7.-' of type string"""

    thousands_sep = lang_sep.get('thousands_sep', ',')
    decimal_point = lang_sep.get('decimal_point', '.')

    if not is_formatted_number(value, thousands_sep, decimal_point):
        return value

    set_val = set(list(value))
    sign = 1
    if '-' in set_val:
        sign = -1
        value = value.replace('-', '')

    value = value.replace(thousands_sep, '')
    value = value.replace(decimal_point, '.')
    return sign * get_value(value)


def string_to_number(value, lang_sep, style=None):
    """Features:
        - brute force conversion of thousands separated value into float

        TODO:
        - change style in cell to currency if currency symbol available
    """
    return unformat_number(value, lang_sep)


@lru_cache(maxsize=2048)
def get_css_style(csstext, style):
    if not csstext:
        return ""

    cssstyle = ""
    cssnode = parseString(csstext)
    for rule in cssnode.cssRules:
        if rule.selectorText.replace(".", "") != style:
            continue
        cssstyle = str(rule.style.cssText)
        break
    return cssstyle


@lru_cache(maxsize=4096)
def html_xpath(html, xpath):
    return html.xpath(xpath)


def get_odoo_style(html, style, node):
    if node.attrib.get('class', False):
        for class_style in node.attrib.get('class', False).split():
            for style_element in html_xpath(html, '//style[@type="text/css"]'):
                styleclass = get_css_style(style_element.text, class_style)
                style.update(dict(item.split(":") for item in
                             text_adapt(styleclass).split(";") if item != ''))
    if node.attrib.get('style', False):
        style_val = node.attrib.get('style').replace(' ', '')
        style.update(dict(item.split(":") for item in
                     style_val.split(";") if item != ''))
    return style


def write_tables_to_excel(sheet, row, col, tables, html, table_styles,
                          lang_sep):
    for table in tables:
        table_styles = get_odoo_style(html, table_styles, table)
        headers = html_xpath(table, "thead")
        if not headers:
            headers = html_xpath(table, "table_header")
        if headers:
            for header in headers:
                head_style = get_odoo_style(html, table_styles, header)
                rows = html_xpath(header, "tr")
                if rows:
                    row = write_rows_to_excel(sheet, row, col, rows,
                                              html, head_style, lang_sep)
        bodies = html_xpath(table, "tbody")
        if not bodies:
            bodies = html_xpath(table, "table_body")
        if bodies:
            for body in bodies:
                body_style = get_odoo_style(html, table_styles, body)
                rows = html_xpath(body, "tr")
                if rows:
                    row = write_rows_to_excel(sheet, row, col, rows,
                                              html, body_style, lang_sep)
        if not headers and not bodies:
            rows = html_xpath(table, "tr")
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
        cols = html_xpath(tr, "td")
        if not cols:
            cols = html_xpath(tr, "th")
        if not cols:
            continue
        row = write_cols_to_excel(sheet, row, col, rowspan, cols,
                                  html, new_styles, lang_sep)
        row += rowspan + 1
    return row


def write_cols_to_excel(sheet, row, col, rowspan, nodes, html, styles,
                        lang_sep):
    for td in nodes:
        new_styles = get_odoo_style(html, styles, td)
        # Check tables in column
        tables = html_xpath(td, "table")
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
    """Takes and HTML string and converts it into an XLS stream,
    by trying to properly convert the tables, rows and cells into a meaningful
    Worksheet.
    """
    if lang_sep is None:
        # Asume lang = en_US
        lang_sep = {
            'decimal_point': '.',
            'thousands_sep': ',',
        }
    wb = xlwt.Workbook(style_compression=2)
    ws = wb.add_sheet('Sheet 1')
    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)
    root = tree.getroottree()
    html = root
    row = 0
    col = 0
    table_styles = {}
    table_styles['background-color'] = '#FFFFFF'
    # Check header tables
    tables = html_xpath(root, "//div[@class=\"header\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles,
                                    lang_sep)
    # Check page tables
    tables = html_xpath(root, "//div[@class=\"page\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles,
                                    lang_sep)
    # Check footer tables
    tables = html_xpath(root, "//div[@class=\"footer\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles,
                                    lang_sep)
    stream = BytesIO()
    wb.save(stream)
    html_xpath.cache_clear()
    return stream.getvalue()


def get_lang_sep(req, context):
    """Get Decimal & Thousands separators on Language being used"""
    lang_obj = req.env['res.lang']
    lang = context.get('lang', 'en_US')
    lang_brw = lang_obj.search([('code', '=', lang)], limit=1)
    return {
        'decimal_point': lang_brw.decimal_point,
        'thousands_sep': lang_brw.thousands_sep,
    }


class ReportController(ReportController):

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

        requestcontent = json.loads(data)
        url = requestcontent[0]

        # decoding the args represented in JSON
        url_split = url.split('?')
        index = len(url_split) > 1 and 1 or 0
        new_data = url_decode(url_split[index]).items()

        new_data = dict(new_data)
        if new_data.get('context'):
            context = json.loads(new_data['context']) or {}

        if not context.get('xls_report'):
            return response

        reportname = url.split('/report/pdf/')[1].split('?')[0]
        if '/' in reportname:
            reportname = reportname.split('/')[0]

        report = request.env['ir.actions.report']._get_report_from_name(reportname)
        filename = "%s.%s" % (report.name, 'pdf')
        # As headers have been implement as as list there are no unique headers
        # adding them just result into duplicated headers that are not
        # unique will convert them into dict update the required header and
        # then will be assigned back into headers
        headers = dict(response.headers.items())
        headers.update(
            {'Content-Disposition':
                'attachment; filename=%s.xls;' % reportname})
        response.headers.clear()
        for key, value in headers.items():
            response.headers.add(key, value)
        return response

    @route([
        '/report/converter>/<reportname>',
        '/report/converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        """Intercepts original method from report module by using a key in context
        sticked when print a report from a wizard ('xls_report') if True this
        method will return a XLS File otherwise it will return the customary
        PDF File"""


        report_obj = request.env['ir.actions.report']
        report = report_obj._get_report_from_name(reportname)
        context = dict(request.env.context)


        origin_docids = docids
        if docids:
            docids = [int(idx) for idx in docids.split(',')]
        options_data = None
        if data.get('options'):
            options_data = json.loads(data['options'])
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the one from
            # the webclient *but* if the user explicitely wants to change the
            # lang, this mechanism overwrites it.
            data_context = json.loads(data['context']) or {}

            if data_context.get('lang'):
                del data_context['lang']
            context.update(data_context)

        xls_report = context.get('xls_report', False)
        if not xls_report:
            return super(ReportController, self).report_routes(
                    reportname, docids=origin_docids,
                    converter=converter, **data)

        html = report.with_context(context).render_qweb_html(
                docids, data=options_data)[0]
        xls_stream = get_xls(html, get_lang_sep(request, context))
        xlshttpheaders = [
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Length', len(xls_stream)),
        ]
        return request.make_response(xls_stream, headers=xlshttpheaders)
