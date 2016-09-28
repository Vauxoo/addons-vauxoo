# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase


class CompanyVatWithoutCountry(TransactionCase):

    def setUp(self):
        super(CompanyVatWithoutCountry, self).setUp()
        self.company_obj = self.env['res.company']
        self.mx = self.env.ref('base.mx')

    def test_company_vat_without_country(self):
        """Verify that VAT is generated when country and vat_without_country
        are assigned."""
        company = self.company_obj.create({
            'name': 'Company MX',
            'country_id': self.mx.id,
            'vat_without_country': 'XXX020202XX3',
        })
        company.onchange_vat_wo_country()
        self.assertEquals('MXXXX020202XX3', company.vat, 'NIF not updated.')

    def test_company_not_vat_without_country(self):
        """Verify that have not problem when VAT without country is not
        assigned."""
        company = self.company_obj.create({
            'name': 'Company MX',
            'country_id': self.mx.id,
        })
        company.onchange_vat_wo_country()
        self.assertFalse(company.vat, 'NIF generated without data.')
