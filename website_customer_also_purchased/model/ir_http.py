# coding: utf-8
from openerp import models
from openerp.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        cookie_sort = request.httprequest.cookies.get('cap_sort', False)
        resp = super(IrHttp, self)._dispatch()
        if request.registry:
            current_website = request.registry['website'].get_current_website(
                request.cr, request.uid, context=request.context)
            if cookie_sort == "False" and request.website_enabled:
                resp.set_cookie('cap_sort',
                                bytes(current_website.cap_sort))
        return resp
