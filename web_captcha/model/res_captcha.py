
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
            required = True,
            help='Public key generated on http://code.google.com/recaptcha'), 
        'recaptcha_private_key': fields.char('Recaptcha Private Key', size=64,
            required = True,
            help='Private key generated on http://code.google.com/recaptcha'), 
    }
