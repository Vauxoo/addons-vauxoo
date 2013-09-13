# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from osv import osv, fields
from tools.translate import _

## Create an invoice based on selected timesheet lines
#

class account_analytic_line(osv.osv):
    _inherit = "account.analytic.line"

    #
    # data = {
    #   'date': boolean
    #   'time': boolean
    #   'name': boolean
    #   'price': boolean
    #   'product': many2one id
    # }
    def invoice_cost_create(self, cr, uid, ids, data={}, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        res_partner_obj = self.pool.get('res.partner')
        account_payment_term_obj = self.pool.get('account.payment.term')
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        invoice_factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        pro_price_obj = self.pool.get('product.pricelist')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        product_uom_obj = self.pool.get('product.uom')
        invoice_line_obj = self.pool.get('account.invoice.line')
        feature_line_obj = self.pool.get('product.feature.line')
        invoices = []
        if context is None:
            context = {}

        account_ids = {}
        for line in self.pool.get('account.analytic.line').browse(cr, uid, ids, context=context):
            account_ids[line.account_id.id] = True

        account_ids = account_ids.keys() #data['accounts']
        for account in analytic_account_obj.browse(cr, uid, account_ids, context=context):
            partner = account.partner_id
            if (not partner) or not (account.pricelist_id):
                raise osv.except_osv(_('Analytic Account incomplete'),
                        _('Please fill in the Partner or Customer and Sale Pricelist fields in the Analytic Account:\n%s') % (account.name,))

            if not partner.address:
                raise osv.except_osv(_('Partner incomplete'),
                        _('Please fill in the Address field in the Partner: %s.') % (partner.name,))

            date_due = False
            if partner.property_payment_term:
                pterm_list= account_payment_term_obj.compute(cr, uid,
                        partner.property_payment_term.id, value=1,
                        date_ref=time.strftime('%Y-%m-%d'))
                if pterm_list:
                    pterm_list = [line[0] for line in pterm_list]
                    pterm_list.sort()
                    date_due = pterm_list[-1]
            curr_invoice = {
                'name': time.strftime('%d/%m/%Y')+' - '+account.name,
                'partner_id': account.partner_id.id,
                'address_contact_id': res_partner_obj.address_get(cr, uid,
                    [account.partner_id.id], adr_pref=['contact'])['contact'],
                'address_invoice_id': res_partner_obj.address_get(cr, uid,
                    [account.partner_id.id], adr_pref=['invoice'])['invoice'],
                'payment_term': partner.property_payment_term.id or False,
                'account_id': partner.property_account_receivable.id,
                'currency_id': account.pricelist_id.currency_id.id,
                'date_due': date_due,
                'fiscal_position': account.partner_id.property_account_position.id,
                'type':'out_invoice',
                'journal_id':account.journal_id.id
            }
            last_invoice = invoice_obj.create(cr, uid, curr_invoice, context=context)
            invoices.append(last_invoice)
            context2 = context.copy()
            context2['lang'] = partner.lang
            cr.execute("SELECT product_id, to_invoice, unit_amount, product_uom_id, w_start, w_end, name, amount, feature_id, prodlot_id " \
                    "FROM account_analytic_line as line " \
                    "WHERE account_id = %s " \
                        "AND id IN %s AND to_invoice IS NOT NULL " , (account.id, tuple(ids),))

            for product_id, factor_id, qty, uom, w_start, w_end, name, amount, feature_id, prodlot_id in cr.fetchall():
                product = product_obj.browse(cr, uid, product_id, context2)
                if not product:
                    raise osv.except_osv(_('Error'), _('At least one line has no product !'))
                factor_name = ''
                factor = invoice_factor_obj.browse(cr, uid, factor_id, context2)

                ctx =  context.copy()
                ctx.update({'uom':uom})
                if account.pricelist_id:
                    pl = account.pricelist_id.id
                    price = pro_price_obj.price_get(cr,uid,[pl], product_id or data.get('product', False), qty or 1.0, account.partner_id.id, context=ctx)[pl]
                else:
                    price = 0.0

                taxes = product.taxes_id
                tax = fiscal_pos_obj.map_tax(cr, uid, account.partner_id.property_account_position, taxes)
                account_id = product.product_tmpl_id.property_account_income.id or product.categ_id.property_account_income_categ.id
                if not account_id:
                    raise osv.except_osv(_("Configuration Error"), _("No income account defined for product '%s'") % product.name)
                curr_line = {
                    'price_unit': amount or price,
                    'quantity': qty,
                    'discount':factor.factor,
                    'invoice_line_tax_id': [(6,0,tax )],
                    'invoice_id': last_invoice,
                    'name': name,
                    'product_id': product_id or data.get('product',product_id),
                    'invoice_line_tax_id': [(6,0,tax)],
                    'uos_id': uom,
                    'account_id': account_id,
                    'account_analytic_id': account.id,
                    'w_start': int(w_start or 0),
                    'w_end': int(w_end or 0),
                    'prodlot_id': prodlot_id,
                }
                feature_line_obj.write(cr, uid, feature_id, {'counter': int(w_end or 0)}, context=context)
                #
                # Compute for lines
                #
                cr.execute("SELECT * FROM account_analytic_line WHERE account_id = %s and id IN %s AND product_id=%s and to_invoice=%s ORDER BY account_analytic_line.date", (account.id, tuple(ids), product_id, factor_id))

                line_ids = cr.dictfetchall()
                note = []
                for line in line_ids:
                    # set invoice_line_note
                    details = []
                    if data.get('date', False):
                        details.append(line['date'])
                    if data.get('time', False):
                        if line['product_uom_id']:
                            details.append("%s %s" % (line['unit_amount'], product_uom_obj.browse(cr, uid, [line['product_uom_id']],context2)[0].name))
                        else:
                            details.append("%s" % (line['unit_amount'], ))
                    if data.get('name', False):
                        details.append(line['name'])
                    note.append(u' - '.join(map(lambda x: unicode(x) or '',details)))

                curr_line['note'] = "\n".join(map(lambda x: unicode(x) or '',note))
                invoice_line_obj.create(cr, uid, curr_line, context=context)
                cr.execute("update account_analytic_line set invoice_id=%s WHERE account_id = %s and id IN %s", (last_invoice, account.id, tuple(ids)))

            invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices

class lines_create(osv.osv_memory):

    _name = 'lines.create'
    _columns = {
        'month': fields.selection([('1','January'), ('2','February'),
            ('3','March'), ('4','April'), ('5','May'), ('6','June'),
            ('7','July'), ('8','August'), ('9','September'), ('10','October'),
            ('11','November'), ('12','December')], 'Month'),
        'line_ids': fields.many2many('account.analytic.line','analytic_wiz_lines_rel','wiz_id','line_id','lines'),
        'contract_id': fields.many2one('account.analytic.account','Contract')
        #~ 'time': fields.boolean('Time spent', help='The time of each work done will be displayed on the invoice'),
        #~ 'name': fields.boolean('Description', help='The detail of each work done will be displayed on the invoice'),
        #~ 'price': fields.boolean('Cost', help='The cost of each work done will be displayed on the invoice. You probably don\'t want to check this'),
        #~ 'product': fields.many2one('product.product', 'Product', help='Complete this field only if you want to force to use a specific product. Keep empty to use the real product that comes from the cost.'),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(lines_create, self).default_get(
            cr, uid, fields, context=context)
        analytic_obj = self.pool.get('account.analytic.account')
        product_obj = self.pool.get('product.product')
        line_obj = self.pool.get('account.analytic.line')
        lines_ids=[]
        if context.get('active_model') == 'account.analytic.account':
            res['contract_id']=context.get('active_id')
            res['month']=str(datetime.strptime(datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d").month)
            for contract in analytic_obj.browse(cr,uid,context['active_ids'],context):
                lines_ids=[]
                for line in contract.line_ids:
                    if not line.invoice_id and line.to_invoice:
                        date_line=datetime.strptime(line.date, "%Y-%m-%d")
                        #~ date=datetime.strptime(datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d")
                        if date_line.month==res['month']:
                            lines_ids.append(line.id)
            res['line_ids']=lines_ids
        return res

    def onchange_date(self, cr, uid, ids, month, contract_id, context=None):
        if context is None:
            context = {}
        res={}
        analytic_obj = self.pool.get('account.analytic.account')
        line_obj = self.pool.get('account.analytic.line')
        lines_ids=[]
        for contract in analytic_obj.browse(cr,uid,[contract_id],context):
            lines_ids=[]
            for line in contract.line_ids:
                if not line.invoice_id and line.to_invoice:
                    date_line=datetime.strptime(line.date, "%Y-%m-%d")
                    #~ date_new=datetime.strptime(month, "%Y-%m-%d")
                    if str(month)==str(date_line.month):
                        for feature in contract.feature_ids:
                                if feature.id==line.feature_id.id:
                                    line_obj.write(cr, uid, line.id, {'w_start':feature.counter}, context=context)
                        lines_ids.append(line.id)
        res['value']={'line_ids':lines_ids}
        return res
        


    def do_create(self, cr, uid, ids, context=None):
        analytic_obj = self.pool.get('account.analytic.account')
        data = self.read(cr, uid, ids, [], context=context)[0]
        if context.get('active_model') == 'account.analytic.account':
            invs=[]
            for contract in analytic_obj.browse(cr,uid,context['active_ids'],context):
                new_lines=[]
                for prod in contract.product_ids:
                    lines_ids=[]
                    for line in contract.line_ids:
                        if not line.invoice_id and line.to_invoice and line.product_id.id==prod.product_id.id and prod.type=='rent':
                            date_line=datetime.strptime(line.date, "%Y-%m-%d")
                            #~ date=datetime.strptime(data['date'], "%Y-%m-%d")
                            if str(date_line.month)==data['month']:
                                lines_ids.append(line.id)
                    if not lines_ids and prod.type=='rent':
                        raise osv.except_osv(_('Warning !'), _("Invoice is already linked to some of the analytic line(s)!"))
                    if contract.group_product and prod.type=='rent':
                        new_lines=new_lines + lines_ids
                    elif not contract.group_product and prod.type=='rent':
                        invs.append(self.pool.get('account.analytic.line').invoice_cost_create(cr, uid, lines_ids, {}, context=context))
                if contract.group_product:
                    invs.append(self.pool.get('account.analytic.line').invoice_cost_create(cr, uid, new_lines, {}, context=context))
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')], context=context)[0]
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id','in',invs),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win


lines_create()



