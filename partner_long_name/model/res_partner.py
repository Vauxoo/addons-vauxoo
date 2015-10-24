# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

from openerp import fields, models


class ResPartner(models.Model):

    """
    Inherit the res partner model to add city, township_id and phone
    to name field.
    """

    _inherit = 'res.partner'

    def _name_get(self, data_dict, context=None):
        """
        @return dictionary
        """
        context = context or {}
        name = data_dict.get('name', '')
        city = data_dict.get('city', False)
        township_id = data_dict.get('township_id', False)
        phone = data_dict.get('phone', False)
        if city:
            name = '%s, %s, %s, %s' % (name, city, township_id, phone)
        return (data_dict['id'], name)

    def name_get(self, cr, user, ids, context=None):
        """
        Because there is a high possibility to get customers or partners
        with the same name, is really important to show more information in a
        many2one search. So, there added x, y and z data to
        make it possible. For e.g.: city, township and phone.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        result = []
        if not len(ids):
            return result
        for partner in self.browse(cr, user, ids, context=context):
            mydict = {
                'id': partner.id,
                'name': partner.name,
                'city': partner.city,
                'township_id': partner.township_id.name,
                'phone': partner.phone,
            }
            result.append(self._name_get(mydict))
        return result
