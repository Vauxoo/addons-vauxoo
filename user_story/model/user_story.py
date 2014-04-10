##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#

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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

import time
import unicodedata

_US_STATE = [('draft', 'New'), ('open', 'In Progress'), (
    'pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]


class user_story(osv.Model):
    """
    OpenERP Model : User Story
    """

    _name = 'user.story'
    _description = 'User Story'
    _inherit = ['mail.thread']

    def _get_tasks(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        task_obj = self.pool.get('project.task')
        for orderpoint in self.browse(cr, uid, ids, context=context):
            task_ids = task_obj.search(cr, uid, [
                                       ('userstory_id', '=', orderpoint.id)])
            result[orderpoint.id] = task_ids
        return result

    def _set_task(self, cr, uid, id, name, value, arg, ctx=None):

        task_ids = self.pool.get('project.task').search(
            cr, uid, [("userstory_id", '=', id)])
        task_id = list(set(value[0][2]) - set(task_ids))
        if task_id:
            for i in task_id:
                sql_str = """UPDATE project_task set
                            userstory_id='%s'
                            WHERE id=%s """ % (id, i)
                cr.execute(sql_str)
        else:
            task_id = list(set(task_ids) - set(value[0][2]))
            for i in task_id:
                    sql_str = """UPDATE project_task set
                                userstory_id=Null
                                WHERE id=%s """ % (i)
                    cr.execute(sql_str)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        task_obj = self.pool.get('project.task')
        
        if vals.get('categ_ids'):
            for tag_id in self.browse(cr, uid, ids, context=context):
                for task in tag_id.task_ids:
                    task_obj.write(cr, uid, [task.id], {'categ_ids': vals['categ_ids']})
                   
        if vals.get('sk_id'):
            task_ids = task_obj.search(cr, uid, [
                                       ('userstory_id', '=', ids[0])])
            task_obj.write(cr, uid, task_ids, {
                           'sprint_id': vals.get('sk_id')}, context=context)

        if 'accep_crit_ids' in vals:
            ac_obj = self.pool.get('acceptability.criteria')
            criteria = [False, False]
            for ac in vals.get('accep_crit_ids'):
                if ac[2] and ac[2].get('accepted', False):
                    if ac[1]:
                        ac_brw = ac_obj.browse(cr, uid, ac[1] , context=context)
                        criteria[1] = ac_brw.name
                    else:
                        criteria[1] = ac[2].get('name', False)
                    
                    body = self.body_criteria(cr, uid, ids, 'template_send_email_hu', criteria[1], context)
                    hu = self.browse(cr, uid, ids[0], context=context)
                    subject = 'Se acepta Criterio de Aceptacion "%s"... en la Historia de Usuario %s' % (criteria[1][:30],hu.id)
                    self.send_mail_hu(cr, uid, ids, subject, body, hu.id, users=False, context=context)
        return super(user_story, self).write(cr, uid, ids,
                                             vals, context=context)
        
    def body_progress(self, cr, uid, ids, template, hu, context=None):
        imd_obj = self.pool.get('ir.model.data')
        template_ids = imd_obj.search(
            cr, uid, [('model', '=', 'email.template'), ('name', '=', template)])
        if template_ids:
            res_id = imd_obj.read(
                cr, uid, template_ids, ['res_id'])[0]['res_id']
            body_html = self.pool.get('email.template').read(
                cr, uid, res_id, ['body_html']).get('body_html')

            user_id = self.pool.get('res.users').browse(cr,uid,[uid],context=context)[0]
            hu = self.browse(cr, uid, ids[0], context=context)

            return body_html
        else:
            return False
        
    def body_criteria(self, cr, uid, ids, template, criteria, context=None):
        imd_obj = self.pool.get('ir.model.data')
        template_ids = imd_obj.search(
            cr, uid, [('model', '=', 'email.template'), ('name', '=', template)])
        if template_ids:
            res_id = imd_obj.read(
                cr, uid, template_ids, ['res_id'])[0]['res_id']
            body_html = self.pool.get('email.template').read(
                cr, uid, res_id, ['body_html']).get('body_html')

            user_id = self.pool.get('res.users').browse(cr,uid,[uid],context=context)[0]
            hu = self.browse(cr, uid, ids[0], context=context)

            body_html = body_html.replace('NAME_OWNER', hu.owner)
            body_html = body_html.replace('NAME_USER', user_id.name)
            body_html = body_html.replace('NAME_CRI', criteria)
            body_html = body_html.replace('NAME_HU', hu.name)
            
            return body_html

        else:
            return False
            

    def send_mail_hu(self, cr, uid, ids, subject, body, res_id, users=[], context=None):
        if not users:
            followers = self.read(cr, uid, ids[0], [
                              'message_follower_ids'])['message_follower_ids']
        else:
            followers = []
            user_obj = self.pool.get('res.users')
            hu = self.browse(cr, uid, res_id, context=context)
            
            owner_name = unicodedata.normalize('NFKD', hu.owner)
            owner_name = owner_name.encode('ASCII','ignore')
            owner_id = user_obj.search(cr, uid, [('name','=',owner_name)], context=context)
            
            if hu.user_id and hu.user_id.partner_id:
                followers.append(hu.user_id.partner_id.id)
            if hu.user_execute_id and hu.user_execute_id.partner_id:
                followers.append(hu.user_execute_id.partner_id.id)
            if owner_id and len(owner_id)==1:
                user_o = user_obj.browse(cr,uid,owner_id,context=context)
                followers.append( user_o[0].partner_id.id)

        context.update({
                        'default_body': body,
                        })
        user_id = self.pool.get('res.users').browse(cr,uid,[uid],context=context)[0]

        mail_mail = self.pool.get('mail.mail')
        mail_id = mail_mail.create(cr, uid,
                   {
                       'model': 'user.story',
                       'res_id': res_id,
                       'subject': subject,
                       'body_html': body,
                       'auto_delete': False,
                       'email_from': user_id.email,
                   }, context=context)
        mail_mail.send(cr, uid, [mail_id],
                       recipient_ids=followers,
                       context=context)


        return False
     
    _columns = {
        'name': fields.char('Title', size=255, required=True, readonly=False,
            translate=True),
        'owner': fields.char('Owner', size=255, required=True, readonly=False),
        'code': fields.char('Code', size=64, readonly=False),
        'planned_hours': fields.float('Planned Hours'),
        'project_id': fields.many2one('project.project', 'Project',
                                      required=True),
        'description': fields.text('Description', translate=True),
        'accep_crit_ids': fields.one2many('acceptability.criteria',
                                          'accep_crit_id',
                                          'Acceptability Criteria',
                                          required=False),
        'info': fields.text('Other Info', translate=True),
        'priority_level':fields.many2one(
            'user.story.priority',
            'Priority Level',
            help=('User story level priority, used to define priority for'
                  ' each user story')), 
        'asumption': fields.text('Assumptions', translate=True),
        'date': fields.date('Date'),
        'user_id': fields.many2one(
            'res.users', 'Responsible Supervisor',
            help=("Person responsible for interacting with the client to give"
                  " details of the progress or completion of the User Story,"
                  " in some cases also the supervisor for the correct"
                  " execution of the user story.")),
        'user_execute_id': fields.many2one('res.users', 'Execution Responsible',help="Person responsible for user story takes place, either by delegating work to other human resource or running it by itself. For delegate work should monitor the proper implementation of associated activities."),
        'sk_id': fields.many2one('sprint.kanban', 'Sprint Kanban'),
        'state': fields.selection(_US_STATE, 'State', readonly=True),
        'task_ids': fields.function(_get_tasks, type='many2many',
                                    relation="project.task",
                                    fnct_inv=_set_task,
                                    string="Tasks",
                                    help="""Draft procurement of
                                            the product and location
                                            of that orderpoint"""),
        'categ_ids': fields.many2many('project.category','project_category_user_story_rel','userstory_id','categ_id', string="Tags"),
        'implementation': fields.text('Implementation Conclusions', translate=True),
    }
    _defaults = {
        'name': lambda *a: None,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, ctx: uid,
        'user_execute_id': lambda self, cr, uid, ctx: uid,
        'state': 'draft',
        'priority_level': lambda self, cr, uid, ctx: self.pool.get(
            'user.story.priority').search(
                cr, uid, [('name', 'like', 'Secondary')], context=ctx)[0]
    }

    def do_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def do_progress(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def do_pending(self, cr, uid, ids, context=None):
        body = self.body_criteria(cr, uid, ids, 'template_send_email_hu_progress', 'hu', context)
        hu_model = self.pool.get('user.story')
        hu = hu_model.browse(cr, uid, ids[0], context=context)
        subject = 'The User Story with ID %s, "%s...", is now in Pending state' % ( hu.id, hu.name[:30] )
        self.send_mail_hu(cr, uid, ids, subject, body, hu.id, users=True, context=context)
        return self.write(cr, uid, ids, {'state': 'pending'}, context=context)

    def do_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def do_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'},
                          context=context)

class user_story_priority(osv.Model):
    """
    User Story Priority Level
    """

    _name = 'user.story.priority'
    _description = "User Story Priority Level"
    _columns = {
        'name': fields.char('Name', size=255, required=True),
    }


class acceptability_criteria(osv.Model):
    """
    OpenERP Model : Acceptability Criteria
    """

    _name = 'acceptability.criteria'
    _description = 'Acceptability Criteria'

    def _get_ac_ids_by_us_ids(self, cr, uid, us_ids, context=None):
        """
        This method is as the method of the sensitive store tuple for the
        functional fields defined in the current field that pretend to pull
        data form the user.story model. The method get us_ids and make a search
        for the acceptability.criteria records that need to be updated.
        @return a list of the acceptability.criteria that need to be updated.
        """
        context = context or {}
        us_obj = self.pool.get('user.story')
        ac_obj = self.pool.get('acceptability.criteria')
        ac_ids = ac_obj.search(
            cr, uid, [('accep_crit_id', 'in', us_ids)], context=context)
        return ac_ids

    def _get_user_story_field(self, cr, uid, ids, fieldname, arg, context=None):
        """
        Method used as the function for extracting values for the user.story
        model using functional fields. This method is used for various fields,
        the fieldname it matters to extract the value, the field name need to
        be the same from the user.story model.
        """
        context = context or {}
        res = {}.fromkeys(ids)
        for ac_brw in self.browse(cr, uid, ids, context=context):
            copy_field = getattr(ac_brw.accep_crit_id, fieldname, False)
            copy_field = copy_field and (isinstance(copy_field, (list)) and [
                elem.id for elem in copy_field ] or copy_field.id) or False
            res[ac_brw.id] = copy_field
        return res

    _columns = {
        'name': fields.char('Title', size=255, required=True, readonly=False,
            translate=True),
        'scenario': fields.text('Scenario', required=True, translate=True),
        'accep_crit_id': fields.many2one('user.story',
                                         'User Story',
                                         required=True),
        'accepted': fields.boolean('Accepted',
                                   help='Check if this criterion apply'),
        'development': fields.boolean('Development'),
        'difficulty': fields.selection(
            [('low','Low'),
             ('medium','Medium'),
             ('high','High'),
             ('na','Not Apply')],
            string='Difficulty'),
        'project_id': fields.function(
            _get_user_story_field,
            type="many2one",
            relation='project.project',
            string='Project',
            help='User Story Project',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['project_id'], 20),
            }),
        'sk_id': fields.function(
            _get_user_story_field,
            type="many2one",
            relation="sprint.kanban",
            string='Sprint',
            help='Sprint Kanban',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['sk_id'], 20),
            }),
        'categ_ids': fields.function(
            _get_user_story_field,
            type="many2one",
            relation="project.category",
            string='Tag',
            help='Tag',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['categ_ids'], 20),
            }),
        'user_id': fields.function(
            _get_user_story_field,
            type="many2one",
            relation="res.users",
            string='Responsible Supervisor',
            help='Responsible Supervisor',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['user_id'], 20),
            }),
        'user_execute_id': fields.function(
            _get_user_story_field,
            type="many2one",
            relation="res.users",
            string='Execution Responsible',
            help='Execution Responsible',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['user_execute_id'], 20),
            }),
    }
    _defaults = {
        'name': lambda *a: None,
        'difficulty': 'na',
    }


