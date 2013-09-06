# -*- coding: utf-8 -*-                                                            
##############################################################################  
#                                                                                  
#    OpenERP, Open Source Management Solution                                      
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).                         
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
{                                                                                  
    'name' : 'Sign Youtube',                                                                   
    'version' : '0.1',                                                             
    'author' : 'Vauxoo',                                                      
    'category' : '',                                                          
    'description' : """                                                            
Sign YouTube
============

What do you need
----------------
You need have a YouTube account and have your client ID and developer key if you don't have one you
can get here_

.. _here: http://code.google.com/apis/youtube/dashboard/gwt/index.html
How to Use
----------
In the configuration menu you have a new menu with the name: Sign YouTube Config.
You need fill the required information to load all videos for you YouTube account and make the 
configuration test

If the configuration is correct you can load the YouTube videos for send it in the company inbox
    """,                                                                           
    'website': 'http://www.vauxoo.com',                                            
    'images' : [],                                                                 
    'depends' : [
        'base',
    ],                                                                
    'data': [                                                                      
    'security/ir.model.access.csv',
    'view/sign_youtube_view.xml',
    ],                                                                                 
    'js': [                                                                        
    ],                                                                                 
    'qweb' : [                                                                     
    ],                                                                                 
    'css':[                                                                        
    ],                                                                                 
    'demo': [                                                                      
    ],                                                                                 
    'test': [                                                                      
    ],                                                                                                                                                                                                  
    'installable': True,                                                           
    'auto_install': False,                                                         
}                                                                                  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 
