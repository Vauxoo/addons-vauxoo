# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna (julio@vauxoo.com)
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

class configure_account_partner(osv.TransientModel):
    _name = 'configure.account.partner'
    _columns = {
        'name' : fields.many2one('account.account', 'Accounts Payable',
            domain="[('type', '=', 'payable'),\
            ('company_id', '=', company_id)]",
            help="Account of payable type which will set in partners "
                 "selected previously"),
        'account_receivable': fields.many2one('account.account',
            'Accounts Receivable',
            domain="[('type', '=', 'receivable'),\
            ('company_id', '=', company_id)]",
            help="Account of receivable type which will set in partners "
                 "selected previously"),
        'company_id': fields.many2one('res.company', 'Company',
                                     help="Company used to define account by "
                                          "company and set in the partners "
                                          "selected"),
        'webkit_partner': fields.boolean(
            'Configure Property Webkit And Partner',
            help='Check this field to configure '\
                'partner and webkit, if not only configures webkit'),
        'partner_ids': fields.many2many('res.partner', 'configure_partner_rel',
            'wiz_id', 'partner_id', 'Partners',
            help="Select partners to set receivable account for company "
                 "selected ")
    }

    _defaults = {
        'company_id': lambda s,cr,uid,c:\
            s.pool.get('res.company')._company_default_get(cr, uid,
                                    'configure.account.partner', context=c),
    }
    
    def create_or_modified(self, cr, uid ,ids, form, context=None):
        ir_property_obj = self.pool.get('ir.property')
        ir_model_fields_obj = self.pool.get('ir.model.fields')
        
        payable_ids = ir_model_fields_obj.search(cr, uid, [
            ('name', '=', 'property_account_payable'),
            ('model', '=', 'res.partner')])
        
        receivable_ids = ir_model_fields_obj.search(cr, uid, [
            ('name', '=', 'property_account_receivable'),
            ('model', '=', 'res.partner')])
            
        ir_property_receivable_ids = ir_property_obj.search(cr, uid, [
                ('fields_id', '=', receivable_ids and\
                                    receivable_ids[0] or None),
                ('company_id', '=', form.company_id.id)])

        ir_property_payable_ids = ir_property_obj.search(cr, uid, [
                ('fields_id', '=', payable_ids and\
                                    payable_ids[0] or None),
                ('company_id', '=', form.company_id.id)])
                
        if ir_property_receivable_ids:
            ir_property_obj.write(cr, uid, ir_property_receivable_ids,
                {'value_reference': 'account.account,%s'
                                            %form.account_receivable.id})
#        if ir_property_payable_ids:
 #           ir_property_obj.write(cr, uid, ir_property_payable_ids,
  #              {'value_reference': 'account.account,%s'%form.name.id})
        return True
    
    def webkit_property(self, cr, uid, ids, form, context=None):
        ir_property_obj = self.pool.get('ir.property')
        ir_model_fields_obj = self.pool.get('ir.model.fields')
        
        webkit_ids = ir_model_fields_obj.search(cr, uid, [
            ('name', '=', 'webkit_header'),
            ('model', '=', 'ir.actions.report.xml')])

        webkit_header_ids = ir_property_obj.search(cr, uid, [
                ('fields_id', '=', webkit_ids and webkit_ids[0] or None),
                ('company_id', '=', form.company_id.id)])

        if webkit_header_ids:
            ir_property_obj.write(cr, uid, webkit_header_ids,
                {'company_id': None})
        return True
    
    def conf_accounts(self, cr, uid, ids, context=None):
        res_partner_obj = self.pool.get('res.partner')
        form = self.browse(cr, uid, ids, context=context)[0]
        if form.webkit_partner:
            res_partner_obj.write(cr, uid,
                [partner.id for partner in form.partner_ids],
                {
                #'property_account_payable':form.name.id,
                'property_account_receivable': form.account_receivable.id})
            self.create_or_modified(cr, uid, ids, form, context=context)
        self.webkit_property(cr, uid, ids, form, context=context)

        return True
