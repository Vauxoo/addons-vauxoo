# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from osv import osv, fields
import os
import random

class document_storage(osv.osv):
    _inherit = 'document.storage'
    
    def recovery_attachments(self, cr, uid, ids, context=None):
        ir_attach_obj=self.pool.get('ir.attachment')
        for id in ids:
            ir_attach=self.browse(cr, uid, id)
            path=ir_attach.path or False
            if path:
                list=ir_attach_obj.search(cr,uid,[])
                for ir in list:
                    name_random=self.__get_random_fname(path)
                    attachment=ir_attach_obj.browse(cr,uid,[ir],context=context)[0]
                    if attachment.datas_fname and attachment.db_datas:
                        r=open (path + str(name_random), "w")
                        r.write(attachment.db_datas)
                        r.close()
                        ir_attach_obj.write(cr, uid, [ir], {'store_fname': path+ str(name_random)})
                        ir_attach_obj.write(cr, uid, [ir], {'db_datas': False})
        return True
