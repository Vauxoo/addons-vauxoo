# coding: utf-8

from openerp import fields, models, api


class SprintKanban(models.Model):

    _inherit = 'sprint.kanban'

    user_story_ids = fields.Many2many('user.story',
                                      'sprin_stories_rel',
                                      'sprint_id',
                                      'story_id',
                                      help='User Stories that belong '
                                      'to this sprint')


class UserStory(models.Model):

    _inherit = 'user.story'

    @api.one
    @api.depends('sprint_ids')
    def _get_last_sprint(self):
        if self.sprint_ids:
            self.sk_id = self.sprint_ids.\
                sorted(key=lambda r: r.datestart)[-1].id

    sprint_ids = fields.Many2many('sprint.kanban',
                                  'sprin_stories_rel',
                                  'story_id',
                                  'sprint_id',
                                  help='Sprints where this User '
                                  'Story was involved')

    sk_id = fields.Many2one('sprint.kanban', 'Sprint Kanban',
                            compute='_get_last_sprint',
                            store=True,
                            help='The last sprint added to this user story')

    @api.one
    def update_sprint_user_story(self):
        us_ids = self.search([('sk_id', '!=', False)])
        for us in us_ids:
            us.write({'sprint_ids': [(4, us.sk_id.id)]})


class AcceptabilityCriteria(models.Model):

    _inherit = 'acceptability.criteria'

    sprint_id = fields.Many2one('sprint.kanban', 'Sprint Kanban',
                                help='Sprint where this criteria was accepted')

    @api.one
    def approve(self):
        res = super(AcceptabilityCriteria, self).approve()
        if self.accep_crit_id.sk_id:
            self.sprint_id = self.accep_crit_id.sk_id.id
        return res
