# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Juan Carlos Hernandez Funes (info@vauxoo.com)
#    Planned by: Moises Augusto Lopez Calderon (info@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import logging
import urlparse

from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger("SignYouTube")
try:
    from gdata.youtube import service
except ImportError:
    _logger.error("You need the gdata library ---> sudo pip install gdata")


class SignYoutubeConf(osv.Model):
    _name = 'sign.youtube.conf'

    _columns = {
        'name': fields.char('YouTube User', 25, help='User name for youtube account used to login in '
                            'youtube'),
        'line': fields.one2many('sign.youtube.conf.line', 'config_id', 'Videos Uploaded'),
        'passwd': fields.char('YouTube Password', 25, help='Password used for your youtube account'),
        'max_v': fields.integer('Max Number Video to load',
                                help='Number max of video to load'),
        'client_id': fields.char('ID Client', 200,
                                 help='Client ID for your youtube account if you do not have a '
                                 'client ID you can a developer key in the YouTube API '
                                 'https://code.google.com/apis/youtube/dashboard/gwt/index.html'),
        'developer_key': fields.char('Developer Key', 150,
                                     help='Developer key used by de API if you do not have one you '
                                     'can get one in the YouTube API '
                                     'https://code.google.com/apis/youtube/dashboard/gwt/index.'
                                     'html'),
    }

    _defaults = {
        'max_v': 50,

    }

    def get_items(self, entry):
        """Return the video details
        """
        youtube_id = ''
        if entry:
            youtube_url = entry.GetHtmlLink().href
            if youtube_url:
                url_data = urlparse.urlparse(youtube_url)
                query = urlparse.parse_qs(url_data.query)
                youtube_id = query.get("v") and query.get("v")[0] or ''
        entry_data = {
            'name': entry and entry.media.title.text or '',
            'published': entry and entry.published.text or '',
            'description': entry and entry.media.description.text or '',
            'category': entry and entry.media.category[0].text or '',
            'tags': entry and entry.media.keywords.text or '',
            'url_swf': entry and entry.GetSwfUrl() or '',
            'duration_seconds': entry and float(entry.media.duration.seconds) or '',
            'favorites': entry and entry.statistics and entry.statistics.favorite_count or '',
            'views': entry and entry.statistics and entry.statistics.view_count or '',
            'private': entry.media.private and entry.media.private.text,
            'public_information': entry and youtube_id or '',
        }
        return entry_data

    def test_connection(self, cr, uid, ids, context=None):
        context = context or {}
        for wzr in self.browse(cr, uid, ids, context=context):
            yt_service = False
            try:
                yt_service = service.YouTubeService(email=wzr.name,
                                                    password=wzr.passwd,
                                                    client_id=wzr.client_id,
                                                    developer_key=wzr.developer_key)
            except:
                raise osv.except_osv(_('Error!'),
                                     _("""The config parameters are wrong please verify it and try
                                           again"""))
            if yt_service:
                raise osv.except_osv(_('Perfect!'),
                                     _("""Connection Completed"""))
        return True

    def load_videos(self, cr, uid, ids, filters_name=None, context=None):
        """Load the videos for your account and added in the config lines
        """
        if context is None:
            context = {}
        line = self.pool.get('sign.youtube.conf.line')
        entry_datas = []
        for wzr in self.browse(cr, uid, ids, context=context):
            userfeed_entry = []
            try:
                yt_service = service.YouTubeService(email=wzr.name,
                                                    password=wzr.passwd,
                                                    client_id=wzr.client_id,
                                                    developer_key=wzr.developer_key)
                yt_service.ProgrammaticLogin()
                username = wzr.name[:wzr.name.index('@')]
                max_results = wzr.max_v
                index = 1

                while True:
                    uri = "http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=%d"\
                        "&start-index=%d" % (username, max_results, index)
                    userfeed = yt_service.GetYouTubeUserFeed(uri)
                    if not len(userfeed.entry):
                        break
                    userfeed_entry.extend(userfeed.entry)
                    index += max_results

                entry_datas = []
            except BaseException, e:
                _logger.error(
                    "Connection error, login to Youtube we got this " +
                    "error %s please verify the parameters and try again", e)
            for entry in userfeed_entry:
                item = self.get_items(entry)
                line_ids = line.search(
                    cr, uid, [('url_swf', '=', item.get('url_swf', False)),
                              ('config_id', '=', wzr.id)],
                    context=context)
                if filters_name:
                    for filter_name in filters_name:
                        if filter_name.lower() in item.get('title', '').lower():
                            entry_datas.append(item)
                            break
                if line_ids:
                    line_brw = line.browse(
                        cr, uid, line_ids[0], context=context)
                    line.write(cr, uid, line_ids,
                               {
                                   'public_information': item.get('public_information', ''), },
                               context=context)
                    if str(line_brw.duration_seconds) == str(item.get('duration_seconds', '')):
                        line.write(cr, uid, line_ids,
                                   {'update': 0,
                                    },
                                   context=context)
                        continue
                    else:
                        line.write(cr, uid, line_ids,
                                   {'update': 1,
                                    'duration_seconds': item.get('duration_seconds', ''), },
                                   context=context)
                else:
                    item.update({'config_id': wzr.id})
                    line.create(cr, uid, item, context=context)

                entry_datas.append(item)

        return entry_datas


