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

    def _check_overlapping(self,cr,uid,ids,context=None):
        obj_warranty = self.browse(cr, uid, ids[0], context=context) 
        if obj_warranty.enddate < obj_warranty.startdate:                        
            return False                                                        
        pids = self.search(cr, uid, [('enddate','>=',obj_warranty.startdate),('startdate','<=',obj_warranty.enddate),('id','<>',obj_warranty.id)])
        if len(pids) > 0:
            return False
        return True

    def _check_duplicity(self,cr,uid,ids,context=None):
        obj_warranty = self.browse(cr, uid, ids[0], context=context)
        pids = self.search(cr, uid, [('enterprise_key','=',obj_warranty.enterprise_key),('id','<>',obj_warranty.id)])
        if len(pids) > 0:
            return False
        return True

    _columns = {
        'startdate':fields.date('Start Date', help='Start Date'), 
        'enddate':fields.date('End date', help='End Date'), 
        'enterprise_key':fields.char('Enterprise Contract Key', 64, help="""Enterprise
            Key"""), 
        'contract_id':fields.many2one('account.analytic.account', 'Contract',
            help='fields help'), 
    }
    _constraints = [                                                            
         (_check_overlapping, 'Error!\n Date is/are invalid.', ['enddate']),
         (_check_duplicity, 'Error!\n Enterprise Key exists in other contract.', ['enterprise_key']),
    ]
                                                                                
class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'license_oerp':fields.boolean('This contract has Enterprise License',
            help='This contract has Enterprise License'), 
        'warranty_oerp_ids':fields.one2many('account.warranty_oerp', 'contract_id', 'Warranties Enterprise', help='Warranties Enterprise'), 
    }
