# -*- coding: utf-8 -*-
import cStringIO
import contextlib
import hashlib
import json
import logging
import os
import datetime

from sys import maxint

import psycopg2
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
from PIL import Image

import openerp
from openerp.osv import fields
from openerp.addons.website.models import website
from openerp.addons.web import http
from openerp.addons.web.http import request


logger = logging.getLogger(__name__)

NOPE = object()
# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
class crm_captcha(http.Controller):
    @website.route(['/website/get_public_id'], type='json', auth="public")
    def get_public_id(self, object):
        _object = request.registry[object]
        obj = _object.browse(request.cr, request.uid, request.uid)
        res_id = obj.company_id and obj.company_id.recaptcha_id

        return res_id