class SignYoutubeConfLine(osv.Model):
    _name = 'sign.youtube.conf.line'

    _columns = {
        'views': fields.integer('Number of views',
                                help='Number of times they have viewed the video'),
        'favorites': fields.integer('Number of favorites',
                                    help='Number of times they have viewed the video'),
        'name': fields.text('Video Title ', help='Tittle for YouTube Video'),
        'message': fields.text('Message', help='Message to shown in inbox'),
        'private': fields.char('Private', 200, help='Private info about the video'),
        'info': fields.boolean('Add in messages', help='Select if you want add this video in the '
                               'company messages'),
        'config_id': fields.many2one('sign.youtube.conf', 'Config'),
        'published': fields.char('Published ', 200, help=''),
        'attachment_ids': fields.many2many('ir.attachment', 'youtube_attachment_rel',
                                           'youtube_id', 'attachment_id', 'Attachments'),
        'tags': fields.char('Tags ', 200, help=''),
        'update': fields.selection([(0, 'Normal'), (1, 'Update')], 'Update', help='Used to know if '
                                   'the video was '
                                   'update'),
        'url_swf': fields.char('Url ', 200, help='URL for you can see the video'),
        'duration_seconds': fields.float('Duration ', help='Video duration in seconds'),
        'category': fields.char('Category ', 200, help='Category seleted for this video from '
                                'YouTube'),
        'description': fields.text('Description', help='Description added for this video when was '
                                   'created'),
        'public_information': fields.text('Public Information', help='This information accept html'
                                          'and is the information that will be used in the portal page.'),
    }
    _defaults = {
        'update': 0,
    }
    _order = 'views desc'

    def load_url(self, cr, uid, ids, context=None):
        """Launch a new window where you can the watch the video
        """
        if context is None:
            context = {}
        for wzr in self.browse(cr, uid, ids, context=context):
            return {
                'type': 'ir.actions.act_url',
                'url': wzr.url_swf,
                'target': 'new'
            }

    def show_on_inbox(self, cr, uid, ids, context=None):
        """Generate a new windows to add a message for then send it to the inbox message
        """
        if context is None:
            context = {}
        for wzr in self.browse(cr, uid, ids, context=context):
            obj_model = self.pool.get('ir.model.data')
            model_data_ids = obj_model.search(
                cr, uid, [('model', '=', 'ir.ui.view'),
                          ('name', '=', 'sign_youtube_form2_view')])
            resource_id = obj_model.read(cr, uid, model_data_ids,
                                         fields=['res_id'])[0]['res_id']
            message = 2 * '<br>' + wzr.name + 2 * '<br>' + _('You need watch this video ') + \
                '<a href="%s">%s</a>' % \
                                                            (wzr.url_swf[
                                                                :wzr.url_swf.find(
                                                                    '?')],
                                                             wzr.name)
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sign.youtube.conf.line',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_message': message, 'default_name': wzr.name},
            }

    def send_to_inbox(self, cr, uid, ids, context=None):
        """Send the message to the inbox for the specific group
        """
        if context is None:
            context = {}
        message_obj = self.pool.get('mail.group')
        data_obj = self.pool.get('ir.model.data')

        for wzr in self.browse(cr, uid, ids, context=context):
            attachment_ids = [i.id for i in wzr.attachment_ids]
            try:
                (dummy, mail_group_id) = data_obj.get_object_reference(cr, uid, 'portal_gallery',
                                                                       'company_gallery_feed')
            except BaseException:
                (dummy, mail_group_id) = data_obj.get_object_reference(cr, uid, 'mail',
                                                                       'group_all_employees')
            dummy = message_obj.message_post(cr, uid, [mail_group_id],
                                             body=wzr.message, subject=wzr.name,
                                             attachment_ids=attachment_ids,
                                             subtype='mail.mt_comment', context=context)
        return {'type': 'ir.actions.act_window_close'}
