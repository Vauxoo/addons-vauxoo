
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

try:
    from recaptcha.client import captcha
except ImportError, e:
    _logger.error("You must install recaptcha to use the recaptcha module")


class res_captcha(osv.Model):
    '''
    For security reasons, we can not allow have access to private key trought
    any objets, due to this we create an extra model to manage both keys
    per company, and with functional fields we can set the keys to the object
    that we need open to portal.
    '''
    _name = 'res.captcha'
    _rec_name = 'company_id'
    _description = 'Captcha Object'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',
                                      help="Company that will use those captcha key"),
        'recaptcha_key': fields.char('Recaptcha Public Key', size=64,
                                     required=True,
                                     help='Public key generated on http://code.google.com/recaptcha'),
        'recaptcha_private_key': fields.char('Recaptcha Private Key', size=64,
                                             required=True,
                                             help='Private key generated on http://code.google.com/recaptcha'),
    }

    def _get_private_key(self, cr, uid, context=None):
        '''
        In order to use a global method.
        This method is to return the private key for tha main company,
        until now this key is global to main company.
        '''
        if context is None:
            context = {}
        captcha_obj = self.pool.get('res.captcha')
        captcha_ids = captcha_obj.search(cr, SUPERUSER_ID,
                                         [('company_id', '=', 1)], context=context)
        if captcha_ids:
            private_key = captcha_obj.browse(cr, SUPERUSER_ID, captcha_ids[0],
                                             context=context)
        return private_key.recaptcha_private_key

    def _valid_captcha(self, cr, uid, capt, context=None):
        '''
        One time you have the captcha field in your model
        just use this methos to wrap the captcha stuff and avoid import
        the captcha lib in every single model you use it.
        just pass the captcha pair:

        :capt: is a text with the pair CAPTCHACHALLENGIMAGE,response

        Where CAPTCHACHALLENGEIMAGE is the image on the field (the widget build
        this pair for you) and "response" is the answer to the challenge.
        '''
        r = capt.split(',')
        print r
        response = captcha.submit(
            r[0], r[1],
            self._get_private_key(cr, uid, context=context),
            "agrinos.local")
        if response.is_valid:
            return True
        return False
