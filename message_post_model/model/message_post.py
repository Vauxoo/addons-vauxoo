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

from openerp import models, api, _


class MessagePostShowAll(models.Model):

    """With this object you can add an extensive log in your model like the
    traditional message log don't does
    You need do it the following way:
        _name = "account.invoice"
        _inherit = ['account.invoice', 'message.post.show.all']

    """

    _name = 'message.post.show.all'
    _inherit = ['mail.thread']

    # pylint: disable=W0622
    @api.model
    def get_last_value(self, ids, model=None, field=None,
                       fieldtype=None):
        """Return the last value of a record in the model to show a post with the
        change
        @param ids: int with id record
        @param model: String with model name
        @param field: Name field to return his value

        return the value of the field
        """

        field = ids and field or []
        model_obj = self.env[model]
        model_brw = model_obj.browse(ids)
        if 'many2one' in fieldtype:
            value = field and model_brw[field] and \
                model_brw[field].name_get() or ''
            value = value and value[0][1]
        elif 'many2many' in fieldtype:
            value = [i.id for i in model_brw[field]]
        else:
            value = field and model_brw[field] or ''

        return field and value or ''

    @api.model
    def prepare_many_info(self, ids, records, string, n_obj,
                          last=None):
        info = {
            0: _('Created New Line'),
            1: _('Updated Line'),
            2: _('Removed Line'),
            3: _('Removed Line'),
            6: _('many2many'),
        }
        message = '<ul>'
        obj = self.env[n_obj]
        r_name = obj._rec_name
        mes = False
        last = last or []
        for val in records:
            if val and info.get(val[0], False):
                if val[0] == 0:
                    value = val[2]
                    message = '%s\n<li><b>%s<b>: %s</li>' % \
                        (self.get_encode_value(message),
                         self.get_encode_value(info.get(val[0])),
                         self.get_encode_value(value.get(r_name)))
                elif val[0] in (2, 3):
                    model_brw = obj.browse(val[1])
                    last_value = model_brw.name_get()
                    last_value = last_value and last_value[0][1]
                    value = val[1]
                    message = '%s\n<li><b>%s<b>: %s</li>' % \
                        (self.get_encode_value(message),
                         self.get_encode_value(info.get(val[0])),
                         self.get_encode_value(last_value))

                elif val[0] == 6:
                    lastv = list(set(val[2]) - set(last))
                    new = list(set(last) - set(val[2]))
                    add = _('Added')
                    delete = _('Deleted')
                    if lastv and not new:
                        dele = [obj.browse(i).name_get()[0][1]
                                for i in lastv]
                        mes = ' - '.join(dele)
                        message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                            (self.get_encode_value(message),
                             self.get_encode_value(add),
                             self.get_encode_value(string),
                             self.get_encode_value(mes))
                    if not lastv and new:

                        dele = [obj.browse(i).name_get()[0][1] for i in new]
                        mes = '-'.join(dele)
                        message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                            (self.get_encode_value(message),
                             self.get_encode_value(delete),
                             self.get_encode_value(string),
                             self.get_encode_value(mes))

                elif val[0] == 1:
                    vals = val[2]
                    id_line = 0
                    for field in vals:
                        if obj._fields[field].type in \
                                ('one2many', 'many2many'):
                            is_many = obj._fields[field].type == 'many2many'

                            last_value = is_many and self.get_last_value(
                                val[1], n_obj, field, 'many2many')
                            field_str = self.get_string_by_field(obj, field)
                            new_n_obj = obj._fields[field].comodel_name
                            mes = self.prepare_many_info(val[1],
                                                         vals[field],
                                                         field_str,
                                                         new_n_obj,
                                                         last_value)

                        elif obj._fields[field].type == 'many2one':
                            mes = self.prepare_many2one_info(val[1],
                                                             n_obj,
                                                             field,
                                                             vals)

                        elif 'many' not in obj._fields[field].type:
                            mes = self.prepare_simple_info(val[1],
                                                           n_obj, field,
                                                           vals)
                        if mes and mes != '<p>':
                            message = id_line != val[1] and \
                                _('%s\n<h3>Line %s</h3>' % (message, val[1])) \
                                or message
                            message = '%s\n%s' % \
                                (self.get_encode_value(message),
                                 mes)
                            id_line = val[1]

        message = '%s\n</ul>' % self.get_encode_value(message)
        return message

    @api.model
    def get_string_by_field(self, source_obj, field):
        """Get the string of a field using fields_get method to
        get the string depending of the user lang

        @param source_obj: Model that contains the field
        @type source_obj: RecordSet
        @param field: Database name of the field
        @type field: str or unicode

        @returns: String of the field shown in the views
        @rtype: str
        """
        description = source_obj.fields_get([field])
        description = description and description.get(field, {})
        description = description and description.get('string', '') or ''
        return description.encode('utf-8', 'ignore')

    @api.model
    def prepare_many2one_info(self, ids, n_obj, field, vals):
        obj = self.env[n_obj]
        message = '<p>'

        last_value = self.get_last_value(
            ids, obj._name, field, obj._fields[field].type)
        model_obj = self.env[obj._fields[field].comodel_name]
        model_brw = model_obj.browse(vals[field])
        new_value = model_brw.name_get()
        new_value = new_value and new_value[0][1]

        if not (last_value == new_value) and any((new_value, last_value)):
            message = '<li><b>%s<b>: %s → %s</li>' % \
                (self.get_string_by_field(obj, field),
                 self.get_encode_value(last_value),
                 self.get_encode_value(new_value))
        return message

    @staticmethod
    def get_encode_value(value):
        """Encode string values to avoid unicode errors
        @param value: Any object to try encode the value
        @type value: str bool date
        """
        val = value
        if isinstance(value, (unicode)):
            val = value.encode('utf-8', 'ignore')
        return val

    @api.model
    def prepare_simple_info(self, ids, n_obj, field,
                            vals):
        obj = self.env[n_obj]
        message = '<p>'
        last_value = self.get_last_value(
            ids, obj._name, field, obj._fields[field].type)

        if ((self.get_encode_value(last_value) !=
             self.get_encode_value(vals[field])) and
                any((last_value, vals[field]))):
            message = '<li><b>%s<b>: %s → %s</li>' % \
                (self.get_string_by_field(obj, field),
                 self.get_encode_value(last_value),
                 self.get_encode_value(vals[field]))
        return message

    # pylint: disable=W0106
    @api.multi
    def write(self, vals):
        for idx in self:
            body = '<ul>'
            message = False
            for field in vals:

                if self._fields[field].type in ('one2many', 'many2many'):
                    is_many = self._fields[field].type == 'many2many'

                    last_value = is_many and self.get_last_value(
                        idx.id, self._name, field, 'many2many')
                    field_str = self.get_string_by_field(self, field)
                    n_obj = self._fields[field].comodel_name
                    message = self.prepare_many_info(
                        idx.id, vals[field], field_str, n_obj,
                        last_value)
                    body = len(message.split('\n')) > 2 and '%s\n%s: %s' % (
                        body, field_str, message)

                elif self._fields[field].type == 'many2one':
                    message = self.prepare_many2one_info(idx.id,
                                                         self._name,
                                                         field,
                                                         vals)
                    body = '%s\n%s' % (body, message)

                elif 'many' not in self._fields[field].type:
                    message = self.prepare_simple_info(
                        idx.id, self._name, field, vals)
                    body = '%s\n%s' % (body, message)

            body = body and '%s\n</ul>' % body
            if body and message:
                idx.message_post(body, _('Changes in Fields'))
        res = super(MessagePostShowAll, self).write(vals)
        return res
