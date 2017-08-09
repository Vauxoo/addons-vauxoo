# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger
from psycopg2 import IntegrityError


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

        self.partner.write({
            'country_id': self.mexico.id,
            'vat': 'MXXXX030303XX4',
        })

    def test_01_test_copy(self):
        """Verify that VAT is cleaned when is duplicated a record"""
        new_partner = self.partner.copy({})
        self.assertFalse(new_partner.vat, 'Partner VAT is not cleaned in copy')

    @mute_logger('openerp.sql_db')
    def test_02_test_duplicated_partner_vat(self):
        """Try set in two partners the same VAT"""
        with self.assertRaisesRegexp(
                IntegrityError,
                r'"res_partner_unique_commercial_vat"'):
            self.partner2.write({
                'country_id': self.mexico.id,
                'vat': 'MXXXX030303XX4',
            })

    def test_03_test_partner_children(self):
        """Try set the same VAT to company and children, in this case the
        raise is not generated"""
        self.partner_obj.create({
            'name': 'Children',
            'country_id': self.mexico.id,
            'parent_id': self.partner.id,
            'type': 'contact',
            'vat': 'MXXXX030303XX4',
        })

    @mute_logger('openerp.sql_db')
    def test_04_test_partner_(self):
        """Try set in two partners the same VAT when partner is new"""
        with self.assertRaisesRegexp(
                IntegrityError,
                r'"res_partner_unique_commercial_vat"'):
            self.partner_obj.create({
                'name': 'New Partner',
                'country_id': self.mexico.id,
                'vat': 'MXXXX030303XX4',
            })
