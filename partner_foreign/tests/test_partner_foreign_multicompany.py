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


class TestPartnerLocationMultiCompany(TransactionCase):

    def setUp(self):
        super(TestPartnerLocationMultiCompany, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.get_records()

    def get_records(self):
        """get records to test
        """
        self.partner_rec = self.env.ref('base.main_partner')
        self.vauxoo_rec = self.env.ref('base.res_partner_23')
        self.vicking_rec = self.env.ref('base.res_partner_22')

    def test_international_field(self):
        """This international field is a fied defined at the res.partner model and
        crm.claim model. This fiels is a functional property field.
        The current test will check:
            1. Multicumpany test (property).
            2. Functional field change when the partner/company country change.
            3. Claim get the international value from the partner_id.
        """
        # 1. Multicompany test (property)

        # Get the defined companies recordsets.
        company_obj = self.env["res.company"]
        data_company = self.env.ref('base.main_company')

        camptocamp = self.env.ref("base.res_partner_12")
        demo_company = company_obj.create(
            {'currency_id': self.env.ref("base.EUR").id,
             'partner_id': camptocamp.id,
             'account_no': False,
             'city': 'Scranton',
             'zip': '18540',
             'email': 'info@yourcompany.example.com',
             'vat': False,
             'website': 'http://www.example.com',
             'phone': '+1 555 123 8069',
             'name': 'YourCompanyDemo',
             'manufacturing_lead': 1.0,
             'po_lead': 1.0,
             'security_lead': 0.0,
             'rml_header': '<header/>',
             'street': '1725 Slough Ave.',
             })

        camptocamp.write({"country_id": False})
        camptocamp.write({"company_id": demo_company.id})

        # Set the current user as a multicompany user
        user = self.env.user
        user.company_ids = [(6, 0, [demo_company.id, data_company.id])]
        self.assertEquals(demo_company in user.company_ids, True)
        self.assertEquals(data_company in user.company_ids, True)

        # Check that the demo company have not country associated. In that case
        # a warning message about this missing configuration must be show in
        # the partners form. Check the company_id.partner_id.
        self.assertEquals(demo_company.country_id.id, False)
        self.assertNotEquals(demo_company.partner_id.message, False)

        # Set the companies country for this test: Set US for demo company
        # and check that the data company is already set to PA country.
        pa_country = self.env.ref('base.pa')
        us_country = self.env.ref('base.us')
        demo_company.partner_id.write({"country_id": us_country.id})
        data_company.partner_id.write({"country_id": pa_country.id})
        self.assertEquals(demo_company.country_id, us_country)
        self.assertEquals(data_company.country_id, pa_country)

        # Find two demo partners and set then a fixed country: a Panama
        # partner and a United State partner.
        demo_partners = self.partner_obj.search([])
        self.assertEquals(len(demo_partners) >= 2, True)
        pa_partner = demo_partners[0]
        us_partner = demo_partners[1]
        pa_partner.country_id = pa_country.id
        us_partner.country_id = us_country.id
        self.assertEquals(pa_partner.country_id, pa_country)
        self.assertEquals(us_partner.country_id, us_country)

        # Check that demo company (US) is the current company, that the partner
        # associated to the company is a 'national' partner and check for the 2
        # national/international partners the new value.
        self.assertEquals(self.env.user.company_id, data_company)
        company_partner = user.company_id.partner_id
        self.assertEquals(demo_company.country_id, us_country)
        self.assertEquals(company_partner.international, 'national')
        self.assertEquals(pa_partner.international, 'national')
        self.assertEquals(us_partner.international, 'international')

        # Change user to the data company (PA) and check that the partner
        # international field automaclty change taking into account the data
        # company countr (PA).
        user.company_id = data_company.id
        self.assertEquals(self.env.user.company_id, data_company)
        company_partner = user.company_id.partner_id
        self.assertEquals(us_partner.international, 'international')
        self.assertEquals(pa_partner.international, 'national')

        # 2. Functional field change when the partner/company country change.

        # Change the PA partner country to US and check that the location type
        # value is automactily updated to 'international'.
        pa_partner.country_id = us_country.id
        self.assertEquals(pa_partner.country_id, us_country)
        self.assertEquals(pa_partner.international, 'international')

        # Change the data company country (PA) to (US) from the company record
        # and check the partner associated to the company will be updated too.
        self.assertEquals(self.env.user.company_id, data_company)
        data_company.country_id = us_country.id
        self.assertEquals(company_partner.country_id, us_country)

        # Change the data company country (US) to (PA) from the parnter record
        # and check the company country will be updated too.
        company_partner.write({"country_id": pa_country.id})
        self.assertEquals(data_company.country_id, pa_country)
