# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import osv, fields

class product_arancel(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code']+': '+name
            res.append((record['id'], name))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of account for searching
                operand1,operand2 = name.split(': ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = 'product.arancel'
    _description = 'Arancel of customs'
    _columns = {
        'code' : fields.char('Code', size=64),
        'name': fields.char('Name', size=2048, required=True, translate=True, select=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
        'parent_id': fields.many2one('product.arancel','Parent Arancel', select=True, domain=[('type','=','view')]),
        'child_ids': fields.one2many('product.arancel', 'parent_id', string='Child Arancel'),
        'type': fields.selection([('view','View'), ('normal','Normal')], 'Arancel Type'),
        'tax_ids' : fields.many2many('account.tax','product_arancel_tax','arancel_id','tax_id','Taxes')

    }

    _order = "code"
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from product_arancel where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive arancel.', ['parent_id'])
    ]
    def child_get(self, cr, uid, ids):
        return [ids]

product_arancel()

