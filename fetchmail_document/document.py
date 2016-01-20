# coding: utf-8
from openerp.osv import osv


class Document(osv.Model):

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
