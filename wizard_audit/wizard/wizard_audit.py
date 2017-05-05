# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Ceferino Cuevas
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv,fields
from openerp import SUPERUSER_ID

class wizard_audit(osv.TransientModel):
    _name = 'audittrail.wizard'
    _description = 'Modulo que hereda de  audittrail'
    _columns = {
        "name" : fields.char("Rule name", size=32, required = True), 
        "object_ids" : fields.many2many('ir.model', 'object_user_rel', 'objects_id', 'object_id', 'Objects', required = True, help ="Modelos"),
        "log_read": fields.boolean("Log Reads", help="Select this if you want to keep track of read/open on any record of the object of this rule"),
        "log_write": fields.boolean("Log Writes", help="Select this if you want to keep track of modification on any record of the object of this rule"),
        "log_unlink": fields.boolean("Log Deletes", help="Select this if you want to keep track of deletion on any record of the object of this rule"),
        "log_create": fields.boolean("Log Creates",help="Select this if you want to keep track of creation on any record of the object of this rule"),
        "log_action": fields.boolean("Log Action",help="Select this if you want to keep track of actions on the object of this rule"),
        "log_workflow": fields.boolean("Log Workflow",help="Select this if you want to keep track of workflow on any record of the object of this rule"),
        "user_ids" : fields.many2many('res.users', 'auditrail_rules_users', 'temp_id', 'user_id', 'Users', help="Usuarios a seleccionar")
    }

    def action_add_rules(self, cr, uid, ids, context=None):
        form = self.read(cr, uid, ids, context=context)
        object_ids = form[0]['object_ids']
        user_ids=form[0]['user_ids']
        name= form[0]['name'] or False
        log_read  = form[0]['log_read'] or False
        log_write= form[0]['log_write'] or False
        log_unlink=form[0]['log_unlink'] or False
        log_create=form[0]['log_create'] or False
        log_action= form[0]['log_action'] or False
        log_workflow=form[0]['log_workflow'] or False
        vals = {}
        rules = []
        obj_action = self.pool.get('ir.actions.act_window')
        obj_rules = self.pool.get('audittrail.rule')
        obj_model_data = self.pool.get('ir.model.data')
        obj_model = self.pool.get('ir.model')
        
        
        for obj1 in obj_model.browse(cr,uid,object_ids):

            val = {
                 "name": 'View Log',
                 "res_model": 'audittrail.log',
                 "src_model": obj1.model,
                 "domain": "[('object_id','=', " + str(obj1.id) + "), ('res_id', '=', active_id)]"
            }             
            
            print val,'============================VAL=>'
            action_id = obj_action.create(cr, SUPERUSER_ID, val)
            action_id = [action_id]
            var_action_id = action_id[0]
            print var_action_id
            print user_ids, "============user_ids========"
            vals = {'name': name, 
                            'log_read': log_read, 
                            'log_unlink': log_unlink, 
                            'log_workflow': log_workflow, 
                            'log_write': log_write, 
                            'log_create': log_create, 
                            'log_action': log_action, 
                            'state': 'subscribed',                            
                            'user_id': [(6, 0, user_ids)],
                            'object_id': obj1.id,
                            'action_id': int(var_action_id)}
            print vals, "====VALS====="
        
            audittrail_rule_id = obj_rules.create(cr, uid, vals, context={}) 
            print audittrail_rule_id
            rules.append(audittrail_rule_id)
            print rules
            keyword = 'client_action_relate'
            value = 'ir.actions.act_window,' + str(int(action_id[0]))
            res = obj_model_data.ir_set(cr, SUPERUSER_ID, 'action', keyword, 'View_log_' + obj1.model, [obj1.model], value, replace=True, isobject=True, xml_id=False)
            print res
        print rules
        #self.subscribe(cr, uid, rules, context)
        return True
        
        
        
    def subscribe(self, cr, uid, ids, context=None):
        print ids, "---------------->"
        """
        Subscribe Rule for auditing changes on object and apply shortcut for logs on that object.
        @param cr: the current row, from the database cursor,
        @param uid: the current userâ€™s ID for security checks,
        @param ids: List of Auddittrail Ruleâ€™s IDs.
        @return: True
        """
        obj_action = self.pool.get('ir.actions.act_window')
        obj_model = self.pool.get('ir.model.data')
        #start Loop
        for thisrule in self.browse(cr, uid, ids):
            obj = self.pool.get(thisrule.object_id.model)
            if not obj:
                raise osv.except_osv(
                        _('WARNING: audittrail is not part of the pool'),
                        _('Change audittrail depends -- Setting rule as DRAFT'))
                self.write(cr, uid, [thisrule.id], {"state": "draft"})
            val = {
                 "name": 'View Log',
                 "res_model": 'audittrail.log',
                 "src_model": thisrule.object_id.model,
                 "domain": "[('object_id','=', " + str(thisrule.object_id.id) + "), ('res_id', '=', active_id)]"
            }
        action_id = obj_action.create(cr, SUPERUSER_ID, val)
        self.write(cr, uid, [thisrule.id], {"state": "subscribed", "action_id": action_id})
        keyword = 'client_action_relate'
        value = 'ir.actions.act_window,' + str(action_id)
        res = obj_model.ir_set(cr, SUPERUSER_ID, 'action', keyword, 'View_log_' + thisrule.object_id.model, [thisrule.object_id.model], value, replace=True, isobject=True, xml_id=False)
        
        #End Loop
        return True
