# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import osv, fields
from lxml import etree
from openerp import tools
from openerp.tools.translate import _


class MergeFuseWizard(osv.TransientModel):
    _name = 'merge.fuse.wizard'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(MergeFuseWizard, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar, submenu)
        if context.get('merge_fuse_object'):
            merge_object = self.pool.get('merge.object')
            fuse_data = merge_object.browse(
                cr, uid, context.get('merge_fuse_object'), context)
            all_fields = {}
            xml_form = etree.Element(
                'form', {'string': tools.ustr(fuse_data.name)})
            etree.SubElement(xml_form, 'separator', {
                             'string': _('Records to be consolidated'), 'colspan': '6'})
            # TODO Creating a tree with the selected records, allowing to
            # select which record will be the main
            xml_group3 = etree.SubElement(
                xml_form, 'group', {'col': '2', 'colspan': '4'})
            etree.SubElement(xml_group3, 'button', {
                             'string': 'Close', 'icon': "gtk-close", 'special': 'cancel'})
            etree.SubElement(xml_group3, 'button', {
                             'string': 'Apply', 'icon': "gtk-execute",
                             'type': 'object', 'name': "action_apply"})
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
        return result

    def create(self, cr, uid, vals, context=None):
        # TODO: migrate to new api, context will brake everything.
        if context.get('active_model') and context.get('active_ids'):
            active_ids = context.get('active_ids')
            base_id = active_ids[0]
            model_obj = self.pool.get(context.get('active_model'))
            models_obj = self.pool.get('ir.model.fields')
            property_obj = self.pool.get('ir.property')
            related_ids = models_obj.search(cr, uid, [('ttype', 'in', ('many2one', 'one2many',
                                                                       'many2many')),
                                                      ('relation', '=',
                                                       str(context.get('active_model')))])
            can = True
            for related in models_obj.browse(cr, uid, related_ids):
                cr.commit()
                to_unlink = []
                target_ids = []
                target_model = self.pool.get(related.model)
                field_obj = target_model and target_model._columns.get(
                    related.name)
                if isinstance(field_obj, fields.property):
                    property_ids = []
                    for field_id in active_ids:
                        v_reference = '%s,%s' % (
                            context.get('active_model'), field_id)
                        property_ids += property_obj.search(cr, uid,
                                                            [('fields_id', '=', related.id),
                                                             ('value_reference',
                                                              '=', v_reference)],
                                                            context=context)

                    if property_ids:
                        v_ref = '%s,%s' % (
                            context.get('active_model'), base_id)
                        property_obj.write(cr, uid, property_ids,
                                           {
                                               'value_reference': v_ref
                                           },
                                           context=context)
                        continue

                elif isinstance(field_obj, fields.function):
                    if field_obj.store or field_obj._fnct_search:
                        target_ids = target_model.search(
                            cr, uid, [(related.name, 'in', active_ids)])
                    else:
                        continue

                else:
                    target_ids = target_model and  \
                        target_model.search(cr, uid,
                                            [(related.name, 'in', active_ids)])
                    if target_ids:
                        try:
                            if isinstance(field_obj, (fields.many2many, fields.one2many)):
                                target_model.write(
                                    cr, uid, target_ids, {str(related.name): [(4, base_id)]})
                            else:
                                target_model.write(
                                    cr, uid, target_ids, {str(related.name): base_id})
                        except Exception, e:
                            if 'cannot update view' in e.message:
                                continue
                            else:
                                can = False
                cr.commit()
            if can:
                to_unlink = list(set(active_ids) - set([base_id]))
                model_obj.unlink(cr, uid, to_unlink)
                cr.commit()
        result = super(MergeFuseWizard, self).create(cr, uid, {}, context)
        return result

    def action_apply(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}


