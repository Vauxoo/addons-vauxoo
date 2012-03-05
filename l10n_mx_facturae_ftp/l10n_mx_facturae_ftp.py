# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
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

import time

from operator import itemgetter

import netsvc
from osv import fields, osv

from tools.misc import currency
from tools.translate import _
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

from tools import config

class ftp_server(osv.osv):
    _name='ftp.server'
    
    _columns={
        'name':fields.char('ftp servidor',size=128,required=True),
        'ftp_user':fields.char('ftp suario',size=128,required=True),
        'ftp_pwd':fields.char('ftp clave',size=128,required=True),
        'ftp_raiz':fields.char('ftp raiz',size=128,required=True,help='llenar con siguiente Formato "/done"'),
    }
ftp_server()