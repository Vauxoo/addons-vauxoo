#-*- coding:utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    Financed by Vauxoo
#    Developed by Oscar Alcala <oszckar@gmail.com>
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
#

from openerp.osv import osv, fields
try:
    from launchpadlib.launchpad import Launchpad
except ValueError:
    raise osv.except_osv('No launchpadlib library installed',
                        'Please install launchpadlib you can it from PyPi or you can install it via\
                         apt-get')


class project_project(osv.osv):
    _inherit = 'project.project'
    _columns = {
            'lp_project': fields.char('Launchpad Project', size=64,
                            help='Put here the name of the project ie. for lp:openobject-server you\
                                    should use only openobject-server'),
            }

    def get_lp_data(self, cr, uid, ids, context=None):
        self_cache = self.browse(cr, uid, ids)[0]
        if self_cache.lp_project:
            cachedir = '~/.launchpadlib/'
            lp = Launchpad.login_anonymously('just testing', 'production', cachedir)
            lp_project_obj = lp.distributions[str(self_cache.lp_project)]
            title = '<h1>%s</h1>'%lp_project_obj.title
            url = '</h6>Puedes descargarla desde <a href="%s">aqui</a></h6>\n'%lp_project_obj.download_url

            summary = '<h3>%s</h3>'%lp_project_obj.summary
            if lp_project_obj.description:
                description = '<p>%s</p>'%lp_project_obj.description
                public_information = title + summary + description + url
            else:
                public_information = title + summary + url
            self.write(cr, uid, ids, {'public_information': public_information})
        else:
            raise osv.except_osv('No Launchpad project supplied',
                                'Please fill the Launchpad Project field in order to retrieve data\
                                from Launchpad.net')
        return True

