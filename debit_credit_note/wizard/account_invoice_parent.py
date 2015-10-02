# coding: utf-8
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>

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
from lxml import etree


class AccountInvoiceParent(osv.osv_memory):

    """Assign parent to invoice"""

    _name = "account.invoice.parent"
    _description = "Parent Invoice"
    _columns = {
        'parent_id': fields.many2one('account.invoice', 'Source Invoice', help='You can select here the source invoice to use as father as the current invoice.'),
        'sure': fields.boolean('Are you sure?'),
        'partner_id': fields.many2one('res.partner', 'Partner', help='Customer or supplier who owns the invoice'),
        'type': fields.selection([('modify', 'Change source invoice')], "Operation Type", help='Operation to make on the refund invoice or debit credit note.\n'
                                 'Change source invoice: Modify the current parent invoice of the current invoice.'),
    }

    def _get_partner(self, cr, uid, context=None):
        """ Return invoice partner
        """
        inv_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        partner_id = False
        if context.get('active_id', False):
            partner_id = inv_obj.browse(
                cr, uid, context['active_id']).partner_id.id
        return partner_id

    _defaults = {
        'partner_id': _get_partner,
        'type': 'modify',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        """ Change fields position in the view
        """
        if context is None:
            context = {}
        res = super(AccountInvoiceParent, self).fields_view_get(cr, uid, view_id=view_id,
                                                                view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='partner_id']")
            partner_string = _('Customer')
            if context.get('type', 'out_invoice') in ('in_invoice', 'in_refund'):
                partner_string = _('Supplier')
            for node in nodes:
                node.set('string', partner_string)

            nodes = doc.xpath("//field[@name='parent_id']")
            parent_invisible = 'True'
            domain = str(False)
            required = str(False)
            if context.get('op_type', False) in ('modify', 'assigned'):
                parent_invisible = 'False'
                state_lst = ['open', 'paid']
                domain = '[("partner_id", "=", ' + str(context.get('partner_id', False)) + '),("id", "!=", ' + \
                    str(context.get('active_id', False)) + \
                    '),("state", "in", ' + str(state_lst) + ')]'
                required = str(True)
            for node in nodes:
                node.set('invisible', parent_invisible)
                node.set('domain', domain)
                node.set('required', required)
                domain = '[("state", "in", "[open,paid]")]'

            nodes = doc.xpath("//button[@string='Next']")
            button_string = _('Next')
            if context.get('op_type', False) == 'assigned':
                button_string = _('Assign')
            if context.get('op_type', False) == 'unlink':
                button_string = _('Unlink')
            if context.get('op_type', False) == 'modify':
                button_string = _('Modify')
            for node in nodes:
                node.set('string', button_string)

            res['arch'] = etree.tostring(doc)
        return res

    def default_get(self, cr, uid, fields, context=None):
        """ Change value for default of the type field
        """
        res = super(AccountInvoiceParent, self).default_get(
            cr, uid, fields, context=context)
        if context.get('op_type', False):
            res.update({'type': context.get('op_type', 'modify')})
        return res

    def get_window(self, cr, uid, ids, xml_id, module, op_type, partner_id, parent_id=False, context=None):
        """ Update values (op_type, partner_id and parent_id) in the window
        @param xml_id:
        @param op_type:
        @param partner_id:
        @param parent_id:
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        # we get the model
        result = mod_obj.get_object_reference(cr, uid, module, xml_id)
        id = result and result[1] or False
        # we read the act window
        result = act_obj.read(cr, uid, id, context=context)
        # we add the new context into context dictionary
        invoice_context = eval(result['context'])
        invoice_context.update(
            {'op_type': op_type, 'partner_id': partner_id, 'parent_id': parent_id})
        result['context'] = invoice_context
        return result

    def check_sure(self, cr, uid, ids, ok, context=None):
        """ Checks if the user is sure
        """
        if not ok:
            raise osv.except_osv(_('User Error'), _(
                'Assign parent invoice, Please check the box to confirm that you agree!'))
        return True

    def check_recursion(self, cr, uid, ids, child_id, parent_id, context=None):
        """ Checks that have not recursion between parent and children
        @param child_id: child id
        @param parent_id: parent id
        """
        if child_id == parent_id:
            raise osv.except_osv(_('User Error'), _(
                'Current invoice is the same father invoice, Credit or debit note have to be diferent of parent invoice, Please choise another one!'))
        return True

    def check_grandfather(self, cr, uid, ids, parent_id, context=None):
        """ Check that parent_id having parent
        @param parent_id:
        """
        inv_obj = self.pool.get('account.invoice')
        inv_parent_brw = inv_obj.browse(cr, uid, parent_id, context=context)
        if inv_parent_brw.parent_id:
            raise osv.except_osv(_('User Error'), _(
                'Incorrect Parent Invoice, The parent invoice selected can not have an assigned parent invoice!'))
        return True

    def action_assigned(self, cr, uid, ids, form, context=None):
        """ Check that credit or debit note having assigned invoice
        @param form: fields values
        """
        self.check_sure(cr, uid, ids, form['sure'], context)
        active_id = context.get('active_id', False)
        parent_id = form.get('parent_id', False)
        partner_id = form.get('partner_id', False)
        self.check_recursion(cr, uid, ids, active_id, parent_id, context)
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, active_id, context=context)

        if inv_brw.parent_id:
            raise osv.except_osv(_('User Error'), _(
                'Credit or debit note assign, This credit or debit note already assign to an invoice!'))
        if parent_id:
            self.check_grandfather(cr, uid, ids, parent_id, context)
            inv_obj.write(cr, uid, active_id, {
                          'parent_id': parent_id}, context=context)
            return {}

        result = self.get_window(cr, uid, ids, 'action_account_invoice_parent',
                                 'l10n_ve_fiscal_requirements', 'assigned', partner_id, parent_id)

        return result

    def action_unlink(self, cr, uid, ids, form, context=None):
        """ Remove the parent of the partner
        @param form: fields values parent_id and partner_id
        """
        self.check_sure(cr, uid, ids, form['sure'], context)
        active_id = context.get('active_id', False)
        parent_id = form.get('parent_id', False)
        partner_id = form.get('partner_id', False)
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, active_id, context=context)

        if inv_brw.parent_id:
            inv_obj.write(cr, uid, active_id, {
                          'parent_id': False}, context=context)
            return {}

        result = self.get_window(cr, uid, ids, 'action_account_invoice_parent',
                                 'l10n_ve_fiscal_requirements', 'unlink', partner_id, parent_id)
        return result

    def action_modify(self, cr, uid, ids, form, context=None):
        """ Modify parent of the partner
        @param form: fields values parent_id and partner_id
        """
        self.check_sure(cr, uid, ids, form['sure'], context)
        active_id = context.get('active_id', False)
        parent_id = form.get('parent_id', False)
        partner_id = form.get('partner_id', False)
        self.check_recursion(cr, uid, ids, active_id, parent_id, context)
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, active_id, context=context)

        if parent_id:
            self.check_grandfather(cr, uid, ids, parent_id, context)
            inv_obj.write(cr, uid, active_id, {
                          'parent_id': parent_id}, context=context)
            return {}

        result = self.get_window(cr, uid, ids, 'action_account_invoice_parent',
                                 'l10n_ve_fiscal_requirements', 'modify', partner_id, parent_id)
        return result

    def invoice_operation(self, cr, uid, ids, context=None):
        """ General method that calls a function depending of the data['type']
        """
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        if data['type']:
            context.update({'op_type': data['type']})
        operation_method = getattr(self, "action_%s" % data['type'])

        return operation_method(cr, uid, ids, data, context=context)
