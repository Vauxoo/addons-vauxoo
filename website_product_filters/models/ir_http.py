# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Coded by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models
from openerp.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        cookie_sort = request.httprequest.cookies.get('default_sort', False)
        resp = super(IrHttp, self)._dispatch()
        if request.registry:
            current_website = request.registry['website'].get_current_website(
                request.cr, request.uid, context=request.context)
            post_sort = request.params.get('product_sorter', False)
            if not cookie_sort and request.website_enabled and not post_sort:
                resp.set_cookie('default_sort',
                                bytes(current_website.default_sort))
            elif post_sort:
                resp.set_cookie('default_sort', post_sort)
        return resp
