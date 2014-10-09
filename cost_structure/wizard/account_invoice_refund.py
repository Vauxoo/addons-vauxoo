#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv

import time
import datetime
invo_cost = {}


class account_invoice_refund(osv.TransientModel):

    _inherit = 'account.invoice.refund'

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        '''
        Compute_refund overwritten the method to assign the date with time, which then will be used to calculate the time of

        '''

        invo_obj = self.pool.get('account.invoice')
        res = super(account_invoice_refund, self).compute_refund(
            cr, uid, ids, mode=mode, context=context)
        invo_brw = res.get('domain', False) and\
            len(res.get('domain', False)[1]) > 2 and\
            res.get('domain', False)[1][2] and \
            invo_obj.browse(cr, uid, res.get(
                            'domain', False)[1][2], context=context)[0]
        date = time.strftime('%Y/%m/%d %H:%M:%S')
        if not invo_brw.date_invoice:
            invo_obj.write(cr, uid, [invo_brw and invo_brw.id], {
                           'date_invoice': date}, context=context)
            return res
        date_2 = invo_brw.date_invoice.split(' ')
        date_2 = date_2 and date_2[0].split('-')
        date = date and date.split(' ')
        date = date and len(date) > 0 and date[1].split(":")

        date_2 = date and time and datetime.datetime(int(date_2[0]),
                                                    int(date_2[1]),
                                                    int(date_2[2]),
                                                    int(date[0]),
                                                    int(date[1]),
                                                    int(date[2])) or False
        invo_obj.write(cr, uid, [invo_brw and invo_brw.id], {
                       'date_invoice': date_2}, context=context)
        return res

