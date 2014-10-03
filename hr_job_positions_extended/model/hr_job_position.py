#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import fields, osv

LEVEL_JOB = [
    ('p1', 'P1'),
    ('p2', 'P2'),
    ('p3', 'P3'),
    ('p4', 'P4'),
    ('p5', 'P5'),
    ('p6', 'P6'),
    ('p7', 'P7'),
    ('p8', 'P8'),
    ('p9', 'P9'),
    ('p10', 'P10'),
]


class hr_job(osv.Model):

    _inherit = "hr.job"

    _columns = {
        'name': fields.char('Job Name', size=128, required=True, select=True,
            translate=True),
        'level': fields.selection(LEVEL_JOB,
                                  'Level',
                                  help="level of job position."),
        'reports_to': fields.many2one('hr.job', 'Reports To',
                                      help="Who reports"),
        'activities': fields.text('Frequent Activities and Tasks', translate=True,
                                  help="Frequent Activities and Tasks"),
        'responsibilities': fields.text('Responsibilities', translate=True,
                                        help="Responsibilities of Job Position"),

        'description': fields.text('Job Description', translate=True),
        'requirements': fields.text('Requirements', translate=True),
    }
