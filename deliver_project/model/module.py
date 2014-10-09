# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import osv, fields


class module(osv.Model):
    _inherit = 'ir.module.module'

    def get_doc_inside(self, cr, uid, ids, context=None):
        """
        Doc in classes on my module
        """
#        for d in dir(self.pool.get("res.partner")):
#            exec('A=self.pool.get("res.partner").%s.__doc__'%d)
#            print A
        return "DOCUMENTACION DOCUMENTACION \n MAS DOCUMENTACION"

    def format_help(self, cr, uid, dict_txt, context={}):
        '''
        {'MenuName':menu.name,
        'CompleteMenuName':menu.complete_name,
        'ActionHelp':menu.action.help,
        'ModuleName':action.__module__
        'XmlId':data_id.name}
        :return docStr Variable with wiki text.
        '''
        docStr = ''
        Name = dict_txt.get('MenuName')
        CompleteMenuName = dict_txt.get('CompleteMenuName')
        ActionHelp = dict_txt.get('ActionHelp')
        XmlId = dict_txt.get('XmlId')
        if Name:
            docStr = docStr + "===%s===" % Name
        if XmlId:
            docStr = docStr + "\nimage: %s.jpeg" % XmlId
        if CompleteMenuName:
            docStr = docStr + "\n''%s''" % CompleteMenuName
        if ActionHelp:
            docStr = docStr + "\n%s" % ActionHelp
        return docStr

    def title_help(self, cr, uid, mod_id, module, context={}):
        '''
        {'CompleteModuleName':action.__module__
        'ModuleName':action.__module__}
        :return docStr Variable with wiki text.
        '''
        docStr = "==%s==\n%s" % (self.browse(cr, uid,
                                             mod_id,
                                             context=context).shortdesc,
                                 self.sub_title_help(cr, uid, module,
                                                     context=context))
        return docStr

    def sub_title_help(self, cr, uid, module_name, context={}):
        '''
        Subtitle generator
        :return docStr Variable with wiki text.
        '''
        docStr = "'''Technical Name: ''' ''%s''" % module_name
        return docStr

    def _get_docs(self, cr, uid, ids, field_name=None, arg=None, context=None):
        '''
        Field function with instrospection algorithm to obtain documentation for
        Module.
        '''
        res = {}
        model_data_obj = self.pool.get('ir.model.data')
        menu_obj = self.pool.get('ir.ui.menu')
        mlist = self.browse(cr, uid, ids, context=context)
        mnames = {}
        for m in mlist:
            # skip uninstalled modules below,
            # no data to find anyway
            if m.state in ('installed', 'to upgrade', 'to remove'):
                mnames[m.name] = m.id
            res[m.id] = {
                'doc_on_module': []
            }

        if not mnames:
            return res
        # VIEWS AND REPORTS AND MENUS RELATED TO ONE SPECIFIC MODULE
        view_id = model_data_obj.search(
            cr, uid, [('module', 'in', mnames.keys()),
                      ('model', 'in', ('ir.ui.view', 'ir.actions.report.xml',
                                    'ir.ui.menu', 'ir.actions.act_window'))])
#            ('model','in',('ir.ui.view','ir.actions.report.xml','ir.ui.menu','ir.actions.act_window'))])
        for data_id in model_data_obj.browse(cr, uid, view_id, context):
            # We use try except, because views or menus may not exist
            try:
                key = data_id.model
                res_mod_dic = res[mnames[data_id.module]]
                # Just MEnu with actions:
                if data_id.model == 'ir.ui.menu':
                    menu = menu_obj.browse(
                        cr, uid, data_id.res_id, context=context)
                    if menu.action._table_name == 'ir.actions.act_window':
                        if menu.action:
                            print "-.-.-.-.-.-.-.-.-.-.-.-.- %s" % data_id.name
                            res_mod_dic[
                                'doc_on_module'].append("%s" %
                                    self.format_help(cr, uid,
                                        {'MenuName': menu.name,
                                         'CompleteMenuName': menu.complete_name,
                                         'ActionHelp': menu.action.help,
                                         'ModuleName': data_id.module,
                                         'XmlId': data_id.name},
                                        context=context))
                            res_mod_dic[
                                'doc_on_module'].append(self.title_help(cr, uid,
                                        mnames[data_id.module],
                                    data_id.module, context=context))
            except KeyError, e:
                self.__logger.warning(
                    'Data not found for reference %s[%s:%s.%s]', data_id.model,
                    data_id.res_id, data_id.model, data_id.name, exc_info=True)
            except Exception, e:
                self.__logger.warning('Unknown error while browsing %s[%s]',
                                      data_id.model, data_id.res_id,
                                      exc_info=True)
        # res_mod_dic['doc_on_module']=list(set(res_mod_dic['doc_on_module']))
        for key, value in res.iteritems():
            for k, v in res[key].iteritems():
                # TODO Make Generic or with regEx
                # Putting title on the begining.
                txt = "\n".join(sorted(v[:len(v) - 2]))
                res[key][k] = txt
        return res

    _columns = {
        'doc_on_module': fields.function(_get_docs, method=True,
            string='Documentation', type='text', multi="meta", store=False),
    }
