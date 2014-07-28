from openerp.tests.common import TransactionCase
from openerp.exceptions import AccessError
from openerp.osv.orm import except_orm
from openerp import SUPERUSER_ID

class TestUserStory(TransactionCase):

    def setUp(self):
        super(TestUserStory, self).setUp()
        self.story = self.registry('user.story')
        self.project = self.registry('project.project')
        self.user = self.registry('res.users')
        self.data = self.registry('ir.model.data')
        self.message = self.registry('mail.message')


    def test_read_project(self):
        cr, uid = self.cr, self.uid
        daniel_user = self.data.get_object(cr, uid, 'portal_user_story', 'user_story_demo_user_1')
        project_1 = self.data.get_object(cr, uid, 'project', 'project_project_5')
        self.assertRaises(except_orm, self.project.read, cr, daniel_user.id,
                           project_1.id, [])
        project_2 = self.data.get_object(cr, uid, 'project', 'project_project_1')
        project_ids = self.project.search(cr, daniel_user.id, [])
        self.assertIn(project_2.id, project_ids, 'An User can not watch a project whose partner is the parent partner of him')


    def test_write_user_story(self):
        cr, uid = self.cr, self.uid
        story_1 = self.data.get_object(cr, uid, 'user_story', 'us_1')
        daniel_user = self.data.get_object(cr, uid, 'portal_user_story', 'user_story_demo_user_1')
        charlie_user = self.data.get_object(cr, uid, 'portal_user_story', 'user_story_demo_user_2')
        self.assertRaises(except_orm, self.story.write, cr, charlie_user.id,
                          [story_1.id], {'name': 'Changed'})

        self.assertRaises(except_orm, self.story.do_approval, cr, charlie_user.id,
                           [story_1.id])

        self.assertTrue(self.story.do_approval(cr, daniel_user.id, [story_1.id]),
                        "The owner of an user story can not approve it")



