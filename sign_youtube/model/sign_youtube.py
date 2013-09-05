# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Juan Carlos Hernandez Funes (info@vauxoo.com)
#    Planned by: Moises Augusto Lopez Calderon (info@vauxoo.com)
############################################################################
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
##############################################################################
from openerp.osv import osv, fields
from gdata.youtube import service


class sign_youtube_conf(osv.Model):
    _name = 'sing.youtube.conf'

    _columns = {
        'name':fields.char('YouTube User', 25, help='User name for youtube account used to login in '
                                            'youtube'), 
        'line':fields.one2many('sing.youtube.conf.line', 'config_id', 'Videos Uploaded'), 
        'passwd':fields.char('YouTube Password', 25, help='Password used for your youtube account'), 
        'max_v':fields.integer('Max Number Video to load',
                             help='Number max of video to load'), 
        'client_id':fields.char('ID Client', 200,
                                help='Client ID for your youtube account if you do not have a '
                                     'client ID you can a developer key in the YouTube API ' 
                                     'https://code.google.com/apis/youtube/dashboard/gwt/index.'
                                     'html#product/AI39si7M7K' '5jj5AHA-VUGJW0XSgEWIS_qjFkfXwygeIF'
                                     '13AQR85UC2Ylo-8pu2G6gs-Q4MSNKzUG11_c45zO1CFaTbmA62rjLw'), 
        'developer_key':fields.char('Developer Key', 150,
                                    help='Developer key used by de API if you do not have one you '
                                         'can get one in the YouTube API '
                                         'https://code.google.com/apis/youtube/dashboard/gwt/index'
                                         '.html#product/AI39si7M7K5jj5AHA-VUGJW0XSgEWIS_qjFkfXwyge'
                                         'IF13AQR85UC2Ylo-8pu2G6gs-Q4MSNKzUG11_c45zO1CFaTbmA62rj'
                                         'Lw'), 
    }

    _defaults = {
            'max_v':50,
            
            }


    def get_items(self, entry):                                                                               
        entry_data = {                                                                                  
            'title': entry and entry.media.title.text or '',                                            
            'published': entry and entry.published.text or '',                                          
            'description': entry and entry.media.description.text or '',                                
            'category': entry and entry.media.category[0].text or '',                                   
            'tags': entry and entry.media.keywords.text or '',                                          
            'url_swf': entry and entry.GetSwfUrl() or '',                                               
            'duration_seconds': entry and float(entry.media.duration.seconds) or '',                           
            #'private':                                                                                 
        }                                                                                               
        return entry_data   

    def load_videos(self, cr, uid, ids, filters_name=None, context=None):
        if context is None:
            context = {}
        line = self.pool.get('sing.youtube.conf.line')
        for wzr in self.browse(cr, uid, ids, context=context):
            yt_service = service.YouTubeService(email=wzr.name,                                              
                                        password=wzr.passwd,                                           
                                        client_id=wzr.client_id,           
                                        developer_key=wzr.developer_key)
            yt_service.ProgrammaticLogin()                                                                  
            username=wzr.name[:wzr.name.index('@')]                                                           
            max_results=wzr.max_v                                                                                  
            index=1                                                                                         
            userfeed_entry = []                                                                             
                                                                                                            
            while True:                                                                                     
                uri = "http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=%d"\
                   "&start-index=%d" % (username, max_results, index)                                       
                userfeed = yt_service.GetYouTubeUserFeed(uri)                                               
                if not len(userfeed.entry):                                                                 
                    break                                                                                   
                userfeed_entry.extend(userfeed.entry)                                                       
                index += max_results                                                                        
                                                                                                            
            entry_datas = []                                                                                
            for entry in userfeed_entry:                                                                    
                item = self.get_items(entry)                                                                     
                line_ids = line.search(cr, uid, [('url_swf', '=', item.get('url_swf',False)),
                                                 ('config_id', '=', wzr.id)],
                                       context=context)
                if filters_name:                                                                            
                    for filter_name in filters_name:                                                        
                        if filter_name.lower() in item.get('title', '').lower():                            
                            entry_datas.append(item)                                                        
                            break                                                                           
                if line_ids:
                    line_brw = line.browse(cr, uid, line_ids[0], context=context)
                    if str(line_brw.duration_seconds) == str(item.get('duration_seconds', '')):
                        line.write(cr, uid, line_ids,
                                    {'update':0,
                                     },
                                    context=context)
                        continue
                    else:
                        line.write(cr, uid, line_ids,
                                    {'update':1,
                                     'duration_seconds':item.get('duration_seconds', ''),},
                                    context=context)
                else:
                    item.update({'config_id':wzr.id})
                    line.create(cr, uid, item, context=context)
                    
                entry_datas.append(item)                                                                
    
        return entry_datas
    
class sign_youtube_conf_line(osv.Model):
    _name = 'sing.youtube.conf.line'

    _columns = {
        'name':fields.char('Video Title ', 200, help='Tittle for YouTube Video'),
        'info':fields.boolean('Add in messages', help='Select if you want add this video in the '
                                                      'company messages'), 
        'config_id':fields.many2one('sing.youtube.conf', 'Config'), 
        'published':fields.char('Published ', 200, help=''),
        'tags':fields.char('Tags ', 200, help=''),
        'update':fields.selection([(0, 'Normal'), (1, 'Update')], 'Update', help='Used to know if '
                                                                                 'the video was '
                                                                                 'update'),
        'url_swf':fields.char('Url ', 200, help='URL for you can see the video'),
        'duration_seconds':fields.float('Duration ', help='Video duration in seconds'),
        'category':fields.char('Category ', 200, help='Category seleted for this video from '
                                                      'YouTube'),
        'description':fields.text('Description', help='Description added for this video when was '
                                                      'created'),
    }
    _defaults = {
            'update':0,
            }

    def load_url(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for wzr in self.browse(cr, uid, ids, context=context):
            return {
                    'type': 'ir.actions.act_url',
                    'url':wzr.url_swf,
                    'target': 'new'
                    }
