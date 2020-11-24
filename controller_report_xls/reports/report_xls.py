import base64
import logging
from io import BytesIO
import lxml.html
import xlwt
from odoo import api, models

from ..reports.xfstyle import css2excel


_logger = logging.getLogger(__name__)


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


def write_tables_to_excel(sheet, row, col, tables, html, table_styles):
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
                                              html, head_style)
        bodies = table.xpath("tbody")
        if not bodies:
            bodies = table.xpath("table_body")
        if bodies:
            for body in bodies:
                body_style = get_odoo_style(html, table_styles, body)
                rows = body.xpath("tr")
                if rows:
                    row = write_rows_to_excel(sheet, row, col, rows,
                                              html, body_style)
        if not headers and not bodies:
            rows = table.xpath("tr")
            if rows:
                row = write_rows_to_excel(sheet, row, col, rows,
                                          html, table_styles)
        row += 1
    return row


def write_rows_to_excel(sheet, row, col, nodes, html, styles):
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
                                      html, new_styles)
        row += rowspan + 1
    return row


def write_cols_to_excel(sheet, row, col, rowspan, nodes, html, styles):
    for td in nodes:
        new_styles = get_odoo_style(html, styles, td)
        # Check tables in column
        tables = td.xpath("table")
        if tables:
            row = write_tables_to_excel(sheet, row, col, tables,
                                        html, new_styles)
        else:
            new_text = ""
            colspan = 0
            if td.attrib.get('colspan', False):
                colspan = int(td.attrib.get('colspan')) - 1
            text = text_adapt(" ".join([x for x in td.itertext()]))
            try:
                new_text = float(text)
            except ValueError:
                new_text = text
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


def write_cell_to_excel(sheet, row, rowspan, col, colspan, node, styles):
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
    sheet.write_rich_text(row, col, tuple(rich_text), cell_styles)
    return True


def get_xls(html):
    wb = xlwt.Workbook(style_compression=2)
    ws = wb.add_sheet('Sheet 1')
    root = lxml.html.fromstring(html)
    html = root
    row = 0
    col = 0
    table_styles = {}
    table_styles['background-color'] = '#FFFFFF'
    # Check header tables
    tables = root.xpath("//div[@class=\"header\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles)
    # Check page tables
    tables = root.xpath("//div[@class=\"page\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles)
    # Check footer tables
    tables = root.xpath("//div[@class=\"footer\"]/table")
    if tables:
        row = write_tables_to_excel(ws, row, col, tables, html, table_styles)
    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


class ActionReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.noguess
    def report_action(self, docids, data=None, config=True):
        response = super(ActionReport, self).report_action(docids, data, config)
        context = self.env.context
        if response is None or not context.get('xls_report'):
            return response
        html = self.render_qweb_html(docids, data=data)[0]
        html = html.decode('utf-8')
        xls_stream = get_xls(html)
        attachment = self.env['ir.attachment'].create({
            'name': 'ProductPricelist.xls',
            'datas_fname': 'ProductPricelis',
            'datas': base64.encodestring(xls_stream),
            'type': 'binary',
            'mimetype': 'application/vnd.ms-excel',
            'description': 'Product Pricelis',
        })
        return {
            'name': 'Product Pricelist',
            'type': 'ir.actions.act_url',
            'url': "web/content/?id=" + str(attachment.id) + "&download=true&filename=" + attachment.name,
            'target': 'new',
        }
