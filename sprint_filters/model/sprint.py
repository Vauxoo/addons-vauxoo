# -*- coding: utf-8 -*-

from openerp import fields, models


class sprint_kanban(models.Model):

    _inherit = 'sprint.kanban'

    user_story_ids = fields.Many2many('user.story',
                                      'sprin_stories_rel',
                                      'sprint_id',
                                      'story_id')


class user_story(models.Model):

    _inherit = 'user.story'

    sprint_ids = fields.Many2many('sprint.kanban',
                                  'sprin_stories_rel',
                                  'story_id',
                                  'sprint_id')
