# -*- coding: utf-8 -*-
import cStringIO
import contextlib
import hashlib
import json
from openerp import SUPERUSER_ID
import logging
import os
import datetime

from sys import maxint
import base64

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
from urllib import quote_plus


logger = logging.getLogger(__name__)

NOPE = object()
# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
class crm_captcha(http.Controller):

    def generate_google_map_url(self, street, city, city_zip, country_name):
        url = "http://maps.googleapis.com/maps/api/staticmap?center=%s&sensor=false&zoom=8&size=298x298" % quote_plus(
            '%s, %s %s, %s' % (street, city, city_zip, country_name)
        )
        return url

    @website.route(['/crm/contactus'], type='http', auth="admin", multilang=True)
    def contactus(self, *arg, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        required_fields = ['contact_name', 'email_from', 'description']
        orm_country = registry.get('res.country')                              
        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)  
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context) 
        state_orm = registry.get('res.country.state')                          
        states_ids = state_orm.search(cr, SUPERUSER_ID, [], context=context)
        states = state_orm.browse(cr, SUPERUSER_ID, states_ids, context)
        post['user_id'] = False
        error = set()
        values =  post
        values['error'] = error
        captcha_obj = registry.get('res.captcha')                              
        captcha_str = '%s,%s' % (str(post.get('recaptcha_challenge_field', '')),
                                 str(post.get('recaptcha_response_field', ''))) 
        captcha_valid = captcha_obj._valid_captcha(cr, uid, captcha_str, context=context)
        values.update({                                                             
            'countries': countries,                                            
            'states': states,                                                  
        })

        # fields validation
        for field in required_fields:
            if not post.get(field):
                error.add(field)
        if error:
            return request.website.render("website.contactus", values)
        elif not captcha_valid:
            values.update({                                                             
                'checkout': {'state_id': int(post.get('state_id', 0)),
                             'country_id': int(post.get('country_id', 0))}
            })
            values['error'] = 'captcha'
            return request.website.render("website.contactus", values)

        # if not given: subject is contact name
        if not post.get('name'):
            post['name'] = post.get('contact_name')

        request.registry['crm.lead'].create(request.cr, request.uid,
                                            post, request.context)
        company = request.website.company_id
        values = {
            'google_map_url': self.generate_google_map_url(company.street, company.city, company.zip, company.country_id and company.country_id.name_get()[0][1] or '')
        }
        return request.website.render("website_crm.contactus_thanks", values)
    @website.route(['/website/get_public_id'], type='json', auth="public")
    def get_public_id(self, object):
        _object = request.registry[object]
        obj = _object.browse(request.cr, request.uid, request.uid)
        res_id = obj.company_id and obj.company_id.recaptcha_id

        return res_id

    @website.route(['/page/website.contactus'], type='http', auth="public", multilang=True)
    def checkout(self, **post):                                                
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
                                                                               
        # must have a draft sale order with lines at this point, otherwise reset
                                                                               
        orm_partner = registry.get('res.partner')                              
        orm_user = registry.get('res.users')                                   
        orm_country = registry.get('res.country')                              
        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)  
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context) 
        state_orm = registry.get('res.country.state')                          
        states_ids = state_orm.search(cr, SUPERUSER_ID, [], context=context)
        states = state_orm.browse(cr, SUPERUSER_ID, states_ids, context)
                                                                               
        values = {                                                             
            'countries': countries,                                            
            'states': states,                                                  
            'checkout': {},                                          
            'error': {},                                                       
        }                                                                      
        checkout = values['checkout']                                          
        error = values['error']                                                
                                                                               
        return request.website.render("website.contactus", values) 


