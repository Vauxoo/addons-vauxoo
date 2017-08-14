# coding: utf-8
from openerp.tests.common import TransactionCase
from openerp import SUPERUSER_ID


class TestMessagePost(TransactionCase):

    def setUp(self):
        super(TestMessagePost, self).setUp()
        self.test_models = [('message.post.test.new.api',
                             'message.post.test.line.new.api')]
        self.user = self.env['res.users']
        self.message = self.env['mail.message']
        self.trans = self.env['ir.translation']

    def get_string_by_field(self, source_obj, field):
        desc = source_obj.fields_get([field])
        desc = desc and desc.get(field, {})
        desc = desc and desc.get('string', '') or ''
        return desc.encode('utf-8', 'ignore')

    def test_01_log_git_flow_message_test(self):
        """Testing the messages in the test model
        """
        i = 0
        for main_model, line_model in self.test_models:
            i += 1
            ir_model = self.env['ir.model'].\
                search([('model', '=', main_model)])
            ir_model._add_write_patch_model()
            message_test = self.env[main_model]

            message_test_line = self.env[line_model]
            user_id_field = self.get_string_by_field(message_test, 'user_id')
            number_field = self.get_string_by_field(message_test, 'number')
            line_ids_field = self.get_string_by_field(message_test, 'line_ids')
            user_ids_field = self.get_string_by_field(message_test, 'user_ids')
            check_field = self.get_string_by_field(message_test, 'check')
            select_field = self.get_string_by_field(message_test, 'select')
            user_1 = self.user.create({'name': 'Test 1',
                                       'login': 'test%s' % str(1 + i)}).id
            user_2 = self.user.create({'name': 'Test 2 ó%á',
                                       'login': 'test%s' % str(8 + i)}).id
            message_test_id = message_test.create({
                'name': 'Test Message ó%á',
                'user_id': SUPERUSER_ID,
                'check': True,
                'select': '2',
                'number': 56,
                'user_ids': [(6, 0, [user_1, user_2, SUPERUSER_ID])],
                'line_ids': [
                    (0, 0, {'name': 'Test 1', 'number': 2, 'check': True}),
                    (0, 0, {'name': 'Test 2', 'number': 3, 'check': True}),
                    (0, 0, {'name': 'Test 3', 'number': 4, 'check': True}),
                    (0, 0, {'name': 'Test 4', 'number': 5, 'check': True}),
                ],
            })
            # Added new lines and modifitying simples fields
            message_test_id.write({
                'check': False,
                'number': 78,
                'user_id': user_1,
                'select': '1',
                'line_ids': [
                    (0, 0, {'name': 'Test 5 óá%'}),
                    (0, 0, {'name': 'Test 6'}),
                ]})

            message_ids = self.message.search(
                [
                    ('res_id', '=', message_test_id.id),
                    ('model', '=', main_model),
                ])
            term = self.trans._get_source('', 'code',
                                          self.env.user.lang,
                                          source='Created New Line')
            message_ids = self.message.search(
                [
                    ('res_id', '=', message_test_id.id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + check_field + '%'),
                    ('body', 'ilike', '%' + number_field + '%'),
                    ('body', 'ilike', '%' + user_id_field + '%'),
                    ('body', 'ilike', '%' + select_field + '%'),
                    ('body', 'ilike', '%' + line_ids_field +
                     '%' + term + '%'),
                    ('body', 'ilike', '%' + 'False' + '%'),
                    ('body', 'ilike', '%' + '78' + '%'),
                    ('body', 'ilike', '%' + 'Test 1' + '%'),
                    ('body', 'ilike', '%' + 'Test 5' + '%'),
                    ('body', 'ilike', '%' + 'Testing' + '%'),
                    ('body', 'ilike', '%' + 'Test 6' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    1,
                                    "The last changes were not registred")
            # Updating lines and remove one of them
            line_ids = message_test_line.search([])
            message_test_id.write({
                'line_ids': [
                    (1, line_ids.ids[0], {'name': 'Test Update'}),
                    (2, line_ids.ids[1]),
                ]})

            message_ids = self.message.search(
                [
                    ('res_id', '=', message_test_id.id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + line_ids_field + '%'),
                    ('body', 'ilike', '%' + 'Test Update' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    1,
                                    "The last changes were not registred")

            # Removing an element of a many2many field

            message_test_id.write({
                'user_ids': [
                    (6, 0, [SUPERUSER_ID, user_2]),
                ]})

            term = self.trans._get_source('', 'code',
                                          self.env.user.lang,
                                          source='Deleted')
            message_ids = self.message.search(
                [
                    ('res_id', '=', message_test_id.id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + user_ids_field + '%' + term + '%'),
                    ('body', 'ilike', '%' + 'Test 1' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    1,
                                    "The last changes were not registred")
            ir_model._remove_patch_model()
            # Added new lines and modifitying simples fields
            message_test_id.write({
                'number': 200,
                })

            message_ids = self.message.search(
                [
                    ('res_id', '=', message_test_id.id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + number_field + '%'),
                    ('body', 'ilike', '%' + '200' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    0,
                                    "The last change was registred")

    def test_02_log_git_flow_message_lang_test(self):
        """Testing the message with another lang configured
        """
        lang_obj = self.env['res.lang']
        modobj = self.env['ir.module.module']
        lang = 'es_MX'
        lang_ids = lang_obj.search([('code', '=', 'es_PA')])
        if not lang_ids:
            lang_obj.load_lang(lang)
        lang_ids = lang_obj.search([('code', '=', lang)])
        mids = modobj.search([('state', '=', 'installed')])
        context = {'overwrite': True}
        mids.with_context(context).update_translations(lang)
        lang_ids.write(
            {
                'date_format': '%d/%m/%Y',
                'time_format': '%H:%M:%S', 'thousands_sep': ',',
                'decimal_point': '.', 'grouping': '[3,3,3,3,3,3,3,3,-2]'})
        self.env.user.write({'lang': lang})
        self.test_01_log_git_flow_message_test()
