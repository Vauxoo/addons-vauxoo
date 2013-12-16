# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from openerp import tools
from openerp import tests
from openerp.osv import osv
from openerp import netsvc
import openerp
from report_webkit import webkit_report
import datetime

class invoice_facturae_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(invoice_facturae_html, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'set_global_data': self._set_global_data,
            'facturae_data_dict': self._facturae_data_dict,
            'split_string': self._split_string,
            'company_address': self._company_address,
            'subcompany_address': self._subcompany_address,
            'get_invoice_sequence': self._get_invoice_sequence,
            'get_approval': self._get_approval,
            'get_taxes': self._get_taxes,
            'get_taxes_ret': self._get_taxes_ret,
            'float': float,
            'exists_key': self._exists_key,
            'get_data_partner': self._get_data_partner,
            'get_sum_total': self._get_sum_total,
            'has_disc': self._has_disc,
            'get_data_certificate': self._get_data_certificate,
            'get_text_promissory' : self._get_text_promissory,
        })
        self.taxes = []

    def _exists_key(self, key):
        return key in self.invoice._columns

    def _set_global_data(self, o):
        try:
            self._get_data_partner(o.partner_id)
        except Exception, e:
            print "exception: %s" % (e)
            pass
        try:
            self.setLang(o.partner_id.lang)
        except Exception, e:
            print "exception: %s" % (e)
            pass
        try:
            self._get_company_address(o.id)
        except Exception, e:
            print "exception: %s" % (e)
            pass
        try:
            self._get_facturae_data_dict(o)
        except Exception, e:
            print "exception: %s" % (e)
            pass
        try:
            self._get_data_certificate(o.id)
        except Exception, e:
            print "exception: %s" % (e)
            pass
        return ""

    def _get_approval(self):
        return self.approval

    def _get_invoice_sequence(self):
        return self.sequence

    def _set_invoice_sequence_and_approval(self, invoice_id):
        context = {}
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        sequence_obj = pool.get('ir.sequence')
        invoice = invoice_obj.browse(self.cr, self.uid, [
                                     invoice_id], context=context)[0]
        context.update({'number_work': invoice.number})
        sequence = invoice.invoice_sequence_id or False
        sequence_id = sequence and sequence.id or False
        self.sequence = sequence
        approval = sequence and sequence.approval_id or False
        approval_id = approval and approval.id or False
        self.approval = approval
        return sequence, approval

    def _get_taxes(self):
        return self.taxes

    def _get_taxes_ret(self):
        try:
            return self.taxes_ret
        except:
            pass
        return []

    def _split_string(self, string, length=100):
        if string:
            for i in range(0, len(string), length):
                string = string[:i] + ' ' + string[i:]
        return string

    def _get_company_address(self, invoice_id):
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        partner_obj = pool.get('res.partner')
        address_obj = pool.get('res.partner')
        invoice = invoice_obj.browse(self.cr, self.uid, invoice_id)
        partner_id = invoice.company_id.parent_id and invoice.company_id.\
            parent_id.partner_id.id or invoice.company_id.partner_id.id
        self.invoice = invoice
        address_id = partner_obj.address_get(
            self.cr, self.uid, [partner_id], ['invoice'])['invoice']
        self.company_address_invoice = address_obj.browse(
            self.cr, self.uid, partner_id)

        subpartner_id = invoice.company_id.partner_id.id
        if partner_id == subpartner_id:
            self.subcompany_address_invoice = self.company_address_invoice
        else:
            subaddress_id = partner_obj.address_get(
                self.cr, self.uid, [subpartner_id], ['invoice'])['invoice']
            self.subcompany_address_invoice = address_obj.browse(
                self.cr, self.uid, subaddress_id)
        return ""

    def _company_address(self):
        return self.company_address_invoice

    def _subcompany_address(self):
        return self.subcompany_address_invoice

    def _facturae_data_dict(self):
        return self.invoice_data_dict

    def _get_facturae_data_dict(self, invoice):
        self._set_invoice_sequence_and_approval(invoice.id)
        self.taxes = [
            tax for tax in invoice.tax_line if tax.tax_percent >= 0.0]
        self.taxes_ret = [
            tax for tax in invoice.tax_line if tax.tax_percent < 0.0]
        return ""

    def _get_data_partner(self, partner_id):
        address_invoice = ''
        partner_obj = self.pool.get('res.partner')
        res = {}
        address_invoice = partner_obj.browse(self.cr, self.uid, partner_id.id)
        id_parent = partner_id.commercial_partner_id.id
        address_parent = partner_obj.browse(self.cr, self.uid, id_parent)
        if address_invoice:
            res.update({
                'name' : address_parent.name or False,
                'vat' : address_parent._columns.has_key('vat_split') \
                    and address_parent.vat_split or address_parent.vat or False,
                'street' : address_invoice.street or False,
                'l10n_mx_street3' : address_invoice.l10n_mx_street3 or False,
                'l10n_mx_street4' : address_invoice.l10n_mx_street4 or False,
                'street2' : address_invoice.street2 or False,
                'city' : address_invoice.city or False,
                'state' : address_invoice.state_id and \
                    address_invoice.state_id.name or False,
                'country' : address_invoice.country_id and\
                    address_invoice.country_id.name or False,
                'l10n_mx_city2' : address_invoice.l10n_mx_city2 or False,
                'zip' : address_invoice.zip or False,
                'phone' : address_invoice.phone or False,
                'fax' : address_invoice.fax or False,
                'mobile' : address_invoice.mobile or False,
            })
            if not res['vat']:
                raise openerp.exceptions.Warning(
                    'Invoice Address Type Not Vat')
                # print "Invoice Address Type Not Vat"
        else:
            # print "Customer Address Not Invoice Type"
            raise openerp.exceptions.Warning(
                'Customer Address Not Invoice Type')
        return res

    def _get_sum_total(self, line_ids):
        suma = 0.0
        for line in line_ids:
            suma += (line.price_unit or 0.0) * (line.quantity or 0.0)
        return suma

    def _has_disc(self, lines):
        discount = False
        for line in lines:
            if line.discount > 0.0:
                discount = True
                break
        return discount

    def _get_data_certificate(self, invoice_id):
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        pac_params_obj = self.pool.get('params.pac')
        res={}
        invoice = invoice_obj.browse(self.cr, self.uid, invoice_id)
        pac_params_ids = pac_params_obj.search(self.cr, self.uid, [
            ('method_type', '=', 'pac_sf_firmar'),
            ('company_id', '=', invoice.company_id.id), 
            ('active', '=', True)], limit=1)
        pac_params_id = pac_params_ids and pac_params_ids[0] or False
        if pac_params_id:
            data_pac = pac_params_obj.browse(self.cr, self.uid, pac_params_id)
            res.update({
                'certificate_link' : data_pac.certificate_link or False,
            })
        return res
        
    def _get_text_promissory(self, company, partner, address_emitter, invoice):
        text = ''
        context = {}
        lang = self.pool.get('res.partner').browse(self.cr, self.uid,\
            partner.id).lang
        if lang:
            context.update({'lang' : lang})
        company = self.pool.get('res.company').browse(self.cr, self.uid,\
            company.id, context=context)
        if company.dinamic_text:
            try:
                if company.dict_var:
                    text = company.dinamic_text % eval("{" + company.dict_var + "}")
                else:
                    text = company.dinamic_text
            except:
                return text
        return text
        

webkit_report.WebKitParser('report.account.invoice.facturae.webkit',
            'account.invoice',
            'addons/l10n_mx_facturae_report/report/invoice_facturae_html.mako',
            parser=invoice_facturae_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
