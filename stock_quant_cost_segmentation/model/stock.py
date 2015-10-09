# coding: utf-8

from openerp.osv import fields, osv


class StockQuant(osv.osv):
    _inherit = "stock.quant"
    _columns = {
        'material_cost': fields.float('Material Cost'),
        'production_cost': fields.float('Material Cost'),
        'subcontracting_cost': fields.float('Material Cost'),
        'landed_cost': fields.float('Material Cost'),
    }
