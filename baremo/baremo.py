# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar.hernandez@netquatro.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp import SUPERUSER_ID


class baremo_book(osv.Model):
    _name = 'baremo.book'

    _columns = {
        'name': fields.char('Baremo', size=64, required=True, readonly=False),
        'notes': fields.text('Notas', required=True, readonly=False),
        'bar_ids': fields.one2many(
            'baremo', 'bar_id', 'Dias de Emision',
            required=False,
            copy=True,
        ),
    }
    _defaults = {
        'name': lambda *a: 'DEBE ESCRIBIR UNA NOTA REFERENTE A ESTE BAREMO \
            PARA SER USADO EN EL REPORTE DE COMISIONES, COMO POR EJEMPLO, LOS\
            DESCUENTOS NEGATIVOS REPRESENTAN LOS SOBRE PRECIOS REALIZADOS A\
            LOS PRODUCTOS PARA COMPENSAR EN PAGO RETARDADO POR PARTE DEL\
            CLIENTE',
    }


class baremo(osv.Model):

    """
    OpenERP Model : baremo
    """

    _name = 'baremo'
    _order = "number asc"

    _columns = {
        'name': fields.char(
            'Nombre', size=64, required=True, readonly=False,
            help="Nombre del termino de Vencimiento"),
        'number': fields.integer(
            'Dias', help="Dias desde emision de la factura", required=True),
        'disc_ids': fields.one2many(
            'baremo.discount', 'disc_id', 'Comision x Dscto.',
            required=False, help="Comision x Dscto x Dia",
            copy=True,
        ),
        'bar_id': fields.many2one('baremo.book', 'Padre', required=False),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class baremo_discount(osv.Model):

    """
    OpenERP Model : baremo_discount
    """

    _name = 'baremo.discount'
    _order = "porc_disc asc"
    _columns = {
        'name': fields.char(
            'Nombre', size=64, required=False, readonly=False,
            help="No Usado"),
        'porc_disc': fields.float(
            '% Dcto', digits_compute=dp.get_precision('Commission'),
            help="% de Descuento por producto", required=True),
        'porc_com': fields.float(
            '% Com.', digits_compute=dp.get_precision('Commission'),
            help="% de Comision @ porcentaje Descuento", required=True),
        'disc_id': fields.many2one('baremo', 'Baremo', required=False),
    }
    _defaults = {
        'name': lambda *a: None,
    }


class res_parter(osv.Model):
    _inherit = "res.partner"
    _columns = {
        'baremo_id': fields.many2one('baremo.book', 'Baremo', required=False),
    }


class res_company(osv.Model):
    _inherit = "res.company"
    _description = 'Companies'

    def _get_baremo_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'baremo_id' functional field. """
        result = {}
        part_obj = self.pool.get('res.partner')
        for company in self.browse(cr, uid, ids, context=context):
            result[company.id] = {}.fromkeys(field_names, False)
            if company.partner_id:
                data = part_obj.read(cr, SUPERUSER_ID, [company.partner_id.id],
                                     field_names, context=context)[0]
                for field in field_names:
                    result[company.id][field] = data[field] or False
        return result

    def _set_baremo_data(self, cr, uid, company_id, name, value, arg,
                         context=None):
        """ Write the 'baremo_id' functional field. """
        part_obj = self.pool.get('res.partner')
        company = self.browse(cr, uid, company_id, context=context)
        if company.partner_id:
            part_obj.write(
                cr, uid, company.partner_id.id, {name: value or False},
                context=context)
        return True

    _columns = {
        'baremo_id': fields.function(
            _get_baremo_data,
            fnct_inv=_set_baremo_data,
            type='many2one',
            relation='baremo.book',
            string="Baremo",
            multi='baremo',
            ),
    }
