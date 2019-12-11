from odoo.tests.common import TransactionCase


class PartnerVatWithoutCountry(TransactionCase):

    def setUp(self):
        super(PartnerVatWithoutCountry, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.mex = self.env.ref('base.mx')

    def test_partner_vat_without_country(self):
        """Verify that VAT is generated when country and vat_without_country
        are assigned."""
        partner = self.partner_obj.create({
            'name': 'Partner MX',
            'country_id': self.mex.id,
            'vat_without_country': 'XXX020202XX3',
        })
        partner.onchange_vat_wo_country()
        self.assertEquals('MXXXX020202XX3', partner.vat, 'NIF not updated.')

    def test_partner_not_vat_without_country(self):
        """Verify that have not problem when VAT without country is not
        assigned."""
        partner = self.partner_obj.create({
            'name': 'Partner MX',
            'country_id': self.mex.id,
        })
        partner.onchange_vat_wo_country()
        self.assertFalse(partner.vat, 'NIF generated without data.')
