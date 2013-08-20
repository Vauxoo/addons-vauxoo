import datetime                                                                 
import logging                                                                  
import time                                                                     
                                                                                
from openerp.osv import osv, fields                                             
from openerp.osv.orm import intersect, except_orm                               
import openerp.tools                                                            
from openerp.tools.translate import _                                           
                                                                                
from openerp.addons.decimal_precision import decimal_precision as dp            
                                                                                
_logger = logging.getLogger(__name__)                                           

class warranty_oerp(osv.Model):
    _name = 'account.warranty_oerp'
    _columns = {
        'contract_id':fields.many2one('account.analytic.account', 'Contract', help='fields help'), 
    }
                                                                                
class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'license_oerp':fields.boolean('This contract has Enterprise License',
            help='This contract has Enterprise License'), 
        'warranty_oerp_ids':fields.one2many('warranty_oerp', 'warranty_id', 'Warranties Enterprise', help='Warranties Enterprise'), 
    }
