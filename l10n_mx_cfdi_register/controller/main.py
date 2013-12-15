import functools
import logging
import simplejson
import werkzeug.utils
from werkzeug.exceptions import BadRequest
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.controllers.main import db_monodb, set_cookie_and_redirect, login_and_redirect
from openerp.modules.registry import RegistryManager

openerpweb = http


#----------------------------------------------------------
# Controller
#----------------------------------------------------------
class Main(openerpweb.Controller):
    _cp_path = '/create_instance'


    @openerpweb.httprequest
    def execute_create(self, req, server_action=None, db=None, **kw):
       # url = '?db=%s&login=%s&record=%s#action=%s' % (db, kw.get('login'),
       #                                                kw.get('record'),
       #                                                kw.get('action'))
       # req.context.update({'prueba':'otra'})
       # path = req.httprequest.url.split('/do_merge')
        url = ''
        return set_cookie_and_redirect(req, url)

    @openerpweb.httprequest
    def apply_merge(self, req, server_action=None, db=None, **kw):
        print 30*'algooooooooo'
        dbname = db
        context = {}
        context.update(kw)
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            u = registry.get('merge.user.for.login')
            credentials = u.execute_merge(cr, SUPERUSER_ID, [1], context)
            cr.commit()
        #return set_cookie_and_redirect(req, url)
        return 'WTF'
