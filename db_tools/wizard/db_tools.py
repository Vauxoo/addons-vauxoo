# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#              Julio (julio@vauxoo.com)
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
import os
import time
import base64

import service
import tempfile

waittime = 10
wait_count = 0
wait_limit = 12


class db_tools(osv.TransientModel):
    _name = 'db.tools'

    def db(self, cr, uid, context=None):
        ws_obj = service.web_services.db()
        db_list = ws_obj.exp_list()
        list_db = []
        for db in db_list:
            list_db.append((db.lower(), db))
        return list_db

    def _db_default(self, cr, uid, context=None):
        res = self.db(cr, uid, context)
        list_db = []
        for db in res:
            if ((cr.dbname, cr.dbname) == db):
                list_db.append(db)
        return list_db

    def db_default(self, cr, uid, context=None):
        return self._db_default(cr, uid, context)[0][0]

    _columns = {
        'filter': fields.selection([
            ('backup', 'Backup'),
            ('restore', 'Backup-Restore')], 'Filter',
            help='Backup creates a backup of the database and stored\
                in the path indicated, Restore-Backup creates a backup\
                of the database, and in turn restores the new name'),
        'password': fields.char('Password', size=64, required=True),
        'list_db': fields.selection(_db_default, 'Data Base Restore',
                                    required=True, readonly=True),
        'name_db': fields.char('Name DB', size=128, required=True),
        'path_save_db': fields.char('Path save DB', size=256, required=True)
    }

    _defaults = {
        'filter': 'restore',
        'list_db': db_default,
        'name_db': lambda self, cr, uid, context=None: cr.dbname +
        time.strftime('_%Y%m%d_%H%M%S.backup'),
        'path_save_db': tempfile.gettempdir()
    }

    def backup_db(self, cr, uid, ids, uri=False, dbname=''):
        ws_obj = service.web_services.db()
        data = self.browse(cr, uid, ids[0])
        filename = os.path.join(data.path_save_db, data.name_db)
        dump_db64 = ws_obj.exp_dump(dbname)
        dump = base64.decodestring(dump_db64)
        file_db = file(filename, 'wb')
        file_db.write(dump)
        file_db.close()
        return filename

    def backup_restore_db(self, cr, uid, ids, uri, dbname=''):
        res = self.backup_db(cr, uid, ids, uri, dbname)
        data = self.browse(cr, uid, ids[0])
        data_base = os.path.basename(res)
        name_db = data_base[:data_base.rfind(".")]
        print 'name_db', name_db
        f = file(res, 'r')
        data_b64 = base64.encodestring(f.read())
        f.close()
        ws_obj = service.web_services.db()
        ws_obj.exp_restore(name_db, data_b64)
        return True

    def find_db(self, cr, uid, ids, context=None):
        return True

    def confirm_action(self, cr, uid, ids, context=None):
        for lin in self.browse(cr, uid, ids, context=context):
            if lin.filter == 'backup':
                self.backup_db(cr, uid, ids, context.get(
                    'uri', False), lin.list_db)
            if lin.filter == 'restore':
                self.backup_restore_db(cr, uid, ids, context.get(
                    'uri', False), lin.list_db)
        return {}

    def cancel_action(self, cr, uid, ids, context=None):
        return {}
