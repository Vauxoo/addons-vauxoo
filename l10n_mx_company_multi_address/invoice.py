# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_address_issued_invoice(self, cr, uid, ids, name, args, context=None):
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(cr, uid, journal_id, context=context)
            a = data_journal.address_invoice_company_id and data_journal.address_invoice_company_id.id or False
            b = data_journal.company2_id and data_journal.company2_id.address_invoice_parent_company_id and data_journal.company2_id.address_invoice_parent_company_id.id or False
            c = data.company_id and data.company_id.address_invoice_parent_company_id and data.company_id.address_invoice_parent_company_id.id or False
            address_invoice = a or b or c or False
            res[data.id] = address_invoice
        return res

    def _get_company_emitter_invoice(self, cr, uid, ids, name, args, context=None):
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(cr, uid, journal_id, context=context)
            company_invoice = data_journal.company2_id and data_journal.company2_id.id or data.company_id and data.company_id.id or False
            res[data.id] = company_invoice
        return res
        
    _columns = {
        'address_issued_id' : fields.function(_get_address_issued_invoice, type="many2one", relation='res.partner', string='Address Issued Invoice', help='This address will be used as address that issued for electronic invoice'),
        'company_emitter_id' : fields.function(_get_company_emitter_invoice, type="many2one", relation='res.company', string='Company Emitter Invoice', help='This company will be used as emitter company in the electronic invoice')
    }
            
    def ____________________________get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        invoice_data_parents = super(account_invoice,self)._get_facturae_invoice_dict_data(cr,uid,ids,context)
        invoice = self.browse(cr, uid, ids)[0]
        invoice_data_parents[0]['Comprobante']['Emisor'] = {'rfc': (invoice.company_id.partner_id._columns.has_key('vat_split') and invoice.company_id.partner_id.vat_split or invoice.company_id.partner_id.vat or '').replace('-', ' ').replace(' ',''),'nombre': invoice.company_id.address_invoice_parent_company_id.name or '' }
        invoice_data_parents[0]['Comprobante']['Emisor']['DomicilioFiscal'] = {'calle': invoice.company_id.address_invoice_parent_company_id.street and invoice.company_id.address_invoice_parent_company_id.street.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                                'noExterior': invoice.company_id.address_invoice_parent_company_id.l10n_mx_street3 and invoice.company_id.address_invoice_parent_company_id.l10n_mx_street3.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                                'noInterior': invoice.company_id.address_invoice_parent_company_id.l10n_mx_street4 and invoice.company_id.address_invoice_parent_company_id.l10n_mx_street4.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                                'colonia': invoice.company_id.address_invoice_parent_company_id.street2 and invoice.company_id.address_invoice_parent_company_id.street2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                                'localidad': invoice.company_id.address_invoice_parent_company_id.l10n_mx_city2 and invoice.company_id.address_invoice_parent_company_id.l10n_mx_city2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                                'municipio': invoice.company_id.address_invoice_parent_company_id.city and invoice.company_id.address_invoice_parent_company_id.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                                'estado': invoice.company_id.address_invoice_parent_company_id.state_id and invoice.company_id.address_invoice_parent_company_id.state_id.name and invoice.company_id.address_invoice_parent_company_id.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                                'pais': invoice.company_id.address_invoice_parent_company_id.country_id and invoice.company_id.address_invoice_parent_company_id.country_id.name and invoice.company_id.address_invoice_parent_company_id.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')or '',
                                                                                'codigoPostal': invoice.company_id.address_invoice_parent_company_id.zip and invoice.company_id.address_invoice_parent_company_id.zip.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
        }
        
        invoice_data_parents[0]['Comprobante']['Emisor']['ExpedidoEn'] = {'calle': invoice.address_invoice_company_id.street and invoice.address_invoice_company_id.street.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                            'noExterior': invoice.address_invoice_company_id.l10n_mx_street3 and invoice.address_invoice_company_id.l10n_mx_street3.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                            'noInterior': invoice.address_invoice_company_id.l10n_mx_street4 and invoice.address_invoice_company_id.l10n_mx_street4.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                            'colonia': invoice.address_invoice_company_id.street2 and invoice.address_invoice_company_id.street2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                            'localidad': invoice.address_invoice_company_id.l10n_mx_city2 and invoice.address_invoice_company_id.l10n_mx_city2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                                                                            'municipio': invoice.address_invoice_company_id.city and invoice.address_invoice_company_id.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                            'estado': invoice.address_invoice_company_id.state_id and invoice.address_invoice_company_id.state_id.name and invoice.address_invoice_company_id.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                            'pais': invoice.address_invoice_company_id.country_id and invoice.address_invoice_company_id.country_id.name and invoice.address_invoice_company_id.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')or '',
                                                                            'codigoPostal': invoice.address_invoice_company_id.zip and invoice.address_invoice_company_id.zip.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                                                                        }
        invoice_data_parents[0]['Comprobante']['Emisor']['RegimenFiscal'] = {'Regimen':invoice.company_id.partner_id.regimen_fiscal_id.name or ''}
        
        city = invoice.address_invoice_company_id.city and invoice.address_invoice_company_id.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or False
        state = invoice.address_invoice_company_id.state_id and invoice.address_invoice_company_id.state_id.name and invoice.address_invoice_company_id.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or False
        country = invoice.address_invoice_company_id.country_id and invoice.address_invoice_company_id.country_id.name and invoice.address_invoice_company_id.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or False
        if city and state and country:
            address = city +', '+ state +', '+ country
        else:
            raise osv.except_osv(('Domicilio Incompleto!'),('Verifique que el domicilio de la compañia emisora del comprobante fiscal este completo (Ciudad - Estado - Pais)'))
        
        invoice_data_parents[0]['Comprobante']['LugarExpedicion'] = address
        return invoice_data_parents

    def onchange_journal_id(self, cr, uid, ids, journal_id=False):
        result = super(account_invoice,self).onchange_journal_id(cr,uid,ids,journal_id)
        address_id = journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id) or False
        if address_id and address_id.address_invoice_company_id:
            result['value'].update({'address_invoice_company_id': address_id.address_invoice_company_id.id})
        if address_id and address_id.company2_id:
            result['value'].update({'company2_id': address_id.company2_id.id})
        return result
        
account_invoice()
