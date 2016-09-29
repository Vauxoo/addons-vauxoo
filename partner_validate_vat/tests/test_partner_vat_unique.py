# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class PartnerVatUnique(TransactionCase):

    def setUp(self):
        super(PartnerVatUnique, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.partner = self.env.ref('base.res_partner_2')
        self.partner2 = self.env.ref('base.res_partner_3')
        self.mexico = self.env.ref('base.mx')
        self.env.ref('base.main_company').write({
            'country_id': self.mexico.id,
        })

    def test_001_test_copy(self):
        """Verify that VAT is cleaned when is duplicated a record"""
        self.partner.write({
            'country_id': self.mexico.id,
            'vat': 'MXXXX030303XX4',
        })
        new_partner = self.partner.copy({})
        self.assertFalse(new_partner.vat, 'Partner VAT is not cleaned in copy')

    def test_002_test_duplicated_partner_vat(self):
        """Try set in two partners the same VAT"""
        self.partner.write({
            'country_id': self.mexico.id,
            'vat': 'MXXXX030303XX4',
        })
        with self.assertRaisesRegexp(
                ValidationError, "Error ! Partner's VAT must be unique."):
            self.partner2.write({
                'country_id': self.mexico.id,
                'vat': 'MXXXX030303XX4',
            })

    def test_003_test_duplicated_vat_different_country(self):
        """Try set in two partners the same VAT, but the partners have
        different country, then any raise is generated"""
        self.partner.write({
            'country_id': self.mexico.id,
            'vat': 'MXXXX030303XX4',
        })
        self.partner2.write({
            'vat': 'MXXXX030303XX4',
        })

    def test_004_test_partner_children(self):
        """Try set the same VAT to company and children, in this case the
        raise is not generated"""
        self.partner.write({
            'company_type': 'company',
            'country_id': self.mexico.id,
            'vat': 'MXXXX030303XX4',
        })
        self.partner_obj.create({
            'name': 'Children',
            'country_id': self.mexico.id,
            'parent_id': self.partner.id,
            'type': 'contact',
            'vat': 'MXXXX030303XX4',
        })
