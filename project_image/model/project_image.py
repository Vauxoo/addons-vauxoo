# coding: utf-8

from openerp.osv import osv, fields


class ProjectProjectInheritImage(osv.Model):

    _inherit = "project.project"
    _columns = {
        'logo': fields.binary("Logo",
                              help="This field holds the image used as logo for the brand, limited to 1024x1024px."),
    }


class ProjectTaskInheritImage(osv.Model):

    _inherit = "project.task"
    _columns = {
        'logo': fields.related('project_id', 'logo', type="binary", string="Logo"),
    }
