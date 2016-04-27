# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
# ############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #########################################################################

from openerp.osv import osv
from openerp.tools.translate import _


class MessagePostShowAll(osv.Model):

    """With this object you can add an extensive log in your model like the
    traditional message log don't does
    You need do it the following way:
        _name = "account.invoice"
        _inherit = ['account.invoice', 'message.post.show.all']

    """

    _name = 'message.post.show.all'
    _inherit = ['mail.thread']

    # pylint: disable=W0622
    def get_last_value(self, cr, uid, ids, model=None, field=None,
                       field_type=None, context=None):
        """Return the last value of a record in the model to show a post with the
        change
        @param ids: int with id record
        @param model: String with model name
        @param field: Name field to return his value

        return the value of the field
        """
        context = context or {}

        field = ids and field or []
        model_obj = self.pool.get(model)
        model_brw = model_obj.browse(cr, uid, ids, context=context)
        if 'many2one' in field_type:
            value = field and model_brw[field] and \
                model_brw[field].name_get() or ''
            value = value and value[0][1]
        elif 'many2many' in field_type:
            value = [i.id for i in model_brw[field]]
        else:
            value = field and model_brw[field] or ''

        return field and value or ''

    def prepare_many_info(self, cr, uid, ids, records, string, n_obj,
                          last=None, context=None):
        context = context or {}
        info = {
            0: _('Created New Line'),
            1: _('Updated Line'),
            2: _('Removed Line'),
            3: _('Removed Line'),
            6: _('many2many'),
        }
        message = '<ul>'
        obj = self.pool.get(n_obj)
        r_name = obj._rec_name
        mes = False
        for val in records:
            if val and info.get(val[0], False):
                if val[0] == 0:
                    value = val[2]
                    message = u'%s\n<li><b>%s<b>: %s</li>' % \
                        (message, info.get(val[0]), value.get(r_name),)
                elif val[0] in (2, 3):
                    model_brw = obj.browse(cr, uid, val[1], context=context)
                    last_value = model_brw.name_get()
                    last_value = last_value and last_value[0][1]
                    value = val[1]
                    message = u'%s\n<li><b>%s<b>: %s</li>' % \
                        (message, info.get(val[0]), last_value)

                elif val[0] == 6:
                    lastv = list(set(val[2]) - set(last))
                    new = list(set(last) - set(val[2]))
                    add = _('Added')
                    delete = _('Deleted')
                    if lastv and not new:
                        dele = [obj.name_get(cr, uid, [i])[0][1]
                                for i in lastv]
                        mes = ' - '.join(dele)
                        message = u'%s\n<li><b>%s %s<b>: %s</li>' % \
                            (message, add, string, mes)
                    if not lastv and new:

                        dele = [obj.name_get(cr, uid, [i])[0][1] for i in new]
                        mes = '-'.join(dele)
                        message = u'%s\n<li><b>%s %s<b>: %s</li>' % \
                            (message, delete, string, mes)

                elif val[0] == 1:
                    vals = val[2]
                    id_line = 0
                    for field in vals:
                        if obj._columns[field]._type in ('one2many',
                                                         'many2many'):
                            is_many = obj._columns[field]._type == 'many2many'

                            last_value = is_many and self.get_last_value(
                                cr, uid, val[1], n_obj, field, 'many2many',
                                context)
                            field_str = obj._columns[field].string
                            new_n_obj = obj._columns[field]._obj
                            mes = self.prepare_many_info(cr, uid, val[1],
                                                         vals[field],
                                                         field_str,
                                                         new_n_obj,
                                                         last_value,
                                                         context)

                        elif obj._columns[field]._type == 'many2one':
                            mes = self.prepare_many2one_info(cr, uid, val[1],
                                                             n_obj,
                                                             field,
                                                             vals,
                                                             context)

                        elif 'many' not in obj._columns[field]._type:
                            mes = self.prepare_simple_info(cr, uid, val[1],
                                                           n_obj, field,
                                                           vals, context)
                        if mes and mes != '<p>':
                            message = id_line != val[1] and \
                                _('%s\n<h3>Line %s</h3>' % (message, val[1])) \
                                or message
                            message = '%s\n%s' % (message, mes)
                            id_line = val[1]

        message = '%s\n</ul>' % message
        return message

    def prepare_many2one_info(self, cr, uid, ids, n_obj, field, vals,
                              context=None):
        context = context or {}
        obj = self.pool.get(n_obj)
        message = '<p>'

        last_value = self.get_last_value(
            cr, uid, ids, obj._name, field, obj._columns[field]._type, context)
        model_obj = self.pool.get(obj._columns[field]._obj)
        model_brw = model_obj.browse(cr, uid, vals[field], context=context)
        new_value = model_brw.name_get()
        new_value = new_value and new_value[0][1]

        if not (last_value == new_value) and any((new_value, last_value)):
            message = u'<li><b>%s<b>: %s → %s</li>' % \
                (obj._columns[field].string,
                 last_value,
                 new_value)
        return message

    def prepare_simple_info(self, cr, uid, ids, n_obj, field,
                            vals, context=None):
        context = context or {}
        obj = self.pool.get(n_obj)
        message = '<p>'
        last_value = self.get_last_value(
            cr, uid, ids, obj._name, field, obj._columns[field]._type, context)

        if (not (unicode(last_value) == unicode(vals[field]))
                and any((last_value, vals[field]))):
            message = u'<li><b>%s<b>: %s → %s</li>' % \
                (obj._columns[field].string,
                 last_value,
                 vals[field])
        return message

    # pylint: disable=W0106
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        for idx in ids:
            body = '<ul>'
            message = False
            for field in vals:

                if self._columns[field]._type in ('one2many', 'many2many'):
                    is_many = self._columns[field]._type == 'many2many'

                    last_value = is_many and self.get_last_value(
                        cr, uid, idx, self._name, field, 'many2many', context)
                    field_str = self._columns[field].string
                    n_obj = self._columns[field]._obj
                    message = self.prepare_many_info(
                        cr, uid, idx, vals[field], field_str, n_obj,
                        last_value, context)
                    body = len(message.split('\n')) > 2 and '%s\n%s: %s' % (
                        body, field_str, message)

                elif self._columns[field]._type == 'many2one':
                    message = self.prepare_many2one_info(cr, uid, idx,
                                                         self._name,
                                                         field,
                                                         vals,
                                                         context)
                    body = '%s\n%s' % (body, message)

                elif 'many' not in self._columns[field]._type:
                    message = self.prepare_simple_info(
                        cr, uid, idx, self._name, field, vals, context)
                    body = '%s\n%s' % (body, message)

            body = body and '%s\n</ul>' % body
            if body and message:
                self.message_post(cr, uid, [idx], body, _('Changes in Fields'))
        res = super(MessagePostShowAll, self).write(cr, uid, ids, vals,
                                                    context=context)
        return res
