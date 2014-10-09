from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm
import threading
from openerp.tools import mute_logger

class TestUserStory(TransactionCase):

    def setUp(self):
        super(TestUserStory, self).setUp()
        self.story = self.registry('user.story')
        self.project = self.registry('project.project')
        self.user = self.registry('res.users')
        self.data = self.registry('ir.model.data')
        self.message = self.registry('mail.message')


    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_salesman_configuration_contrac(self):
        cr, uid = self.cr, self.uid
        #Salesman configures portal access
        daniel_user = self.data.get_object(cr, uid, 'portal_user_story', 'user_story_demo_user_1')
        #Validate if salesman does not finish the configuration the customer will not watch the true portal
        project_1 = self.data.get_object(cr, uid, 'project', 'project_project_5')
        self.assertRaises(except_orm, self.project.read, cr, daniel_user.id,
                           project_1.id, [])
        #Salesman configures correctly the portal access setting as follower to the project user
        project_2 = self.data.get_object(cr, uid, 'project', 'project_project_1')
        daniel_brw = self.user.browse(cr, uid, daniel_user.id)
        self.project.write(cr, uid, [project_2.id], {'message_follower_ids':[(4, daniel_brw.partner_id.id)]})
        project_ids = self.project.search(cr, daniel_user.id, [])
        self.assertIn(project_2.id, project_ids, 'An User can not watch a project whose partner is the parent partner of him')


    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_customer_changes_user_story(self):
        cr, uid = self.cr, self.uid
        story_1 = self.data.get_object(cr, uid, 'user_story', 'us_1')
        daniel_user = self.data.get_object(cr, uid, 'portal_user_story', 'user_story_demo_user_1')
        charlie_user = self.data.get_object(cr, uid, 'portal_user_story', 'user_story_demo_user_2')
        threading.currentThread().testing = True
        #If the customer is not owner of the user history, he cannot change it
        self.assertRaises(except_orm, self.story.write, cr, charlie_user.id,
                          [story_1.id], {'name': 'Changed'})

        #If the customer is not owner of the user history, he cannot approve the user story
        self.assertRaises(except_orm, self.story.do_approval, cr, charlie_user.id,
                           [story_1.id])
        #Onlye the owner of the user story can change it and approve it
        self.assertTrue(self.story.do_approval(cr, daniel_user.id, [story_1.id]),
                        "The owner of an user story can not approve it")



