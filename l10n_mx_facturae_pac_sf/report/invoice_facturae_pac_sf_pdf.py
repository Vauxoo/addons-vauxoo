# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
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
from openerp import tools
# from amount_to_text_es import amount_to_text as amount_to_text_class

# amount_to_text = amount_to_text_obj.amount_to_text
# amount_to_text = amount_to_text_obj.amount_to_text_cheque

# sql_delete_report = "DELETE FROM ir_act_report_xml WHERE report_name =
# 'account.invoice.facturae.pdf'"--Si no toma la actualizacion del reporte
# xml, borrarlo directamente desde la base de datos, con este script.


class account_invoice_facturae_pac_sf_pdf(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_invoice_facturae_pac_sf_pdf, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'set_global_data': self._set_global_data,
            'facturae_data_dict': self._facturae_data_dict,
            #'amount_to_text': self._get_amount_to_text,
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
        })
        self.taxes = []

    def _exists_key(self, key):
        return key in self.invoice._columns
        """
        try:
            str= 'self.invoice.'+key
            if eval(str):
                return True
        except:
            return False
        """

    def _set_global_data(self, o):
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
        return ""

    def _get_approval(self):
        return self.approval

    def _get_invoice_sequence(self):
        return self.sequence

    def _set_invoice_sequence_and_approval(self, invoice_id):
        # TinyERP Compatibility
        context = {}
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        sequence_obj = pool.get('ir.sequence')
        approval_obj = pool.get('ir.sequence.approval')
        # invoice = invoice_obj.browse(self.cr, self.uid, invoice_id)
        sequence_id = invoice_obj._get_invoice_sequence(
            self.cr, self.uid, [invoice_id])[invoice_id]
        sequence = sequence_obj.browse(self.cr, self.uid, [sequence_id])[0]
        self.sequence = sequence

        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id])[0]
        context.update({'number_work': invoice.number})
        approval_id = sequence_obj._get_current_approval(
            self.cr, self.uid, [sequence_id], context=context)[sequence_id]
        approval = approval_obj.browse(self.cr, self.uid, [approval_id])[0]
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

    '''
    def _set_taxes(self, invoice_id):
        """
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        invoice = invoice_obj.browse(self.cr, self.uid, [invoice_id])[0]
        taxes = []
        for line_tax_id in invoice.tax_line:
            tax_name = line_tax_id.name.lower().replace('.','').replace(
                '-','').replace(' ', '')
            if tax_name in ['iva']:
                tax_name = 'IVA'
            elif 'isr' in tax_name:
                tax_name = 'ISR'
            elif 'ieps' in tax_name:
                tax_name = 'IEPS'
            tax_names.append( tax_name )
            taxes.append({
                'name': tax_name,
                'rate': "%.2f"%( round( line_tax_id.amount/(
                    invoice.amount_total-line_tax_id.amount)*100, 0) ),
                'amount': "%.2f"%( line_tax_id.amount or 0.0),
            })
        """
        self.taxes = self.invoice_data_dict['Comprobante']['Impuestos']['Traslados']
        #self.taxes = taxes
        return taxes
    '''

    def _split_string(self, string, length=75):
        if string:
            for i in range(0, len(string), length):
                string = string[:i] + ' ' + string[i:]
        return string
    """
    def _get_amount_to_text(self, amount, lang, currency=""):
        if currency.upper() in ('MXP', 'MXN', 'PESOS', 'PESOS MEXICANOS'):
            sufijo = 'M. N.'
            currency = 'PESOS'
        else:
            sufijo = 'M. E.'
        #return amount_to_text(amount, lang, currency)
        amount_text = amount_to_text(amount, currency, sufijo)
        amount_text = amount_text and amount_text.upper() or ''
        return amount_text
    """
    def _get_company_address(self, invoice_id):
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        partner_obj = pool.get('res.partner')
        address_obj = pool.get('res.partner')
        invoice = invoice_obj.browse(self.cr, self.uid, invoice_id)
        partner_id = invoice.company_id.parent_id and invoice.company_id.\
            parent_id.partner_id.id or invoice.company_id.partner_id.id
        self.invoice = invoice
        # print "partner_id",partner_id
        # invoice = partner_obj.browse(cr, uid, invoice_id)
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
        # print "self.company_address_invoice",self.company_address_invoice
        # print "self.company_address_invoice[0]",self.company_address_invoice[0]
        # self.company_address_invoice  = self.company_address_invoice and self.company_address_invoice[0] or False
        # print "self.company_address_invoice",self.company_address_invoice
        # return [self.company_address_invoice]
        return ""

    def _company_address(self):
        # print "self.company_address_invoice",self.company_address_invoice
        return self.company_address_invoice

    def _subcompany_address(self):
        return self.subcompany_address_invoice

    def _facturae_data_dict(self):
        # print "self.invoice_data_dict",self.invoice_data_dict
        return self.invoice_data_dict

    def _get_facturae_data_dict(self, invoice):
        self._set_invoice_sequence_and_approval(invoice.id)
        self.taxes = [
            tax for tax in invoice.tax_line if tax.tax_percent >= 0.0]
        self.taxes_ret = [
            tax for tax in invoice.tax_line if tax.tax_percent < 0.0]
        return ""
    """
    def _get_facturae_data_dict(self, invoice_id):
        pool = pooler.get_pool(self.cr.dbname)
        invoice_obj = pool.get('account.invoice')
        invoice_tax = pool.get('account.invoice.tax')
        self.invoice_data_dict = invoice_obj._get_facturae_invoice_xml_data(
            self.cr, self.uid, [invoice_id], context={'type_data': 'dict'})
        self._set_invoice_sequence_and_approval( invoice_id )
        try:
            self.taxes = [ traslado['Traslado'] for traslado in self.\
                invoice_data_dict['Comprobante']['Impuestos']['Traslados'] if (
                float( traslado['Traslado']['tasa'] ) >= 0.00 and traslado[
                'Traslado']['impuesto']!='IEPS') or (traslado['Traslado'][
                'impuesto']=='IEPS' and float(traslado['Traslado']['tasa']) > 0.01)]
            #self.taxes.extend( self.taxes_ret )
        except Exception, e:
            print "exception: %s"%( e )
            pass

        self.taxes_ret = []
        for retencion in self.invoice_data_dict['Comprobante']['Impuestos'].get(
            'Retenciones', []):
            amount_untaxed = float( self.invoice_data_dict['Comprobante']['subTotal'] )
            tax_ret_amount = float( retencion['Retencion']['importe'] )
            tasa = tax_ret_amount and amount_untaxed and tax_ret_amount * 100 \
            / amount_untaxed or 0.0
            retencion['Retencion'].update({'tasa':  tasa})
            self.taxes_ret.append( retencion['Retencion'] )
        return ""
    """

    def _get_data_partner(self, partner_id):
        partner_obj = self.pool.get('res.partner')
        res = {}
        address_invoice_id = partner_obj.search(self.cr, self.uid, [(
            'parent_id', '=', partner_id.id), ('type', '=', 'invoice')])
        if address_invoice_id:
            address_invoice = partner_obj.browse(
                self.cr, self.uid, address_invoice_id[0])
            if address_invoice:
                res.update({
                    'street': address_invoice.street or False,
                    'street3': address_invoice.l10n_mx_street3 or False,
                    'street4': address_invoice.l10n_mx_street4 or False,
                    'street2': address_invoice.street2 or False,
                    'city': address_invoice.city or False,
                    'state': address_invoice.state_id and address_invoice.
                    state_id.name or False,
                    'city2': address_invoice.l10n_mx_city2 or False,
                    'zip': address_invoice.zip or False,
                    'vat': 'vat_split' in address_invoice._columns and
                    address_invoice.vat_split or address_invoice.vat or False,
                    'phone': address_invoice.phone or False,
                    'fax': address_invoice.fax or False,
                    'mobile': address_invoice.mobile or False,
                })
        return res
report_sxw.report_sxw(
    'report.account.invoice.facturae.pac.sf.pdf',
    'account.invoice',
    'addons/l10n_mx_facturae_pac_sf/report/invoice_facturae_pac_sf_pdf.rml',
    header=False,
    parser=account_invoice_facturae_pac_sf_pdf,
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
