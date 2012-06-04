from osv import osv, fields

class product_product(osv.osv):
     _inherit = "product.product"
     
     _columns = {
          'product_partner_upc_ids': fields.one2many('product.partner.upc', 'product_id', 'Partner UPCs'),
     }
     
     def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
          res = super(product_product, self).name_search(cr, user, name, args, operator, context, limit)
          if not res:
               query = """SELECT id, product_id, upc
                    FROM product_partner_upc
                    WHERE upc='%s'
               """%(name)
               cr.execute(query)
               id = (cr.dictfetchone() or {}).get('product_id', False)
               if id:
                    ids = self.search(cr, user, [('id','=',id)], limit=limit, context=context)
                    res = self.name_get(cr, user, ids, context)
                    
               if not res:
                    query = """SELECT id, product_id, ean
                                   FROM product_packaging
                                   WHERE ean='%s'
                                   limit 1 """%(name)
               cr.execute(query)
               id = (cr.dictfetchone() or {}).get('product_id', False)
               if id:
                    ids = self.search(cr, user, [('id','=',id)], limit=limit, context=context)
                    res = self.name_get(cr, user, ids, context)
          return res
     
product_product()

class product_partner_upc(osv.osv):
     _name = "product.partner.upc"
     _description = "Add manies UPC of Partner's"
     
     _rec_name = 'upc'
     
     _columns = {
          'name': fields.char('Para que no marque error el auditrail', size=1),###BORRAR DESPUES DE QUE CORRIGAN EL ERROR EN AUDITRAIL.
          'upc': fields.char('UPC', size = 13, required = True),
          'product_id': fields.many2one('product.product', 'Product', required = True),
          'partner_id': fields.many2one('res.partner', 'Partner'),
          'description': fields.text('Description'),
          'product': fields.many2one('product.product', 'Product'),
     }
     
     _defaults = {
     }
     
     #TODO: Add index column 'upc'
     #	Add def check_upc
     
     _sql_constraints = [
          ('number_uniq', 'unique (upc)', 'UPC tiene que ser unico!')
     ]
product_partner_upc()
