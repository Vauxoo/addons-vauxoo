# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today OpenERP SA (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.web.http import Controller, route, request
from openerp import SUPERUSER_ID


class DownloadableBrochure(Controller):

    @route([
        '/downloadable/productbrochure/<docids>',
    ], type='http', auth='public', website=True)
    def report_routes(self, docids=None, **data):
        report_obj = request.registry['report']
        cr, context = request.cr, request.context

        if docids:
            docids = [int(i) for i in docids.split(',')]
        reportname = 'website_variants_extra.pprintable'
        pdf = report_obj.get_pdf(cr, SUPERUSER_ID, docids, reportname,
                                 context=context)
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
