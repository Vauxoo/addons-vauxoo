#!/usr/bin/python                                                               
# -*- encoding: utf-8 -*-                                                       
############################################################################### 
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved                                                        
################# Credits###################################################### 
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
from openerp.tools.translate import _

class convert_note_task(osv.TransientModel):
    
    '''Convert Note to Task Wizard'''
    
    _name = 'convert.note.task'
    
    _columns = {
            'estimated_time':fields.float('Estimated Time', help="""Estimated Time to Complete the
                Task"""), 
            'project_id':fields.many2one('project.project', 'Project', help='Project Linked'), 
            'date_end':fields.date('Date End', help='Date to complete the Task'), 
   }

