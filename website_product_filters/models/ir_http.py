from openerp import models
from openerp.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        cookie_sort = request.httprequest.cookies.get('default_sort')
        resp = super(IrHttp, self)._dispatch()
        current_website = request.registry['website'].get_current_website(
            request.cr, request.uid, context=request.context)
        print current_website, current_website.default_sort
        if request.website_enabled and cookie_sort and cookie_sort != current_website.default_sort:
            resp.set_cookie('default_sort', 'rating')
        return resp
