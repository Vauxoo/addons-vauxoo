# coding: utf-8
import threading

from openerp import SUPERUSER_ID
from openerp.osv.orm import except_orm
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger


class TestUserStory(TransactionCase):

    def setUp(self):
        super(TestUserStory, self).setUp()
        self.story = self.registry('user.story')
        self.criterial = self.registry('acceptability.criteria')
        self.project = self.registry('project.project')
        self.user = self.registry('res.users')
        self.data = self.registry('ir.model.data')
        self.message = self.registry('mail.message')
        self.context = {'tracking_disable': True}

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_create_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object(
            cr, uid, 'user_story', 'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create(cr, SUPERUSER_ID, {
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create(cr, SUPERUSER_ID, {
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Try that a user without user story group cannot create an user story
        self.assertRaises(except_orm, self.story.create, cr, user_test_id, {
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            # Adding user story group to the user created
            # previously
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Adding user story group to the user created previously
        self.user.write(cr, SUPERUSER_ID, [user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can create a user story,  this
        # group must allow create user story without problems
        us_create = self.story.create(cr, user_test_id, {
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]
        }, self.context)
        self.assertTrue(
            us_create,
            "An user with user story group manager cannot create an"
            " user story")
        # Test sequence acceptability criteria
        # You create the context manually
        context_ac = self.context.copy()
        us_ac_ids = self.story.browse(cr, user_test_id, us_create)
        ac_l_v = [[us_create, ac.id, False] for ac in us_ac_ids.accep_crit_ids]
        context_ac.update({'accep_crit_ids': ac_l_v})
        seq_ac = self.criterial._get_default_sequence(cr,
                                                      user_test_id,
                                                      context_ac)
        self.assertEqual(seq_ac, 4, 'Sequence should be equal 4')

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_write_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object(cr, uid, 'user_story',
                                                'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create(cr, SUPERUSER_ID, {
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create(cr, SUPERUSER_ID, {
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Creating an user story for try modify
        story_id = self.story.create(cr, SUPERUSER_ID, {
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Try that a user without user story group cannot write an user story
        self.assertRaises(except_orm, self.story.write, cr,
                          user_test_id, [story_id],
                          {
                              'name': 'User Story Test Changed',
                          })
        # Adding user story group to the user created previously
        self.user.write(cr, SUPERUSER_ID, [user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can write a user story,  this
        # group must allow create user story without problems
        self.assertTrue(
            self.story.write(cr, user_test_id, [story_id], {
                'name': 'User Story Test Changed',
                }, self.context),
            "An user with user story group manager cannot write an user story")

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_unlink_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object(cr, uid, 'user_story',
                                                'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create(cr, SUPERUSER_ID, {
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create(cr, SUPERUSER_ID, {
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Creating an user story for try modify
        story_id = self.story.create(cr, SUPERUSER_ID, {
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Try that a user without user story group cannot remove an user story
        self.assertRaises(except_orm, self.story.unlink,
                          cr, user_test_id, [story_id])
        # Adding user story group to the user created previously
        self.user.write(cr, SUPERUSER_ID, [user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can remove a user story,  this
        # group must allow create user story without problems
        self.assertTrue(self.story.unlink(cr, user_test_id, [story_id]),
                        "An user with user story group manager cannot remove "
                        "an user story")

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_copy_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object(cr, uid, 'user_story',
                                                'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create(cr, SUPERUSER_ID, {
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create(cr, SUPERUSER_ID, {
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Creating an user story for try modify
        story_id = self.story.create(cr, SUPERUSER_ID, {
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Try that a user without user story group cannot copy an user story
        self.assertRaises(except_orm, self.story.copy, cr,
                          user_test_id, story_id)
        # Adding user story group to the user created previously
        self.user.write(cr, SUPERUSER_ID, [user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can copy a user story,  this
        # group must allow create user story without problems
        self.assertTrue(
            self.story.copy(cr, user_test_id, story_id, context=self.context),
            "An user with user story group manager cannot remove an"
            " user story")

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_acceptability_criterial_buttons(self):
        cr, uid = self.cr, self.uid
        self.test_create_method()
        threading.currentThread().testing = True
        # Search the user and the user story to change the criterials
        user_id = self.user.search(cr, uid, [('name', '=', 'User Test')])
        story_id = self.story.search(cr, uid,
                                     [('name', '=', 'User Story Test')])
        user_brw = user_id and self.user.browse(cr, uid, user_id[0])
        if not user_brw.email:
            user_brw.write({'email': 'admin@test.com'})
        story_brw = story_id and self.story.browse(cr, uid, story_id[0])

        # Test approve an acceptability criteria with a specific user and chack
        # that the generated message is send by the user who approve.
        approve_user_id = self.user.create(cr, uid, {
            'name': 'Approver User', 'login': 'user_approver',
            'email': 'approver@test.com',
        })
        self.assertTrue(approve_user_id)
        user_brw = self.user.browse(cr, uid, approve_user_id)
        # Adding user story group to the user created previously
        us_manager_group = self.data.get_object(
            cr, uid, 'user_story', 'group_user_story_manager')
        self.user.write(cr, uid, [approve_user_id], {
            'groups_id': [(4, us_manager_group.id)]})

        i = 0
        for criterial in user_brw and story_brw and story_brw.accep_crit_ids:
            if i == 0:
                mes = ('The acceptability criterion %%%(criteria)s%%'
                       ' has been accepted by %%') % dict(
                           criteria=criterial.name)
                self.assertFalse(criterial.accepted)
                self.criterial.approve(cr, user_brw.id, [criterial.id])
                self.assertTrue(criterial.accepted)
                m_id = self.message.search(cr, uid,
                                           [('res_id', '=', story_brw.id),
                                            ('body', 'ilike', mes)])
                self.assertTrue(m_id, "The message was not created")
                msg_data = self.message.read(cr, uid, m_id, [
                    'model', 'author_id', 'create_uid', 'write_uid',
                    'email_from', 'notified_partner_ids', 'partner_ids',
                ])[0]
                self.partner = self.registry('res.partner')
                author_id = msg_data.get('author_id')[0]
                approver_partner = self.user.browse(
                    cr, uid, approve_user_id).partner_id.id
                self.assertEqual(approver_partner, author_id)
                cri_brw = self.criterial.browse(cr, uid, criterial.id)
                self.assertTrue(cri_brw.accepted,
                                "The criterial was not accepted")

            elif i == 1:
                mes = 'Please Review%%%s' % criterial.name
                self.criterial.ask_review(cr, user_brw.id, [criterial.id])
                m_id = self.message.search(cr, uid,
                                           [('res_id', '=', story_brw.id),
                                            ('body', 'ilike', mes)])
                self.assertTrue(m_id, "The message was not created")
            i += 1

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_approve_button(self):
        cr, uid = self.cr, self.uid
        self.test_create_method()
        threading.currentThread().testing = True
        # Search the user and the user story to change the criterials
        user_id = self.user.search(cr, uid, [('name', '=', 'User Test')])
        story_id = self.story.search(cr, uid,
                                     [('name', '=', 'User Story Test')])
        user_brw = user_id and self.user.browse(cr, uid, user_id[0])
        if not user_brw.email:
            user_brw.write({'email': 'admin@test.com'})
        self.story.do_approval(cr, user_id[0], story_id)
