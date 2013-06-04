# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

from openerp.tools.translate import _

from openerp.osv import osv, fields


class procurement_order(osv.Model):
    _inherit = "procurement.order"

    _columns = {
        'production_ids': fields.many2many('mrp.production',
            'mrp_production_procurement_order_rel', 'procurement_id',
            'production_id', 'Production orders'),
        'production_created': fields.many2one('mrp.production',
            'Production order'),
    }

    def make_mo(self, cr, uid, ids, context=None):
        """ writes the production created to the procurement
        @return: same res than original make_mo
        """
        res = super(procurement_order, self).make_mo(
            cr, uid, ids, context=context)
        for line in res:
            self.write(cr, uid, [line], {'production_created': res.get(line)})
        return res
