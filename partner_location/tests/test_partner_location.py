# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yanina Aular
#    Copyright 2015 Vauxoo
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

from openerp.tests.common import TransactionCase


class TestPartnerLocation(TransactionCase):

    def setUp(self):
        super(TestPartnerLocation, self).setUp()
        self.res_partner_obj = self.env['res.partner']
        self.get_records()

    def get_records(self):
        """
        """
        cr, uid = self.cr, self.uid
        import pdb; pdb.set_trace()

        partner_id = self.registry("ir.model.data").\
            get_object_reference(cr, uid, "base",
                                 "main_partner")[1]

        vauxoo_id = self.registry("ir.model.data").\
            get_object_reference(cr, uid, "base",
                                 "res_partner_23")[1]

        vicking_id = self.registry("ir.model.data").\
            get_object_reference(cr, uid, "base",
                                 "res_partner_22")[1]


    def test_company_location(self):
        """
        """
        import pdb; pdb.set_trace()