class MergeEditingWizard(osv.TransientModel):
    _name = 'merge.editing.wizard'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(MergeEditingWizard, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar, submenu)
        if context.get('merge_editing_object'):
            merge_object = self.pool.get('merge.object')
            editing_data = merge_object.browse(
                cr, uid, context.get('merge_editing_object'), context)
            all_fields = {}
            xml_form = etree.Element(
                'form', {'string': tools.ustr(editing_data.name)})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            etree.SubElement(
                xml_group, 'label', {'string': '', 'colspan': '2'})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            model_obj = self.pool.get(context.get('active_model'))
            for field in editing_data.field_ids:
                if field.ttype == "many2many":
                    field_info = model_obj.fields_get(
                        cr, uid, [field.name], context)
                    all_fields[field.name] = field_info[field.name]
                    all_fields["selection_" + field.name] = {'type': 'selection',
                                                             'string':
                                                             field_info[field.name][
                                                                 'string'],
                                                             'selection': [('set', 'Set'),
                                                                           ('remove_m2m',
                                                                            'Remove'),
                                                                           ('add', 'Add')]}
                    xml_group = etree.SubElement(
                        xml_group, 'group', {'colspan': '4'})
                    etree.SubElement(xml_group, 'separator', {
                                     'string': field_info[field.name]['string'], 'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                                     'name': "selection_" + field.name, 'colspan': '2',
                                     'nolabel': '1'})
                    etree.SubElement(xml_group, 'field', {
                                     'name': field.name, 'colspan': '4',
                                     'nolabel': '1',
                                     'attrs': "{'invisible':[('selection_" + field.name + "','=','remove_m2m')]}"})  # noqa
                elif field.ttype == "many2one":
                    field_info = model_obj.fields_get(
                        cr, uid, [field.name], context)
                    if field_info:
                        all_fields["selection_" + field.name] = {'type': 'selection',
                                                                 'string': field_info[field.name]['string'],  # noqa
                                                                 'selection': [('set', 'Set'),
                                                                               ('remove',
                                                                                'Remove')]}
                        all_fields[field.name] = {
                            'type': field.ttype,
                            'string': field.field_description,
                            'relation': field.relation
                        }
                        etree.SubElement(
                            xml_group, 'field',
                            {'name': "selection_" + field.name, 'colspan': '2'})
                        etree.SubElement(xml_group, 'field', {
                                         'name': field.name,
                                         'nolabel': '1',
                                         'colspan': '2',
                                         'attrs': "{'invisible':[('selection_" + field.name + "','=','remove')]}"})  # noqa
                elif field.ttype == "char":
                    field_info = model_obj.fields_get(
                        cr, uid, [field.name], context)
                    all_fields["selection_" + field.name] = {'type': 'selection',
                                                             'string': field_info[field.name]['string'],  # noqa
                                                             'selection': [('set', 'Set'), ('remove', 'Remove')]}  # noqa
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'size': field.size or 256
                    }
                    etree.SubElement(xml_group, 'field', {
                                     'name': "selection_" + field.name,
                                     'colspan': '2',
                                     'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                                     'name': field.name, 'nolabel': '1',
                        'attrs': "{'invisible':[('selection_" + field.name + "','=','remove')]}", 'colspan': '2'})  # noqa : TODO This kind of dicts should be real dicts converted to string not concatenated strings, really ugly and error propen
                elif field.ttype == 'selection':
                    field_info = model_obj.fields_get(
                        cr, uid, [field.name], context)
                    all_fields["selection_" + field.name] = {'type': 'selection',
                                                             'string': field_info[field.name]['string'],  # noqa
                                                             'selection': [('set', 'Set'), ('remove', 'Remove')]}  # noqa
                    field_info = model_obj.fields_get(
                        cr, uid, [field.name], context)
                    etree.SubElement(
                        xml_group, 'field', {'name': "selection_" + field.name, 'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                                     'name': field.name, 'nolabel': '1', 'colspan': '2', 'attrs': "{'invisible':[('selection_" + field.name + "','=','remove')]}"})  # noqa
                    all_fields[field.name] = {
                        'type': field.ttype, 'string': field.field_description,
                        'selection': field_info[field.name]['selection']}
                else:
                    field_info = model_obj.fields_get(
                        cr, uid, [field.name], context)
                    all_fields[field.name] = {
                        'type': field.ttype, 'string': field.field_description}
                    all_fields["selection_" + field.name] = {'type': 'selection',
                                                             'string': field_info[field.name]['string'],  # noqa
                                                             'selection': [('set', 'Set'),
                                                                           ('remove', 'Remove')]}
                    if field.ttype == 'text':
                        xml_group = etree.SubElement(
                            xml_group, 'group', {'colspan': '6'})
                        etree.SubElement(xml_group, 'separator', {
                                         'string': all_fields[field.name]['string'],
                                         'colspan': '2'})
                        etree.SubElement(xml_group, 'field', {
                                         'name': "selection_" + field.name,
                                         'colspan': '2', 'nolabel': '1'})
                        etree.SubElement(xml_group, 'field', {
                                         'name': field.name,
                                         'colspan': '4',
                                         'nolabel': '1',
                                         'attrs': "{'invisible':[('selection_" + field.name + "','=','remove')]}"})  # noqa
                    else:
                        all_fields["selection_" + field.name] = {'type': 'selection',
                                                                 'string': field_info[field.name]['string'],  # noqa
                                                                 'selection': [('set', 'Set'),
                                                                               ('remove',
                                                                                'Remove')]}
                        etree.SubElement(
                            xml_group, 'field', {'name': "selection_" + field.name,
                                                 'colspan': '2', })
                        etree.SubElement(xml_group, 'field', {
                                         'name': field.name,
                                         'nolabel': '1',
                                         'attrs': "{'invisible':[('selection_" + field.name + "','=','remove')]}",  # noqa
                                         'colspan': '2', })

            etree.SubElement(
                xml_form, 'separator', {'string': '', 'colspan': '6'})
            xml_group3 = etree.SubElement(
                xml_form, 'group', {'col': '2', 'colspan': '4'})
            etree.SubElement(xml_group3, 'button', {
                             'string': 'Close', 'icon': "gtk-close", 'special': 'cancel'})
            etree.SubElement(xml_group3, 'button', {
                             'string': 'Apply',
                             'icon': "gtk-execute",
                             'type': 'object',
                             'name': "action_apply"})

            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
        return result

    def create(self, cr, uid, vals, context=None):
        if context.get('active_model') and context.get('active_ids'):
            model_obj = self.pool.get(context.get('active_model'))
            dict = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('_', 1)[1]
                    if val == 'set':
                        dict.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        dict.update({split_key: False})
                    elif val == 'remove_m2m':
                        dict.update({split_key: [(5, 0, [])]})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        dict.update({split_key: m2m_list})
            if dict:
                model_obj.write(
                    cr, uid, context.get('active_ids'), dict, context)
        result = super(MergeEditingWizard, self).create(cr, uid, {}, context)
        return result

    def action_apply(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
