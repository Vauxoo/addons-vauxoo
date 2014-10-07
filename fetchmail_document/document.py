# -*- encoding: utf-8 -*-
from openerp.osv import osv


class document(osv.Model):

    """
    fetchmail
    """
    _inherit = 'ir.attachment'

    def _check_duplication(self, cr, uid, ids, context=None):
        for attach in self.browse(cr, uid, ids, context):
            domain = [('id', '!=', attach.id),
                      ('name', '=', attach.name),
                      ('parent_id', '=', attach.parent_id.id),
                      ('res_model', '=', attach.res_model),
                      ('res_id', '=', attach.res_id),
                      ]
            # If another model fail i need to add here the validation "Just for
            # V6.0"
            if attach.res_model == 'project.issue':
                return True
            if self.search(cr, uid, domain, context=context):
                return False
        return True
    # On Trunk there are a commentary that say with pure SQL it ca not be done.
    # Delete this constraint whe we migrate to 6.1
    _constraints = [
        (_check_duplication, 'File name must be unique!', [
         'name', 'parent_id', 'res_model', 'res_id'])
    ]
