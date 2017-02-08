# coding: utf-8
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
        """get records to test
        """
        self.partner_rec = self.env.ref('base.main_partner')
        self.vauxoo_rec = self.env.ref('base.res_partner_18')
        self.vicking_rec = self.env.ref('base.res_partner_22')

    def test_company_foreign(self):
        """Test if partners are national or international depends
        of main partner
        """
        country_ve = self.env.ref('base.ve')
        self.partner_rec.write({'country_id': country_ve.id})
        self.assertEquals(self.partner_rec.country_id.id, country_ve.id)
        self.assertEquals(self.vauxoo_rec.international, 'national')
        self.assertEquals(self.vicking_rec.international, 'international')
