# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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

from openerp.osv import osv, fields


class ProductUomUpdate(osv.TransientModel):

    _name = 'base.product.merge.uom.wizard'

    def default_get(self, cr, uid, fields, context=None):

        if not context:
            context = {}
        products = context.get('active_ids', False)
        res = super(ProductUomUpdate, self).default_get(
            cr, uid, fields, context=context)
        res.update({'uom_id_from': products})
        return res

    def unit_measure_update(self, cr, uid, ids, context=None):

        product_ids_validate = []
        product_ids_unvalidate = []
        product_ids_validate_name = []
        string_result = ''

        product_model = self.pool.get('product.product')
        wizard = self.browse(cr, uid, ids[0], context=context)
        new_unit = context.get('uom_id_to_id')[0]
        product_ids = []
        for product in wizard.uom_id_from:
            product_ids.append(product.id)
        if len(product_ids) > 0:
            context.update({'active_ids': product_ids})
            res = self.pool.get('base.product.merge.automatic.wizard').\
                _update_foreign_keys(
                cr, uid, False, [new_unit],
                model='product_uom', context=context)
            dst_product_ids = product_model.browse(
                cr, uid, product_ids, context=context)
            uom_factor_dst = self.pool.get('product.uom').browse(
                cr, uid, context.get('uom_id_to_id'), context=context)[0].\
                factor
            for dst_product_id in dst_product_ids:
                if dst_product_id.uom_id.factor == uom_factor_dst:
                    product_ids_validate.append(dst_product_id.product_tmpl_id.id)
                    product_ids_validate_name.append(
                        dst_product_id.name.encode('utf8'))
                else:
                    product_ids_unvalidate.append(
                        dst_product_id.name.encode('utf8'))
                if len(product_ids_validate) > 0:
                    product_ids_tuple = tuple(product_ids_validate)
                    query = '''UPDATE "product_template" SET uos_id = %s ,\
                            uom_id = %s , uom_po_id = %s
                                           WHERE id IN %%s''' % (new_unit,
                                                                 new_unit, new_unit)
                    cr.execute(query, (product_ids_tuple,))

            if len(product_ids_validate) > 0:
                string_aux1 = '\n'.join(product_ids_validate_name)
                string_result += '''Products changed:\n\n %s ''' % (
                    string_aux1)
            if len(product_ids_unvalidate) > 0:
                string_aux2 = '\n'.join(product_ids_unvalidate)
                string_result += '''\n\nProducts that not change because the '''\
                    '''conversion factor is not equal:\n\n %s''' % (
                        string_aux2)

        else:
            string_result = 'Warning! \n\n You must choose at least one record..'

        __, xml_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'product_uom_update',
            'base_product_uom_merge_wizard_result')

        context.update(
            {'default_result': string_result})

        return {
            'res_model': 'base.product.merge.uom.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': xml_id,
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def close_vw(self, cr, uid, ids, context=None):
        return self.pool.get('base.product.merge.automatic.wizard').\
            close_cb(cr, uid, ids, context=context)

    _columns = {
        'uom_id_from': fields.many2many('product.product',
                                        'product_produtc_uom_rel',
                                        'product_id', 'uom_id',
                                        'products with unit of measure from',
                                        help="Default unit of measure used for all stock operation."),
        'uom_id_to': fields.many2one('product.uom', 'Unit of Measure To',
                                     help="Default unit of measure used for all stock operation."),
        'result': fields.text('Result'),

    }


class ProductWizard(osv.TransientModel):
    _name = 'product.uom.wizard'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'wizard_id': fields.many2one('base.product.merge.uom.wizard'),
    }
