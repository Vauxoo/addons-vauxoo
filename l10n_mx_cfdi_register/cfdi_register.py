# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP S.A (<http://www.openerp.com>).
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
from datetime import datetime
import re
from openerp.tools.translate import _
import time

class cfdi_register(osv.TransientModel):
    """ Create new issues through the "contact us" form """
    _name = 'cfdi.register'
    _inherit = 'project.issue'


    def _get_domain_contracts(self, cr, uid,context=None):
        context = context or {}
        uid = context.get('uid', False) or uid
        partner = self.pool.get('res.users').read(cr, uid, uid, ['partner_id'],
                context)['partner_id']
        cont_ids = self.pool.get('account.analytic.account').search(cr, uid,
                [('date','!=',False), ('partner_id','=',partner[0])], context=context)
        result = []
        if len(cont_ids) > 0:
            res = self.pool.get('account.analytic.account').read(cr, uid, cont_ids,
                ['id','vx_contract_code','date_start','date'], context=context)
            for list in res:
                name_contract = list.get('vx_contract_code', '') + ' [' + list['date_start']+ ' / ' + \
                list['date']+ ']' 
                result.append((list['id'],name_contract))
        return result 

    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        res = super(cfdi_register, self).default_get(cr, uid, fields, context=context)
        user_brw = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        admin_brw = self.pool.get('res.users').browse(cr, uid, SUPERUSER_ID, context=context)
        country_name = ''
        if res.get('country_id', False):
            country_name = self.pool.get('res.country').browse(cr, uid, res.get('country_id'),
                                                              context=context).name
        state_name = ''
        if res.get('state_id', False):
            state_name = self.pool.get('res.country.state').browse(cr, uid, res.get('state_id'),
                                                              context=context).name
            
            
        partner_brw = user_brw.partner_id
        model_ids = self.search(cr, uid, ['|', ('vat', '=', partner_brw.vat),
                                               ('email_from', '=', partner_brw.email)],
                                context=context)
        if context.get('fromview', False):
            a = '''
<head>                                                                                              
    <body>                                                                                          
        <div style="position:relative;">                                                            
            <table style="text-align:center;">                               
                <tr>                                                                                                                                                                                                                   
            <td style="right:12px; position:absolute;">'''+time.strftime('%d-%m-%Y')+u'''</td>                           
                </tr>                                                                               
                <tr style="height:100px;">                                                          
        <td style="border-top: 30px solid transparent;" >Vauxoo SA de CV</td>                                                            
                </tr>                                                                               
                <tr>                                                                                
                    <td style="text-align:center; max-width: 100%; word-wrap: break-word; 
                        ">Asunto: Manifestación de Conocimiento y                 
                        Autorización de entrega de CFDI para que                                    
                        Vauxoo SA de CV, entregue al SAT, copia de                                       
                        los comprobantes certificados. </td>                                        
                    </tr>                                                                           
                <tr style="margin-bottom: 100px;">                                                  
                    <td style="border-top: 80px solid transparent;text-align:center; max-width: 80%; word-wrap: break-word;">
                       '''+res.get('company_name', '')+u''' con registro federal de contribuyentes
                       '''+res.get('vat', '')+u''' y con domicilio fiscal en '''+res.get('street',
                               '')+u'''
                   , CP '''+res.get('zip', '')+u', '+res.get('locality', '')+ ', '+state_name+u''', 
                   '''+country_name+u''', con la finalidad de que la presente sirva como constancia de lo
                        previsto en la regla I.2.7.2.1 de la Resolución Miscelánea Fiscal en vigor manifiesto que:
            </td>                                                                                   
                    </tr>                                                                           
                <tr >                                                                               
                    <td style=" border-top: 20px solid transparent;text-align:center; max-width: 80%; word-wrap: break-word;">
                        1. Haré uso de los servicios de Vauxoo SA de CV
                        para la certificación de Comprobantes Fiscales Digitales a través de Internet.                                             
            </td>                                                                                   
                    </tr>                                                                           
                <tr >                                                                               
                    <td style=" border-bottom: 30px solid transparent;border-top: 10px solid transparent;text-align:center; max-width: 80%; word-wrap: break-word;">
                         2. Tengo conocimiento y autorizo a Vauxoo SA de CV para que entregue al        
                         Servicio de                                                                
                                                                                                    
                         Administración Tributaria, copia de los comprobantes fiscales que haya     
                         certificado a mí                                                           
                                                                                                    
                         persona en dicho servicio.                                                 
            </td>                                                                                   
                    </tr>                                                                           
            </table>                                                                                
        </div>                                                                                      
    </body>                                                                                         
</head>      
'''
            a = a.encode('utf-8', 'ignore')
            res.update({'term_conditions':a})
        
       # if model_ids:
       #     raise osv.except_osv(('Error'), ("""You have a server created"""))
       #     return self.read(cr, uid, model_ids[0], [], context=context)
            
        return res

    
    _columns = {

        'name':fields.selection(_get_domain_contracts, 'Contract Codes',
                                help="""Contract Codes"""), 
        'company_name':fields.char('Name', 255, help='Company Name'), 
        'accept':fields.boolean('I accept the terms and conditions',
                                help='Select if you accept the terms and conditions to continue '
                                     'the register'), 
        
        'vat':fields.char('RFC', 32, help='Your Company RFC to do commercial operation'), 
        'term_conditions':fields.html("Terms and Conditions", help="You need agree with the terms "
                                                                   "and condition to continue "
                                                                   "with the register for create "
                                                                   "your test instance"),
        'zip':fields.char('ZIP', 24, help='ZIP code for your city'), 
        'email_from':fields.char('Email', 255, help='Email to receive information'), 
        'phone':fields.char('Phone Number', 255, help='Phone Number'), 
        'street':fields.char('Street', 128, help='Street of your company address'), 
        'city':fields.char('City', 128, help='City of your company address'), 
        'locality':fields.char('Locality', 128, help='Locality of your company address'), 
        'country_id':fields.many2one('res.country', 'Country',
                                     help='Country of your company address'), 
        'state_id':fields.many2one('res.country.state', 'State',
                                   help='State of your company address'), 
        'process_ids': fields.many2many('process.process', string='Companies', readonly=True),
        'cif_file':fields.binary("CIF", help="Fiscal identification card"),
        'certificate_file':fields.binary("Certificate File",
                                         help="The .cer file that was given by the SAT"),
        'certificate_file_pem':fields.binary("Certificate File PEM",
                                             help="This file is generated with the .cer file"),
        'certificate_key_file':fields.binary("Certificate Key File",
                                             help="The .key file that was given by the SAT"),
        'certificate_key_file_pem':fields.binary("Certificate Key File",
                                                 help="This file is generated with the .cer file"),
        'password_sat':fields.char('Certificate Password', 64,
                                   help='This is the password was given by SAT'), 
        'serial_number':fields.char('Serial Number', 64,
                                    help='Number of serie of the certificate'), 
        'date_start':fields.date('Date Start', help='Date start the certificate before the SAT'), 
        'date_end':fields.date('Date End', help='Date end of validity of the certificate'), 
        
    }

