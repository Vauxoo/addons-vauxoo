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
from openerp.osv import osv
import os


class document_storage(osv.Model):
    _inherit = 'document.storage'

    def recovery_attachments(self, cr, uid, ids, context=None):
        ir_attach_obj = self.pool.get('ir.attachment')
        for document_storage_pool in self.browse(cr, uid, ids, context=context):
            path = document_storage_pool.path or False
            if path and document_storage_pool.type == 'filestore':
                document_dir_obj = self.pool.get('document.directory')
                id_type_int = self.search(cr, uid, [
                                          ('type', '=', 'filestore')])
                if id_type_int:
                    directory_ids = document_dir_obj.search(
                        cr, uid, [('storage_id', '=', id_type_int[0])])
                    attach_ids = ir_attach_obj.search(cr, uid, [
                                                      ('parent_id', 'in', directory_ids)])
                    for attachment in ir_attach_obj.browse(cr, uid, attach_ids, context=context):
                        name_random = self.__get_random_fname(path)
                        if attachment.db_datas:
                            r = open(os.path.join(path, name_random), "wb")
                            r.write(attachment.db_datas)
                            r.close()
                            ir_attach_obj.write(cr, uid, [attachment.id], {
                                                'store_fname': os.path.join(path, name_random), 'db_datas': False})
        return True
