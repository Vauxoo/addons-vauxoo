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

from openerp import models, api, _, fields, SUPERUSER_ID
from openerp.exceptions import Warning as UserError


def get_last_value(self, ids, model=None, field=None,
                   fieldtype=None):
    """Return the last value of a record in the model to show a post
    with the change
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


def prepare_many_info(self, ids, records, string, n_obj, exclude_names,
                      last=None):
    """Generated the message when there are changes in many records
    related with the main record(*2many fields)
    @param ids: Identifiers of the record to be changed
    @type ids: integer
    @param records: Details of the change
    @type records: list of tuples
    @param string: name of the field to be changed
    @type string: str or unicode
    @param n_obj: Name of the object
    @type n_obj: str or unicode
    @param exclude_names: Fields to be exclude in the message
    @type exclude_names: list of str
    @param last: Last change for this field
    @type last: type of the field
    @return: The message of the changes
    @rtype: str
    """
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
    mes = ''
    last = last or []
    for val in records:
        if val and info.get(val[0], False):
            if val[0] == 0:
                value = val[2]
                message = '%s\n<li><b>%s<b>: %s</li>' % \
                    (get_encode_value(message),
                        get_encode_value(info.get(val[0])),
                        get_encode_value(value.get(r_name)))
            elif val[0] in (2, 3):
                model_brw = obj.browse(val[1])
                last_value = model_brw.name_get()
                last_value = last_value and last_value[0][1]
                value = val[1]
                message = '%s\n<li><b>%s<b>: %s</li>' % \
                    (get_encode_value(message),
                        get_encode_value(info.get(val[0])),
                        get_encode_value(last_value))

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
                        (get_encode_value(message),
                            get_encode_value(add),
                            get_encode_value(string),
                            get_encode_value(mes))
                if not lastv and new:

                    dele = [obj.browse(i).name_get()[0][1]
                            for i in new]
                    mes = '-'.join(dele)
                    message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                        (get_encode_value(message),
                            get_encode_value(delete),
                            get_encode_value(string),
                            get_encode_value(mes))

            elif val[0] == 1:
                vals = val[2]
                id_line = 0
                for field in vals:
                    if field in exclude_names:
                        continue
                    if obj._fields[field].type in \
                            ('one2many', 'many2many'):
                        is_many = \
                            obj._fields[field].type == 'many2many'

                        last_value = is_many and \
                            get_last_value(self, val[1], n_obj, field,
                                           'many2many')
                        field_str = get_string_by_field(obj, field)
                        new_n_obj = obj._fields[field].comodel_name
                        mes = prepare_many_info(self, val[1],
                                                vals[field], field_str,
                                                new_n_obj,
                                                exclude_names,
                                                last_value)

                    elif obj._fields[field].type == 'many2one':
                        mes = prepare_many2one_info(self, val[1],
                                                    n_obj, field, vals)

                    elif 'many' not in obj._fields[field].type:
                        mes = prepare_simple_info(self, val[1], n_obj, field,
                                                  vals)
                    if mes and mes != '<p>':
                        message = id_line != val[1] and \
                            _('%s\n<h3>Line %s</h3>' %
                                (message, val[1])) \
                            or message
                        message = '%s\n%s' % \
                            (get_encode_value(message),
                                mes)
                        id_line = val[1]

    message = '%s\n</ul>' % get_encode_value(message)
    return message


def get_selection_value(source_obj, field, value):
    """Get the string of a selection field using
    fields_get method to get the string

    @param source_obj: Model that contains the field
    @type source_obj: RecordSet
    @param field: Database name of the field
    @type field: str or unicode
    @param value: Database value used to find its the
                string in the selection
    @type value: str or unicode

    @returns: String shown in the selection field
    @rtype: str
    """
    val = source_obj.fields_get([field])
    val = val and val.get(field, {})
    val = val and val.get('selection', ()) or ()
    val = [i[1] for i in val if value in i]
    val = val and val[0] or ''
    return val.encode('utf-8', 'ignore')


def get_string_by_field(source_obj, field):
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


def prepare_many2one_info(self, ids, n_obj, field, vals):
    """Generate the message when many2one fields in the record are changed
    @param ids: Identifiers of the record to be changed
    @type ids: integer
    @param n_obj: Name of the object
    @type n_obj: str or unicode
    @param field: name of the field to be changed
    @type field: str or unicode
    @param vals: Values of the record to be changed
    @type vals: dict
    @return: The message of the changes
    @rtype: str
    """
    obj = self.env[n_obj]
    message = '<p>'

    last_value = get_last_value(self,
                                ids, obj._name, field,
                                obj._fields[field].type)
    model_obj = self.env[obj._fields[field].comodel_name]
    model_brw = model_obj.browse(vals[field])
    new_value = model_brw.name_get()
    new_value = new_value and new_value[0][1]

    if not (last_value == new_value) and any((new_value, last_value)):
        message = '<li><b>%s<b>: %s → %s</li>' % \
            (get_string_by_field(obj, field),
                get_encode_value(last_value),
                get_encode_value(new_value))
    return message


def get_encode_value(value):
    """Encode string values to avoid unicode errors
    @param value: Any object to try encode the value
    @type value: str bool date
    @return: Return decode value
    @rtype: str
    """
    val = value
    if isinstance(value, (unicode)):
        val = value.encode('utf-8', 'ignore')
    return val


def prepare_simple_info(self, ids, n_obj, field,
                        vals):
    """Generate the message to be shown when simple fields(without
    relations) are changed
    @param ids: Identifiers of the record to be changed
    @type ids: integer
    @param n_obj: Name of the object
    @type n_obj: str or unicode
    @param field: name of the field to be changed
    @type field: str or unicode
    @param vals: Values of the record to be changed
    @type vals: dict
    @return: The message of the changes
    @rtype: str
    """
    obj = self.env[n_obj]
    message = '<p>'
    last_value = get_last_value(self,
                                ids, obj._name, field,
                                obj._fields[field].type)

    last_value = obj._fields[field].type == 'selection' and \
        get_selection_value(obj, field, last_value) or last_value
    new_value = obj._fields[field].type == 'selection' and \
        get_selection_value(obj, field, vals[field]) or vals[field]
    last_value = get_encode_value(last_value)
    new_value = get_encode_value(new_value)

    message = ((last_value != new_value) and
               any((last_value, vals[field]))) and \
        '<li><b>%s<b>: %s → %s</li>' % \
        (get_string_by_field(obj, field), last_value,
            new_value) or '<p>'
    return message


class IrModel(models.Model):

    _inherit = 'ir.model'

    exclude_field_ids = fields.Many2many('ir.model.fields',
                                         string='Excluded Fields',
                                         help='List of fields that you '
                                         'want to exclude of the traking')
    exclude_fields_text = fields.Char('Exclude External Fields',
                                      help='Name of the fields that you '
                                      'want to exclude but these does '
                                      'not have a directly relation with '
                                      'the model. \nThis text must be the '
                                      'database field name separated by '
                                      '(,) without spaces. '
                                      'E.g. name,date,notes')
    tracked = fields.Boolean('Tracked',
                             help='This field identifies if the fields '
                             'in this models are being tracked')

    def write_track_all(self):

        @api.multi
        def write(self, vals):
            """Added a message in the record with the details of the fields changed
            """
            model = self.env['ir.model'].\
                search([('model', '=', str(self._model))])

            exclude_names = model.exclude_field_ids.mapped('name')
            exclude_names += model.exclude_fields_text and \
                model.exclude_fields_text.split(',') or []
            for idx in self:
                body = '<ul>'
                message = ''
                for field in vals:
                    if field in exclude_names:
                        continue
                    if self._fields[field].type in ('one2many', 'many2many'):
                        is_many = self._fields[field].type == 'many2many'

                        last_value = is_many and \
                            get_last_value(self, idx.id, self._name, field,
                                           'many2many')
                        field_str = get_string_by_field(self, field)
                        n_obj = self._fields[field].comodel_name
                        message = prepare_many_info(self,
                                                    idx.id, vals[field],
                                                    field_str, n_obj,
                                                    exclude_names, last_value)
                        body = len(message.split('\n')) > 2 and \
                            '%s\n%s: %s' % (
                            body, field_str, message) or body

                    elif self._fields[field].type == 'many2one':
                        message = \
                            prepare_many2one_info(self, idx.id, self._name,
                                                  field, vals)
                        body = '%s\n%s' % (body, message)

                    elif 'many' not in self._fields[field].type:
                        message = \
                            prepare_simple_info(self, idx.id, self._name,
                                                field, vals)
                        body = '%s\n%s' % (body, message)

                body = body and '%s\n</ul>' % body
                if body and not body == '<ul>\n</ul>' and \
                        message and hasattr(idx, 'message_post'):
                    idx.message_post(body, _('Changes in Fields'))
            return write.origin(self, vals)
        return write

    @api.multi
    def _add_write_patch_model(self):
        """Patch write method for all instances of this model, This replaces
        the original method.
        The original method is then accessible via ``method.origin``
        """
        for record in self:
            obj = self.env[record.model]
            if not obj._fields.get('message_ids', False):
                raise UserError(_('Warning!'),
                                _('This model does not have a relation '
                                  'with mail.message. For this feature '
                                  'work the model must have at least an '
                                  'inheritance with mail.thread'))
            if not record.tracked:
                obj._patch_method('write', self.write_track_all())
                record.write({'tracked': True})

    @api.multi
    def _remove_patch_model(self):
        """Remove Patch all instances of this model to restore the original
        method
        """
        for record in self:
            obj = self.env[record.model]
            if record.tracked:
                obj._revert_method('write')
                record.write({'tracked': False})

    @api.model_cr
    def _register_hook(self):
        """Modified to wrap the method if the server is restarted
        """
        with api.Environment.manage():
            env = api.Environment(self._cr, SUPERUSER_ID, {})
            models_obj = env['ir.model'].search([('tracked', '=', True)])
            for record in models_obj:
                obj = env[record.model]
                obj._patch_method('write', self.write_track_all())
        return super(IrModel, self)._register_hook()
