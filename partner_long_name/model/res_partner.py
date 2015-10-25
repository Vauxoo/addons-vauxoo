# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

from openerp import models


class ResPartner(models.Model):

    """
    Inherit the res partner model to add base data fields like
    city and phone number to field name.
    """

    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        """
        Because there is a high possibility to get customers or partners
        with the same name, is really important to show more information in a
        many2one search. So, there added x, y ... data to
        make it possible. For e.g.: city, and phone.
        """
        res = super(ResPartner, self).name_get(cr, uid, ids, context=context)
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_name, name)
            if record.city:
                name = "%s, %s" % (name, record.city)
            if record.phone:
                name = "%s, %s" % (name, record.phone)
            if context.get('show_address_only'):
                name = self._display_address(
                    cr,
                    uid,
                    record,
                    without_company=True,
                    context=context)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(
                    cr,
                    uid,
                    record,
                    without_company=True,
                    context=context)
            res.append((record.id, name))
        return res
