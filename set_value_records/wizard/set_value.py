#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

import time
import datetime
import re


class set_values(osv.TransientModel):

    _name = 'set.values'

    def _get_fields(self, cr, uid, ids=1, context=None,*a):
        if context is None:
            context = {}

        product_obj = self.pool.get('product.product')
        fields = product_obj.fields_get(cr, uid)     
        select = []
        for field in fields:
            if fields.get(field,{}).get('type',_('No String')) not in \
                    ('many2many','one2many'):
                select.append((field,
                           fields.get(field,{}).get('string',_('No String'))))
    
        return select 
    

    _columns = {
        'sure': fields.boolean('Sure', help="Are sure this operation"),
        'confirm': fields.boolean('Confirm', help="Are sure this operation"),
        'fields':fields.selection(_get_fields, help='All model fields to '
                                                    'select which you want '
                                                    'change'), 
        'value':fields.text('Value',help='Value to change or search parameter '
                                         'to find value in relational field'),
        
    }


    def _get_type(self, cr, uid, value, field_val, field , model, context):

        context = context or {}

        model_obj  = self.pool.get(model)
        fieldi_d = model_obj.fields_get(cr, uid, field)
        if fieldi_d:
            type = fieldi_d.get(field,{}).get('type')
            if type == 'boolean':
                true = '^(Y|y|T|t|s|S)*[a-z|A-Z]*(E|e|i|I|s|S)$' 
                false = '^(N|n|F|f)*[a-z|A-Z]*(E|e|o|O)$' 
                if re.search(true,value):
                    return True
                if re.search(false,value):
                    return False
            if type in ('int','many2one'):
                return field_val.isdigit() and int(field_val)

            if type in ('char', 'text', 'date', 'datetime'):
                return field_val

        return eval(field_val)

        

    def _get_value(self, cr, uid, value, type,relation, context):

        context = context or {}
        if type == 'boolean':
            true = '^(Y|y|T|t|s|S)*[a-z|A-Z]*(E|e|i|I|s|S)$' 
            false = '^(N|n|F|f)*[a-z|A-Z]*(E|e|o|O)$' 
            if re.search(true,value):
                return True
            if re.search(false,value):
                return False


        search = []
        if type == 'many2one':
            for val in value.split('\n'):
                vals = val.split(' ')
                if len(vals) >= 3:
                    search.append((vals[0],vals[1],self._get_type(cr,uid,value,
                                                                ' '.join(vals[2:]),
                                                                vals[0],
                                                                relation,
                                                                context,
                                                                )))
            model_ids = search and self.pool.get(relation).search(cr, uid,
                                                                  search,
                                                               context=context)
            return model_ids and model_ids[0] or value.isdigit() and\
                                                 int(value)
            
        if type in ('int'):
            return value.isdigit() and int(value)

        if type in ('char', 'text', 'date', 'datetime'):
            return value

        return eval(field_val)
            




    def change_values(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for wzr_brw in self.browse(cr, uid, ids, context=context):
            if wzr_brw.sure and wzr_brw.confirm:
                if context.get('active_ids') and context.get('active_model'):
                    model_obj = self.pool.get(context.get('active_model'))
                    field = model_obj.fields_get(cr, uid, wzr_brw.fields)
                    types = field.get(wzr_brw.fields,{}).get('type')
                    if types in ('char','text'):
                        model_obj.write(cr, uid, context.get('active_ids'),
                                        {wzr_brw.fields:wzr_brw.value.strip()},
                                       context=context)

                    if types == 'boolean':
                        model_obj.write(cr, uid, context.get('active_ids'),
                                        {wzr_brw.fields:\
                                         self._get_value(cr, uid,
                                                         wzr_brw.value.strip(),
                                                         types,
                                                         False,
                                                         context)},
                                       context=context)
                    if types in('many2one','int','float','date','datetime'):
                        val = self._get_value(cr, uid,wzr_brw.value.strip(),
                                                         types,
                                                         field.get(wzr_brw.fields,{}).get('relation'),
                                                         context)
                        if val and \
                           field.get(wzr_brw.fields,{}).get('required') or \
                           not field.get(wzr_brw.fields,{}).get('required') and \
                           val:
                            model_obj.write(cr, uid, context.get('active_ids'),
                                        {wzr_brw.fields:val
                                         },
                                       context=context)
            else:
                raise osv.except_osv(_('Error'),
                                               _('Please select the checkbox'))
        return {'type': 'ir.actions.act_window_close'}