class project_task(osv.Model):
    """
    OpenERP Model : Project Task
    """
    _inherit = 'project.task'

    def default_get(self, cr, uid, fields, context=None):
        '''Owerwrite default get to add project in new task automatically'''
        if context is None:
            context = {}
        res = super(project_task, self).default_get(cr, uid, fields, context=context)
        context.get('project_task',False) and \
                res.update({'project_id':context.get('project_task'),'categ_ids':context.get('categ_task'),
                            'sprint_id':context.get('sprint_task'),'userstory_id':context.get('userstory_task')})
        return res
    

    def onchange_user_story_task(self, cr, uid, ids, us_id, context=None):
        v = {}
        us_obj = self.pool.get('user.story')
        if us_id:
            sprint = us_obj.browse(cr, uid, us_id, context=context)
            if sprint.sk_id:
                v['sprint_id'] = sprint.sk_id.id
            categs = us_obj.browse(cr, uid, us_id, context=context)
            if categs.categ_ids:
                v['categ_ids'] = [cat.id for cat in categs.categ_ids]
        return {'value': v}

    _columns = {
        'userstory_id': fields.many2one('user.story', 'User Story',
                                        #domain="[('sk_id', '=', sprint_id)]",
                                        help="Set here the User Story related with this task"),
        'branch_to_clone':fields.char('Branch to clone', 512,
            help='Source branch to be clone and make merge proposal'), 
        
    }
class inherit_project(osv.Model):
    
    '''Inheirt project model to a new Descripcion field'''
    
    _inherit = 'project.project'

    _columns = {
            'descriptions':fields.text('Description',
                help="Reference on what the project is about"),
            }
