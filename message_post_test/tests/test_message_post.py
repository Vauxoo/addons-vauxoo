# coding: utf-8
from openerp.tests.common import TransactionCase
from openerp import SUPERUSER_ID


class TestMessagePost(TransactionCase):

    def setUp(self):
        super(TestMessagePost, self).setUp()
        self.test_models = [('message.post.test', 'message.post.test.line'),
                            ('message.post.test.new.api',
                             'message.post.test.line.new.api')]
        self.user = self.registry('res.users')
        self.message = self.registry('mail.message')

    def test_log_git_flow_message_test(self):
        cr, uid = self.cr, self.uid
        i = 0
        for main_model, line_model in self.test_models:
            i += 1
            message_test = self.registry(main_model)
            message_test_line = self.registry(line_model)
            user_id_field = message_test._fields.get('user_id').string
            number_field = message_test._fields.get('number').string
            line_ids_field = message_test._fields.get('line_ids').string
            user_ids_field = message_test._fields.get('user_ids').string
            check_field = message_test._fields.get('check').string
            user_1 = self.user.create(cr, uid,
                                      {'name': 'Test 1',
                                       'login': 'test%s' % str(1 + i)})
            user_2 = self.user.create(cr, uid,
                                      {'name': 'Test 2',
                                       'login': 'test%s' % str(8 + i)})
            message_test_id = message_test.create(cr, uid, {
                'name': 'Test Message',
                'user_id': SUPERUSER_ID,
                'check': True,
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
            message_test.write(cr, uid, [message_test_id], {
                'check': False,
                'number': 78,
                'user_id': user_1,
                'line_ids': [
                    (0, 0, {'name': 'Test 5'}),
                    (0, 0, {'name': 'Test 6'}),
                ]})

            message_ids = self.message.search(
                cr, uid, [
                    ('res_id', '=', message_test_id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + check_field + '%'),
                    ('body', 'ilike', '%' + number_field + '%'),
                    ('body', 'ilike', '%' + user_id_field + '%'),
                    ('body', 'ilike', '%' + line_ids_field +
                     '%Created New Line%'),
                    ('body', 'ilike', '%' + 'False' + '%'),
                    ('body', 'ilike', '%' + '78' + '%'),
                    ('body', 'ilike', '%' + 'Test 1' + '%'),
                    ('body', 'ilike', '%' + 'Test 5' + '%'),
                    ('body', 'ilike', '%' + 'Test 6' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    1,
                                    "The last changes were not registred")
            # Updating lines and remove one of them
            line_ids = message_test_line.search(cr, uid, [])
            message_test.write(cr, uid, [message_test_id], {
                'line_ids': [
                    (1, line_ids[0], {'name': 'Test Update'}),
                    (2, line_ids[1]),
                ]})

            message_ids = self.message.search(
                cr, uid, [
                    ('res_id', '=', message_test_id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + line_ids_field + '%'),
                    ('body', 'ilike', '%' + 'Test Update' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    1,
                                    "The last changes were not registred")

            # Removing an element of a many2many field

            message_test.write(cr, uid, [message_test_id], {
                'user_ids': [
                    (6, 0, [SUPERUSER_ID, user_2]),
                ]})

            message_ids = self.message.search(
                cr, uid, [
                    ('res_id', '=', message_test_id),
                    ('model', '=', main_model),
                    ('body', 'ilike', '%' + user_ids_field + '%Deleted%'),
                    ('body', 'ilike', '%' + 'Test 1' + '%'),
                ])

            self.assertGreaterEqual(len(message_ids),
                                    1,
                                    "The last changes were not registred")
