# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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

from lxml import etree
import os
from openerp import addons
from openerp import tools
from openerp.tools import to_xml
from openerp.osv import osv
from openerp.tools.translate import _


class survey_name_wiz(osv.TransientModel):
    _inherit = 'survey.name.wiz'

    def action_next(self, cr, uid, ids, context=None):
        res = super(survey_name_wiz, self).action_next(cr, uid, ids, context)

        res.update({
            'target': 'inline',
        })
        return res


class survey_question_wiz(osv.TransientModel):
    _inherit = 'survey.question.wiz'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """

        if context is None:
            context = {}
        result = super(survey_question_wiz, self).fields_view_get(cr, uid, view_id,
                                        view_type, {}, toolbar, submenu)

        surv_name_wiz = self.pool.get('survey.name.wiz')
        survey_obj = self.pool.get('survey')
        page_obj = self.pool.get('survey.page')
        que_obj = self.pool.get('survey.question')
        sur_response_obj = self.pool.get('survey.response')
        que_col_head = self.pool.get('survey.question.column.heading')
        user_obj = self.pool.get('res.users')

        if view_type in ['form']:
            wiz_id = 0
            sur_name_rec = None
            if 'sur_name_id' in context:
                sur_name_rec = surv_name_wiz.browse(cr, uid, context['sur_name_id'], context=context)
            elif 'survey_id' in context:
                res_data = {
                    'survey_id': context.get('survey_id', False),
                    'page_no': -1,
                    'page': 'next',
                    'transfer': 1,
                    'response': 0
                }
                wiz_id = surv_name_wiz.create(cr, uid, res_data)
                sur_name_rec = surv_name_wiz.browse(cr, uid, wiz_id, context=context)
                context.update({'sur_name_id': wiz_id})

            if context.has_key('active_id'):
                context.pop('active_id')

            survey_id = context.get('survey_id', False)
            if not survey_id:
                # Try one more time to find it
                if sur_name_rec and sur_name_rec.survey_id:
                    survey_id = sur_name_rec.survey_id.id
                else:
                    # raise osv.except_osv(_('Error!'), _("Cannot locate survey for the question wizard!"))
                    # If this function is called without a survey_id in
                    # its context, it makes no sense to return any view.
                    # Just return the default, empty view for this object,
                    # in order to please random calls to this fn().
                    return super(survey_question_wiz, self).\
                        fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                        toolbar=toolbar, submenu=submenu)
            sur_rec = survey_obj.browse(cr, uid, survey_id, context=context)
            p_id = map(lambda x: x.id, sur_rec.page_ids)
            total_pages = len(p_id)
            pre_button = False
            readonly = 0

            if context.get('response_id', False) \
                    and int(context['response_id'][0]) > 0:
                readonly = 1

            if not sur_name_rec.page_no + 1:
                surv_name_wiz.write(cr, uid, [context['sur_name_id'], ], {'store_ans': {}})

            sur_name_read = surv_name_wiz.browse(cr, uid, context['sur_name_id'], context=context)
            page_number = int(sur_name_rec.page_no)
            if sur_name_read.transfer or not sur_name_rec.page_no + 1:
                surv_name_wiz.write(cr, uid, [context['sur_name_id']], {'transfer': False})
                flag = False
                fields = {}
                if sur_name_read.page == "next" or sur_name_rec.page_no == -1:
                    if total_pages > sur_name_rec.page_no + 1:
                        if ((context.has_key('active') and not context.get('active', False))
                                or not context.has_key('active')) and not sur_name_rec.page_no + 1:
                            if sur_rec.state != "open":
                                raise osv.except_osv(_('Warning!'), _("You cannot answer because the survey is not open."))
                            cr.execute('select count(id) from survey_history where user_id=%s\
                                                    and survey_id=%s', (uid, survey_id))
                            res = cr.fetchone()[0]
                            user_limit = survey_obj.browse(cr, uid, survey_id)
                            user_limit = user_limit.response_user
                            if user_limit and res >= user_limit:
                                raise osv.except_osv(_('Warning!'), _("You cannot answer this survey more than %s times.") % (user_limit))

                        if sur_rec.max_response_limit and sur_rec.max_response_limit <= sur_rec.tot_start_survey and not sur_name_rec.page_no + 1:
                            survey_obj.write(cr, uid, survey_id, {'state': 'close', 'date_close': strftime("%Y-%m-%d %H:%M:%S")})

                        p_id = p_id[sur_name_rec.page_no + 1]
                        surv_name_wiz.write(cr, uid, [context['sur_name_id'], ], {'page_no': sur_name_rec.page_no + 1})
                        flag = True
                        page_number += 1
                    if sur_name_rec.page_no > - 1:
                        pre_button = True
                    else:
                        flag = True
                else:
                    if sur_name_rec.page_no != 0:
                        p_id = p_id[sur_name_rec.page_no - 1]
                        surv_name_wiz.write(cr, uid, [context['sur_name_id'], ],
                                            {'page_no': sur_name_rec.page_no - 1})
                        flag = True
                        page_number -= 1

                    if sur_name_rec.page_no > 1:
                        pre_button = True
                if flag:
                    pag_rec = page_obj.browse(cr, uid, p_id, context=context)
                    note = False
                    question_ids = []
                    if pag_rec:
                        title = pag_rec.title
                        note = pag_rec.note
                        question_ids = pag_rec.question_ids
                    else:
                        title = sur_rec.title
                    form = etree.Element('form', {'class': 'bs3 bs3-form-bg bs3-footer', 'string': tools.ustr(title)})
                    section = etree.SubElement(form, 'section', {'class': 'bgvauxoo'})
                    xml_form = etree.SubElement(section, 'div', {'class': 'container'})
                    if context.has_key('active') and context.get('active', False) and context.has_key('edit'):
                        context.update({'page_id': tools.ustr(p_id), 'page_number': sur_name_rec.page_no, 'transfer': sur_name_read.transfer})
                        xml_group3 = etree.SubElement(xml_form, 'group', {'col': '4', 'colspan': '4'})
                        etree.SubElement(xml_group3, 'button', {'string': 'Add Page', 'icon': "gtk-new", 'type': 'object', 'name': "action_new_page", 'context': tools.ustr(context)})
                        etree.SubElement(xml_group3, 'button', {'string': 'Edit Page', 'icon': "gtk-edit", 'type': 'object', 'name': "action_edit_page", 'context': tools.ustr(context)})
                        etree.SubElement(xml_group3, 'button', {'string': 'Delete Page', 'icon': "gtk-delete", 'type': 'object', 'name': "action_delete_page", 'context': tools.ustr(context)})
                        etree.SubElement(xml_group3, 'button', {'string': 'Add Question', 'icon': "gtk-new", 'type': 'object', 'name': "action_new_question", 'context': tools.ustr(context)})

                    # FP Note
                    xml_group = xml_form

                    if context.has_key('response_id') and context.get('response_id', False) \
                            and int(context.get('response_id', 0)[0]) > 0:
                        # TODO: l10n, cleanup this code to make it readable. Or template?
                        xml_group = etree.SubElement(xml_form, 'group', {'col': '40', 'colspan': '4'})
                        record = sur_response_obj.browse(cr, uid, context['response_id'][context['response_no']])
                        etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr('Answer Of :- ' + record.user_id.name + ',  Date :- ' + record.date_create.split('.')[0])), 'align': "0.0"})
                        etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr(" Answer :- " + str(context.get('response_no', 0) + 1) + "/" + str(len(context.get('response_id', 0))))), 'align': "0.0"})
                        if context.get('response_no', 0) > 0:
                            etree.SubElement(xml_group, 'button', {'colspan': "1", 'icon': "gtk-go-back", 'name': "action_forward_previous", 'string': tools.ustr("Previous Answer"), 'type': "object"})
                        if context.get('response_no', 0) + 1 < len(context.get('response_id', 0)):
                            etree.SubElement(xml_group, 'button', {'colspan': "1", 'icon': "gtk-go-forward", 'name': "action_forward_next", 'string': tools.ustr("Next Answer"), 'type': "object", 'context': tools.ustr(context)})

                    if wiz_id:
                        fields["wizardid_" + str(wiz_id)] = {'type': 'char', 'size': 255, 'string': "", 'views': {}}
                        etree.SubElement(xml_form, 'field', {'widget': 'FieldCharBS3', 'invisible': '1', 'name': "wizardid_" + str(wiz_id), 'default': str(lambda *a: 0), 'modifiers': '{"invisible":true}'})

                    if note:
                        xml_group_note = etree.SubElement(xml_form, 'group', {'col': '1', 'colspan': '4'})
                        for que_test in note.split('\n'):
                            etree.SubElement(xml_group_note, 'label', {'string': to_xml(tools.ustr(que_test)), 'align': "0.0"})
                    que_ids = question_ids
                    qu_no = 0

                    for que in que_ids:
                        qu_no += 1
                        que_rec = que_obj.browse(cr, uid, que.id, context=context)
                        separator_string = tools.ustr(qu_no) + "." + tools.ustr(que_rec.question)
                        if ((context.has_key('active') and not context.get('active', False)) or not context.has_key('active')) and que_rec.is_require_answer:
                            star = '*'
                        else:
                            star = ''
                        if context.has_key('active') and context.get('active', False) and \
                                context.has_key('edit'):
                            etree.SubElement(xml_form, 'separator', {'string': star + to_xml(separator_string)})

                            xml_group1 = etree.SubElement(xml_form, 'group', {'col': '2',
                                'colspan': '2'})
                            context.update({'question_id': tools.ustr(que.id), 'page_number': sur_name_rec.page_no, 'transfer': sur_name_read.transfer, 'page_id': p_id})
                            etree.SubElement(xml_group1, 'button', {'string': '', 'icon': "gtk-edit", 'type': 'object', 'name': "action_edit_question", 'context': tools.ustr(context)})
                            etree.SubElement(xml_group1, 'button', {'string': '', 'icon': "gtk-delete", 'type': 'object', 'name': "action_delete_question", 'context': tools.ustr(context)})
                        else:
                            etree.SubElement(xml_form, 'newline')
                            etree.SubElement(xml_form, 'separator', {'string': star + to_xml(separator_string)})

                        ans_ids = que_rec.answer_choice_ids
                        xml_group = etree.SubElement(xml_form, 'group', {'col': '1', 'colspan': '4'})

                        if que_rec.type == 'multiple_choice_only_one_ans':
                            selection = []
                            for ans in ans_ids:
                                selection.append((tools.ustr(ans.id), ans.answer))
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '2', 'colspan': '2'})
                            etree.SubElement(xml_group, 'field', {'nolabel': 'True', 'class': 'dropdown-menus', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_selection"})
                            fields[tools.ustr(que.id) + "_selection"] = {'type': 'selection', 'selection': selection, 'string': "Answer"}

                        elif que_rec.type == 'multiple_choice_multiple_ans':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '4', 'colspan': '4'})
                            for ans in ans_ids:
                                etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id)})
                                fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id)] = {'type': 'boolean', 'string': ans.answer}

                        elif que_rec.type in ['matrix_of_choices_only_one_ans', 'rating_scale']:
                            if que_rec.comment_column:
                                col = "4"
                                colspan = "4"
                            else:
                                col = "2"
                                colspan = "2"
                            xml_group = etree.SubElement(xml_group, 'group', {'col': tools.ustr(col), 'colspan': tools.ustr(colspan)})
                            for row in ans_ids:
                                etree.SubElement(xml_group, 'newline')
                                etree.SubElement(xml_group, 'field', {'nolabel': 'True', 'readonly': str(readonly), 'class': 'dropdown-menus', 'name': tools.ustr(que.id) + "_selection_" + tools.ustr(row.id), 'string': to_xml(tools.ustr(row.answer))})
                                selection = [('', '')]
                                for col in que_rec.column_heading_ids:
                                    selection.append((str(col.id), col.title))
                                fields[tools.ustr(que.id) + "_selection_" + tools.ustr(row.id)] = {'type': 'selection', 'selection': selection, 'string': "Answer"}
                                if que_rec.comment_column:
                                    fields[tools.ustr(que.id) + "_commentcolumn_" + tools.ustr(row.id) + "_field"] = {'type': 'char', 'size': 255, 'string': tools.ustr(que_rec.column_name), 'views': {}}
                                    etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_commentcolumn_" + tools.ustr(row.id) + "_field"})

                        elif que_rec.type == 'matrix_of_choices_only_multi_ans':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': str(len(que_rec.column_heading_ids) + 1), 'colspan': '4'})
                            etree.SubElement(xml_group, 'separator', {'string': '.', 'colspan': '1'})
                            for col in que_rec.column_heading_ids:
                                etree.SubElement(xml_group, 'separator', {'string': tools.ustr(col.title), 'colspan': '1'})
                            for row in ans_ids:
                                etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr(row.answer)) + ' :-', 'align': '0.0'})
                                for col in que_col_head.browse(cr, uid, [head.id for head in que_rec.column_heading_ids]):
                                    etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'name': tools.ustr(que.id) + "_" + tools.ustr(row.id) + "_" + tools.ustr(col.id), 'nolabel': "1"})
                                    fields[tools.ustr(que.id) + "_" + tools.ustr(row.id) + "_" + tools.ustr(col.id)] = {'type': 'boolean', 'string': col.title}

                        elif que_rec.type == 'matrix_of_drop_down_menus':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': str(len(que_rec.column_heading_ids) + 1), 'colspan': '4'})
                            etree.SubElement(xml_group, 'separator', {'string': '.', 'colspan': '1'})
                            for col in que_rec.column_heading_ids:
                                etree.SubElement(xml_group, 'separator', {'string': tools.ustr(col.title), 'colspan': '1'})
                            for row in ans_ids:
                                etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr(row.answer)) + ' :-', 'align': '0.0'})
                                for col in que_rec.column_heading_ids:
                                    selection = []
                                    if col.menu_choice:
                                        for item in col.menu_choice.split('\n'):
                                            if item and not item.strip() == '':
                                                selection.append((item, item))
                                    etree.SubElement(xml_group, 'field', {'nolabel': 'True', 'class': 'dropdown-menus', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_" + tools.ustr(row.id) + "_" + tools.ustr(col.id), 'nolabel': '1'})
                                    fields[tools.ustr(que.id) + "_" + tools.ustr(row.id) + "_" + tools.ustr(col.id)] = {'type': 'selection', 'string': col.title, 'selection': selection}

                        elif que_rec.type == 'multiple_textboxes':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '4', 'colspan': '4'})
                            type = "char"
                            if que_rec.is_validation_require:
                                if que_rec.validation_type in ['must_be_whole_number']:
                                    type = "integer"
                                elif que_rec.validation_type in ['must_be_decimal_number']:
                                    type = "float"
                                elif que_rec.validation_type in ['must_be_date']:
                                    type = "date"
                            for ans in ans_ids:
                                etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'width': "300", 'colspan': '1', 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"})
                                if type == "char":
                                    fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"] = {'type': 'char', 'size': 255, 'string': ans.answer}
                                else:
                                    fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"] = {'type': str(type), 'string': ans.answer}

                        elif que_rec.type == 'numerical_textboxes':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '4', 'colspan': '4'})
                            for ans in ans_ids:
                                etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'width': "300", 'colspan': '1', 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_numeric"})
                                fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_numeric"] = {'type': 'integer', 'string': ans.answer}

                        elif que_rec.type == 'date':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '4', 'colspan': '4'})
                            for ans in ans_ids:
                                etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'width': "300", 'colspan': '1', 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id)})
                                fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id)] = {'type': 'date', 'string': ans.answer}

                        elif que_rec.type == 'date_and_time':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '4', 'colspan': '4'})
                            for ans in ans_ids:
                                etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'width': "300", 'colspan': '1', 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id)})
                                fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id)] = {'type': 'datetime', 'string': ans.answer}

                        elif que_rec.type == 'descriptive_text':
                            if que_rec.descriptive_text:
                                for que_test in que_rec.descriptive_text.split('\n'):
                                    etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr(que_test)), 'align': "0.0"})

                        elif que_rec.type == 'single_textbox':
                            etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_single", 'nolabel': "1", 'colspan': "4"})
                            fields[tools.ustr(que.id) + "_single"] = {'type': 'char', 'size': 255, 'string': "single_textbox", 'views': {}}

                        elif que_rec.type == 'comment':
                            etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'name': tools.ustr(que.id) + "_comment", 'nolabel': "1", 'colspan': "4"})
                            fields[tools.ustr(que.id) + "_comment"] = {'type': 'text', 'string': "Comment/Eassy Box", 'views': {}}

                        elif que_rec.type == 'table':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': str(len(que_rec.column_heading_ids)), 'colspan': '4'})
                            for col in que_rec.column_heading_ids:
                                etree.SubElement(xml_group, 'separator', {'string': tools.ustr(col.title), 'colspan': '1'})
                            for row in range(0, que_rec.no_of_rows):
                                for col in que_rec.column_heading_ids:
                                    etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_table_" + tools.ustr(col.id) + "_" + tools.ustr(row), 'nolabel': "1"})
                                    fields[tools.ustr(que.id) + "_table_" + tools.ustr(col.id) + "_" + tools.ustr(row)] = {'type': 'char', 'size': 255, 'views': {}}

                        elif que_rec.type == 'multiple_textboxes_diff_type':
                            xml_group = etree.SubElement(xml_group, 'group', {'col': '4', 'colspan': '4'})
                            for ans in ans_ids:
                                if ans.type == "email":
                                    fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"] = {'type': 'char', 'size': 255, 'string': ans.answer}
                                    etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'widget': 'email', 'width': "300", 'colspan': '1', 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"})
                                else:
                                    etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'width': "300", 'colspan': '1', 'name': tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"})
                                    if ans.type == "char":
                                        fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"] = {'type': 'char', 'size': 255, 'string': ans.answer}
                                    elif ans.type in ['integer', 'float', 'date', 'datetime']:
                                        fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"] = {'type': str(ans.type), 'string': ans.answer}
                                    else:
                                        selection = []
                                        if ans.menu_choice:
                                            for item in ans.menu_choice.split('\n'):
                                                if item and not item.strip() == '':
                                                    selection.append((item, item))
                                        fields[tools.ustr(que.id) + "_" + tools.ustr(ans.id) + "_multi"] = {'type': 'selection', 'selection': selection, 'string': ans.answer}

                        if que_rec.type in ['multiple_choice_only_one_ans', 'multiple_choice_multiple_ans', 'matrix_of_choices_only_one_ans', 'matrix_of_choices_only_multi_ans', 'matrix_of_drop_down_menus', 'rating_scale'] and que_rec.is_comment_require:
                            if que_rec.type in ['multiple_choice_only_one_ans', 'multiple_choice_multiple_ans'] and que_rec.comment_field_type in ['char', 'text'] and que_rec.make_comment_field:
                                etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_otherfield", 'colspan': "4"})
                                fields[tools.ustr(que.id) + "_otherfield"] = {'type': 'boolean', 'string': que_rec.comment_label, 'views': {}}
                                if que_rec.comment_field_type == 'char':
                                    etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_other", 'nolabel': "1", 'colspan': "4"})
                                    fields[tools.ustr(que.id) + "_other"] = {'type': 'char', 'string': '', 'size': 255, 'views': {}}
                                elif que_rec.comment_field_type == 'text':
                                    etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'name': tools.ustr(que.id) + "_other", 'nolabel': "1", 'colspan': "4"})
                                    fields[tools.ustr(que.id) + "_other"] = {'type': 'text', 'string': '', 'views': {}}
                            else:
                                if que_rec.comment_field_type == 'char':
                                    etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr(que_rec.comment_label)), 'colspan': "4"})
                                    etree.SubElement(xml_group, 'field', {'widget': 'FieldCharBS3', 'readonly': str(readonly), 'name': tools.ustr(que.id) + "_other", 'nolabel': "1", 'colspan': "4"})
                                    fields[tools.ustr(que.id) + "_other"] = {'type': 'char', 'string': '', 'size': 255, 'views': {}}
                                elif que_rec.comment_field_type == 'text':
                                    etree.SubElement(xml_group, 'label', {'string': to_xml(tools.ustr(que_rec.comment_label)), 'colspan': "4"})
                                    etree.SubElement(xml_group, 'field', {'readonly': str(readonly), 'name': tools.ustr(que.id) + "_other", 'nolabel': "1", 'colspan': "4"})
                                    fields[tools.ustr(que.id) + "_other"] = {'type': 'text', 'string': '', 'views': {}}

                    xml_footer = etree.SubElement(xml_form, 'footer', {'col': '8', 'colspan': '1', 'width': "100%"})

                    if pre_button:
                        etree.SubElement(xml_footer, 'label', {'string': ""})
                        etree.SubElement(xml_footer, 'button', {'name': "action_previous", 'string': "e", 'type': "object", 'class': "answer_exit btn btn-primary btn-large oe_e"})
                    but_string = "Next"
                    if int(page_number) + 1 == total_pages:
                        but_string = "Done"
                    if context.has_key('active') and context.get('active', False) and int(page_number) + 1 == total_pages and context.has_key('response_id') and context.has_key('response_no') and context.get('response_no', 0) + 1 == len(context.get('response_id', 0)):
                        etree.SubElement(xml_footer, 'label', {'string': ""})
                        etree.SubElement(xml_footer, 'button', {'special': 'cancel', 'string': tools.ustr("Done"), 'context': tools.ustr(context), 'class': "oe_highlight"})
                    elif context.has_key('active') and context.get('active', False) and int(page_number) + 1 == total_pages and context.has_key('response_id'):
                        etree.SubElement(xml_footer, 'label', {'string': ""})
                        etree.SubElement(xml_footer, 'button', {'name': "action_forward_next", 'string': tools.ustr("Next Answer"), 'type': "object", 'context': tools.ustr(context), 'class': "oe_highlight"})
                    elif context.has_key('active') and context.get('active', False) and int(page_number) + 1 == total_pages:
                        etree.SubElement(xml_footer, 'label', {'string': ""})
                        etree.SubElement(xml_footer, 'button', {'special': "cancel", 'string': 'Done', 'context': tools.ustr(context), 'class': "answer_exit btn btn-primary btn-large"})
                    else:
                        etree.SubElement(xml_footer, 'label', {'string': ""})
                        etree.SubElement(xml_footer, 'button', {'class': "btn btn-primary btn-large oe_e", 'name': "action_next", 'string': but_string == 'Next'and '/' or '8', 'type': "object", 'context': tools.ustr(context)})
                    etree.SubElement(xml_footer, 'button', {'special': "cancel", 'string': "c", 'class': "answer_exit btn btn-primary btn-large oe_e"})
                    etree.SubElement(xml_footer, 'label', {'string': tools.ustr(page_number + 1) + "/" + tools.ustr(total_pages), 'class': "oe_survey_title_page oe_right"})

                    root = form.getroottree()
                    result['arch'] = etree.tostring(root)
                    result['fields'] = fields
                    print 'rooooooooot', etree.tostring(root)
                    print 'fields', fields
                    result['context'] = context
                else:
                    survey_obj.write(cr, uid, survey_id, {'tot_comp_survey': sur_rec.tot_comp_survey + 1})
                    sur_response_obj.write(cr, uid, [sur_name_read.response], {'state': 'done'})

                    # mark the survey request as done; call 'survey_req_done' on its actual model
                    survey_req_obj = self.pool.get(context.get('active_model'))
                    if survey_req_obj and hasattr(survey_req_obj, 'survey_req_done'):
                        survey_req_obj.survey_req_done(cr, uid, context.get('active_ids', []), context=context)

                    if sur_rec.send_response:
                        survey_data = survey_obj.browse(cr, uid, survey_id)
                        response_id = surv_name_wiz.read(cr, uid, context.get('sur_name_id', False))['response']
                        self.create_report(cr, uid, [survey_id], 'report.survey.browse.response', survey_data.title, context)
                        attachments = {}
                        pdf_filename = addons.get_module_resource('survey', 'report') + survey_data.title + ".pdf"
                        if os.path.exists(pdf_filename):
                            file = open(pdf_filename)
                            file_data = ""
                            while 1:
                                line = file.readline()
                                file_data += line
                                if not line:
                                    break

                            attachments[survey_data.title + ".pdf"] = file_data
                            file.close()
                            os.remove(addons.get_module_resource('survey', 'report') + survey_data.title + ".pdf")
                        context.update({'response_id': response_id})
                        user_email = user_obj.browse(cr, uid, uid, context).email
                        resp_email = survey_data.responsible_id and survey_data.responsible_id.email or False

                        if user_email and resp_email:
                            user_name = user_obj.browse(cr, uid, uid, context=context).name
                            mail = "Hello " + survey_data.responsible_id.name + ",\n\n " + str(user_name) + " has given the Response Of " + survey_data.title + " Survey.\nThe Response has been attached herewith.\n\n Thanks."
                            vals = {'state': 'outgoing',
                                    'subject': "Survey Answer Of " + user_name,
                                    'body_html': '<pre>%s</pre>' % mail,
                                    'email_to': [resp_email],
                                    'email_from': user_email}
                            if attachments:
                                vals['attachment_ids'] = [(0, 0, {'name': a_name,
                                                                'datas_fname': a_name,
                                                                'datas': str(a_content).encode('base64')})
                                                          for a_name, a_content in attachments.items()]
                            self.pool.get('mail.mail').create(cr, uid, vals, context=context)

                    xml_form = etree.Element('form', {'string': _('Complete Survey Answer')})
                    xml_footer = etree.SubElement(xml_form, 'footer', {'col': '6', 'colspan': '4', 'class': 'oe_survey_title_height'})

                    etree.SubElement(xml_form, 'separator', {'string': 'Survey Completed', 'colspan': "4"})
                    etree.SubElement(xml_form, 'label', {'string': 'Thanks for your Answer'})
                    etree.SubElement(xml_form, 'newline')
                    etree.SubElement(xml_footer, 'button', {'special': "cancel", 'string': "OK", 'colspan': "2", 'class': 'oe_highlight'})
                    root = xml_form.getroottree()
                    result['arch'] = etree.tostring(root)
                    result['fields'] = {}
                    result['context'] = context
        return result

    def action_next(self, cr, uid, ids, context=None):
        res = super(survey_question_wiz, self).action_next(cr, uid, ids, context)

        res.update({
            'target': 'inline',
        })
        return res