#    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False,
#            submenu=False):
#        if context.get('fromview') and len(self._get_domain_contracts(cr, uid,context=context)) == 0:
#            mod_obj = self.pool.get('ir.model.data') 
#            model, view_id = mod_obj.get_object_reference(cr, uid, 'contpaq_openerp_vauxoo',
#                'wizard_contact_form_view_nocontract')
#        return super(cfdi_register, self).fields_view_get(cr, uid, view_id=view_id,
#                view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

    def _get_process(self, cr, uid, context=None):
        """
        Fetch companies in order to display them in the wizard view

        @return a list of ids of the companies
        """
        r = self.pool.get('process.process').search(cr, SUPERUSER_ID, [], context=context)
        return r

    def _get_user_name(self, cr, uid, context=None):
        """
        If the user is logged in (i.e. not anonymous), get the user's name to
        pre-fill the  field.
        Same goes for the other _get_user_attr methods.

        @return current user's name if the user isn't "anonymous", None otherwise
        """
        user = self.pool.get('res.users').read(cr, uid, uid, ['login'], context)

        if (user['login'] != 'anonymous'):
            return self.pool.get('res.users').name_get(cr, uid, uid, context)[0][1]
        else:
            return ''

    def _get_user_email(self, cr, uid, context=None):
        user = self.pool.get('res.users').read(cr, uid, uid, ['login', 'email'], context)

        if (user['login'] != 'anonymous' and user['email']):
            return user['email']
        else:
            return ''

    def _get_rfc(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        if (user['login'] != 'anonymous' and user.partner_id.vat):
            return user.partner_id.vat
        else:
            return ''

    def _get_street(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        if (user['login'] != 'anonymous' and user.partner_id.street):
            return user.partner_id.street
        else:
            return ''

    def _get_city(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        if (user['login'] != 'anonymous' and user.partner_id.city):
            return user.partner_id.city
        else:
            return ''

    def _get_locality(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        if (user['login'] != 'anonymous' and user.partner_id.l10n_mx_city2):
            return user.partner_id.l10n_mx_city2
        else:
            return ''

    def _get_country(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        if (user['login'] != 'anonymous' and user.partner_id.country_id):
            return user.partner_id.country_id.id
        else:
            return ''

    def _get_state(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)

        if (user['login'] != 'anonymous' and user.partner_id.state_id):
            return user.partner_id.state_id.id
        else:
            return ''

    def _get_user_phone(self, cr, uid, context=None):
        user = self.pool.get('res.users').read(cr, uid, uid, ['login', 'phone'], context)

        if (user['login'] != 'anonymous' and user['phone']):
            return user['phone']
        else:
            return ''

    _defaults = {
        'company_name': _get_user_name,
        'street': _get_street,
        'city': _get_city,
        'locality': _get_locality,
        'country_id': _get_country,
        'state_id': _get_state,
        'vat': _get_rfc,
        'email_from': _get_user_email,
        'phone': _get_user_phone,
        'process_ids': _get_process,
    }

    def create(self, cr, uid, values, context=None):
        sf =  ['city', 'name', 'zip', 'locality', 'country_id', 'phone', 'street', 'company_name',
              'state_id', 'email_from', 'vat']
        context = context or {}
        context.update({'uid':uid})
        r = True
        if set(sf).issubset(values.keys()):
            r = super(cfdi_register,self).create(cr,SUPERUSER_ID,values,context=context)
            cr.commit()
            cr.execute('''
                       UPDATE cfdi_register
                       SET create_uid=%d
                       WHERE id=%d
                       ''' % (uid, r))
        else:
            raise osv.except_osv(('Error'), ("""No Tiene permitido esta operacion"""))
        return r

    def send_emails(self, cr, uid, user_id, res_id, email=None, context=None):                                      
        '''
        Send an email to ask permission to do merge with users that have the same email account
        @param user_id: User id that receives the notification mail
        @param res_id: Id of record created to do merge
        '''
        mail_mail = self.pool.get('mail.mail')                                                      
        partner_obj = self.pool.get('res.partner')                                                      
        user = self.pool.get('res.users').browse(cr, uid, user_id)                                 
        url = partner_obj._get_signup_url_for_action(cr, user.id, [user.partner_id.id],
                action='',
                res_id=res_id, model='cfdi.register', context=context)[user.partner_id.id]

        
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url',
                                                                  default='', context=context)
        if not user.email:                                                                          
            raise osv.except_osv(_('Email Required'), _('The current user must have an email address configured in User Preferences to be able to send outgoing emails.'))
                                                                                                    
        # TODO: also send an HTML version of this mail                                              
        mail_ids = []                                                                               
        email_to = email or user.email                                                    
        subject = user.name                                                              
        body = """
          <html>
          <head>                                                                                              
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />                      
                <title>Binding and Unbinding Events with jQuery</title>                                         
            </head>                                                                                                 
            <body>                                                                                                  
            <div>                                                                                      
                <h1 style="text-align:center;">%s</h1>                                                           
                <div style="font-size:18pt; position:absolute;">                                       
                    <div style="top:10px">%s: %s</div>                                                
                    <div style="top:10px">%s: %s </div>                                                                
                    <div style="top:10px">%s: <a href="%s">%s</a></div>                           
                    <div style="top:10px">%s</div>                                                     
                </div>                                                                                         
            </div>                                                                                     
            </body>                                                                                               
            </html> 
        """ % (_('Merge Proposal'), _('Serve Location'), base_url, _('Data Base'), cr.dbname,
                _('You have a request to join this user if you agree click on the following link'), 
                url, _('Direct Access'), 
                _('If you do not agree ignore this email Contact with your administrator'),)
        mail_ids.append(mail_mail.create(cr, uid, {                                             
                'email_from': user.email,                                                       
                'email_to': email_to,                                                           
                'subject': subject,                                                             
                'body_html':  body}, context=context))                         
        # force direct delivery, as users expect instant notification                               
        mail_mail.send(cr, uid, mail_ids, context=context)                                          
        return True

    def submit(self, cr, uid, ids, context=None):
        """ When the form is submitted, redirect the user to a "Thanks" message """
        context = context or {}
        wz_obj = self.browse(cr, uid, ids[0], context=context)
        if not re.match("[^@]+@[^@]+\.[^@]+", wz_obj.email_from):
            raise osv.except_osv(_('Error'), _("""You need a valid email account"""))

        elif not wz_obj.accept:
            raise osv.except_osv(_('Error'),
                                 _("You need accept the terms and conditions to continue"))

        else:
            self.send_emails(cr, uid, uid, wz_obj.id, wz_obj.email_from, context)

        return True

    def submit2(self, cr, uid, ids, context=None):
        """ When the form is submitted, redirect the user to a "Thanks" message """
        wz_obj = self.browse(cr, uid, ids[0], context=context)
        mod_obj = self.pool.get('ir.model.data')
        
        model, view_id = mod_obj.get_object_reference(cr, uid, 'l10n_mx_cfdi_register',
                                                      'cfdi_register_form_view_readonly')
        if not re.match("[^@]+@[^@]+\.[^@]+", wz_obj.email_from):
            raise osv.except_osv(_('Error'), _("""You need a valid email account"""))

        elif not wz_obj.accept:
            raise osv.except_osv(_('Error'),
                                 _("You need accept the terms and conditions to continue"))

        wz_obj = self.read(cr, SUPERUSER_ID, ids[0], [], context=context)
        wz_obj.pop('partner_id', 'NO')
        wz_obj.update({'name':wz_obj.get('company_name')})
        wz_obj.update({'country_id':wz_obj.get('country_id')[0]})
        wz_obj.update({'state_id':wz_obj.get('state_id')[0]})
        user_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        user_brw = user_obj.browse(cr, SUPERUSER_ID, SUPERUSER_ID, context=context)
        company_id = user_brw.company_id.id
        partner_id = user_brw.company_id.partner_id.id
        menu_obj = self.pool.get('ir.ui.menu')
        data_obj = self.pool.get('ir.model.data')
        company_obj = self.pool.get('res.company')
        menu_id = data_obj.get_object_reference(cr, SUPERUSER_ID,
                'l10n_mx_cfdi_register', 'company_cfdi_register')
        group_id = data_obj.get_object_reference(cr, SUPERUSER_ID,
                'base', 'group_no_one')
        
        partner_obj.write(cr, SUPERUSER_ID, partner_id,
                          {
                           'vat':wz_obj.get('vat') ,
                           'regimen_fiscal_id':1,
                           'type':'invoice',
                              }  
                         )
        wz_obj.update({'address_invoice_parent_company_id':partner_id})
        company_obj.write(cr, SUPERUSER_ID, company_id,
                wz_obj
                         )
        menu_obj.write(cr, SUPERUSER_ID, menu_id[1],
                        {'groups_id':[(6, 0, [group_id[1]])]},
                        context=context)

        return {
                'type': 'ir.actions.act_window',
                'res_id': ids[0],
                'target': 'inline',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                }

    def storage_cfdi(self, cr, uid, ids, context=None):
        wz_obj = self.browse(cr, SUPERUSER_ID, ids[0], context=context)
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        res = certificate_obj.onchange_certificate_info(cr, SUPERUSER_ID, ids,
                                                        wz_obj.certificate_file,                                  
                                                        wz_obj.certificate_key_file,                                  
                                                        wz_obj.password_sat,                                  
                                                        context=context)
        res = res.get('value')
        res.update({
            'certificate_file':wz_obj.certificate_file, 
            'certificate_key_file':wz_obj.certificate_key_file, 
            'certificate_password':wz_obj.password_sat, 
            
            })
        certificate_obj.create(cr, SUPERUSER_ID, res, context=context)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    def _needaction_domain_get(self, cr, uid, context=None):
        """
        This model doesn't need the needactions mechanism inherited from
        crm_lead, so simply override the method to return an empty domain
        and, therefore, 0 needactions.
        """
        return False
    def onchange_certificate(self, cr, uid, ids, cer_der_b64str, key_der_b64str, password,
                             context=None):
        context = context or {}
        facturae_obj = self.pool.get('res.company.facturae.certificate')
        if cer_der_b64str and key_der_b64str and password:
            res = facturae_obj.onchange_certificate_info(cr, uid, ids, cer_der_b64str,                                  
                                                     key_der_b64str, password, context=context)
        else:
            res = {'value':{}}

        return res
        
    def onchange_fill_terms(self, cr, uid, ids, company_name, vat, country, state, street,
                            city, locality, zip, context=None):
        context = context or {}
        company_name = company_name or ''
        vat = vat or ''
        street = street or ''
        city = city or ''
        locality = locality or ''
        zip = zip or ''
        admin_brw = self.pool.get('res.users').browse(cr, uid, SUPERUSER_ID, context=context)
        country_name = ''
        if country:
            country_name = self.pool.get('res.country').browse(cr, uid, country,
                                                              context=context).name
        state_name = ''
        if state:
            state_name = self.pool.get('res.country.state').browse(cr, uid, state,
                                                              context=context).name
            
        a = '''
<head>                                                                                              
    <body>                                                                                          
        <div style="position:relative;">                                                            
            <table style="text-align:center;">                               
                <tr>                                                                                                                                                                                                                   
            <td style="right:12px; position:absolute;">'''+time.strftime('%d-%m-%Y')+u'''</td>                           
                </tr>                                                                               
                <tr style="height:100px;">                                                          
        <td style="border-top: 30px solid transparent;" >Vauxoo SA de CV</td>                                                            
                </tr>                                                                               
                <tr>                                                                                
                    <td style="text-align:center; max-width: 100%; word-wrap: break-word;                     
                        position:absolute;">Asunto: Manifestación de Conocimiento y                 
                        Autorización de entrega de CFDI para que                                    
                        Vauxoo SA de CV, entregue al SAT, copia de                                       
                        los comprobantes certificados. </td>                                        
                    </tr>                                                                           
                <tr style="margin-bottom: 100px;">                                                  
                    <td style="border-top: 80px solid transparent;text-align:center; max-width: 80%; word-wrap: break-word;">
                       '''+company_name+u''' con registro federal de contribuyentes
                       '''+vat +u''' y con domicilio fiscal en '''+street+u'''
                   , CP '''+zip+u', '+locality + ', '+state_name+u''', 
                   '''+country_name+u''', con la finalidad de que la presente sirva como constancia de lo
                        previsto en la regla I.2.7.2.1 de la Resolución Miscelánea Fiscal en vigor manifiesto que:
            </td>                                                                                   
                    </tr>                                                                           
                <tr >                                                                               
                    <td style=" border-top: 20px solid transparent;text-align:center; max-width: 80%; word-wrap: break-word;">
                        1. Haré uso de los servicios de Vauxoo SA de CV
                        para la certificación de Comprobantes Fiscales Digitales a través de Internet.                                             
            </td>                                                                                   
                    </tr>                                                                           
                <tr >                                                                               
                    <td style=" border-bottom: 30px solid transparent;border-top: 10px solid transparent;text-align:center; max-width: 80%; word-wrap: break-word;">
                         2. Tengo conocimiento y autorizo a Vauxoo SA de CV para que entregue al        
                         Servicio de                                                                
                                                                                                    
                         Administración Tributaria, copia de los comprobantes fiscales que haya     
                         certificado a mí                                                           
                                                                                                    
                         persona en dicho servicio.                                                 
            </td>                                                                                   
                    </tr>                                                                           
            </table>                                                                                
        </div>                                                                                      
    </body>                                                                                         
</head>      
'''
        a = a.encode('utf-8', 'ignore')
        res = {'value':{'term_conditions':a}}
    
        return res
    
