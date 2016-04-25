# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <rsilvam@vauxoo.com>
#    Audited by: Gabriela Quilarque <gabriela@openerp.com.ve>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################


from openerp.osv import fields, osv


__HELP__ = '''
Escriba el Patron de las cuentas, su estructura, por ejemplo:
Clase:           1,
Grupo:           12,
Cuentas:         123,
Subcuentas:      1234,
Cuentas Aux.:    1234567
Entonces escriba:  1, 12, 123, 1234, 1234567
'''


class AccountOrderWizardPattern(osv.TransientModel):
    _name = 'account.order.wizard.pattern'
    _rec_name = 'pattern'
    _columns = {
        'pattern': fields.char('Account Pattern', size=1024, required=True,
                               help=__HELP__,),
        'wzd_id': fields.many2one('account.order.wizard', 'Wizard')
    }


class AccountOrderWizard(osv.TransientModel):
    _name = 'account.order.wizard'
    _columns = {
        'select_patter': fields.selection([
            ('wp', 'With Pattern'),
            ('fp', 'Free Pattern')],
            'Select pattern type',
            help='Select pattern type by account'),
        'account_id': fields.many2one('account.account',
                                      'Parent Account',
                                      required=True),
        'company_id': fields.many2one('res.company', 'Compania',
                                      required=True,),
        'account_ids': fields.many2many(
            'account.account',
            'rel_wizard_account',
            'account_list', 'account_id',
            'Accounts to order', required=False),
        'patterns': fields.one2many('account.order.wizard.pattern',
                                    'wzd_id', 'Patterns'),
    }

    _defaults = {
        'select_patter': 'wp'
    }

    def _get_list(self, cr, uid, id, context=None):

        def t(s, p='x'):
            return s.replace(p, '_')
        return [t(i.pattern.strip()) for i in self.browse(cr,
                                                          uid, id, context).patterns]

    def _get_pattern(self, lista):
        patron = []
        patron = list(set(([len(lista[i]) for i in range(len(lista))])))
        patron.sort()
        return patron

    def _ordering(self, cr, uid, patron, len_patron, dict, dict_i0, k, i=0):
        """patron: es una lista de enteros indicando la longitud de cada patron
        len_patron: es el numero de patrones con el cual se estara trabajando
        dict: es un diccionario con una lista en cada clave
        [codigo, parent_flag, parent_id] dict_i0: codigo que se envia para
        hacer el ordenamiento, funge de codigo padre
        k:  es el id del codigo padre,
        i: es el contador para hacer el recorrido sobre el patron
        """
        for j in dict.keys():
            #~ la similitud del codigo con la similutud del patron
            #~
            if len(dict[j][0]) == patron[i + 1] and\
                    dict[j][0][:patron[i]] == dict_i0:
                dict[j][1] = True
                dict[j][2] = k
                if i + 1 < len_patron:
                    self._ordering(
                        cr, uid, patron, len_patron, dict, dict[j][0], j, i + 1)

    def _new_ordering(self, cr, uid, company_id, pattern, pattern_list,
                      lpl, top_parent, parent_id, pc=0, d={}):
        aa_obj = self.pool.get('account.account')
        cr.execute("SELECT id, code FROM account_account\
                WHERE code like %s AND company_id = %s AND active = True", (
            pattern, company_id))
        ids_list_dict = cr.dictfetchall()

        if not ids_list_dict:
            return True

        for ild in ids_list_dict:
            #~ dict[account_id] = ['code', parent_flag, parent_id]

            if ild['id'] == top_parent:
                continue

            if ild['id'] == parent_id:
                continue

            if len(ild['code'].strip()) != len(pattern):
                continue

            if pc == lpl - 1:
                aa_obj.write(cr, uid, [ild['id']], {
                             'parent_id': parent_id,
                             'code': ild['code'].strip()})
                continue
            aa_obj.write(cr, uid, [ild['id']], {
                         'parent_id': parent_id,
                         'code': ild['code'].strip(),
                         'type': 'view'})

        for ild in ids_list_dict:

            #~ dict[account_id] = ['code', parent_flag, parent_id]
            if ild['id'] == top_parent:
                continue
            if ild['id'] == parent_id:
                continue
            if pc == lpl - 1:
                continue
            if len(ild['code'].strip()) != len(pattern):
                continue

            now = pattern_list[pc]
            nxt = pattern_list[pc + 1]
            #~ code = ild['code']
            #~ minlen = min(map(len,[now,nxt,code]))
            #~ maxlen = max(map(len,[now,nxt,code]))
            ck = 0
            lf = now.rfind('_')
            rf = nxt.rfind('_')
            new_pattern = ''
            for k in nxt:

                if len(ild['code']) == len(nxt):
                    if lf < ck and ck <= rf:
                        if rf + 1 == len(nxt):
                            new_pattern += nxt[ck].replace('_', '%')
                        else:
                            new_pattern += nxt[ck]

                    else:
                        new_pattern += ild['code'][ck]
                else:
                    if ck + 1 <= len(ild['code']):
                        new_pattern += ild['code'][ck]
                    else:
                        new_pattern += nxt[ck]
                ck += 1
            new_parent_id = ild['id']
            self._new_ordering(cr, uid, company_id, new_pattern,
                               pattern_list, lpl, top_parent,
                               new_parent_id, pc + 1, {})
        #~ for ac_id in d:
            #~ print 'IMPRIMIENDO UN DIC id: %s - parent_id %s'%(ac_id,d[ac_id],)
            #~ aa_obj.write(cr, uid, [ac_id], d[ac_id])

        return True

    def get_order(self, cr, uid, ids, context=None):

        for id in ids:

            company_id = self.browse(cr, uid, id, context).company_id.id

            #~ aa_list = aa_obj.search(cr, uid, [('company_id','=',company_id)])
            #~ aa_obj.write(cr, uid, aa_list, {'parent_id':False})

            #~ break

            pattern_list = self._get_list(cr, uid, id, context)
            parent_id = self.browse(cr, uid, id, context).account_id.id
            lpl = len(pattern_list)
            top_parent = parent_id
            self._new_ordering(cr, uid, company_id, pattern_list[0],
                               pattern_list, lpl, top_parent, parent_id, 0, {})

            #~ d.get(top_parent) and d.pop(top_parent)
            #~ print 'DICCIONARIO TOTAL',d
            #~ for ac_id in d:
            #~ print 'IMPRIMIENDO UN DIC ',d[ac_id]
            #~ aa_obj.write(cr, uid, [ac_id], d[ac_id])
        return {}

    def get_level(self, cr, uid, ids, code, context=None):
        if context is None:
            context = {}
        cr.execute('''select distinct char_length(code) as level
                        from account_account
                        where code like '%s'
                        and char_length(code) > %s
                        order by level''' % (code + '%', len(str(code))))

        return cr.fetchall()

    def get_code(self, cr, uid, ids, code, level=None,
                 parent_id=None, context=None):
        if context is None:
            context = {}
        if parent_id:
            cr.execute('''select id, code
                          from account_account
                          where id <> %s and code like '%s'
                          order by code''' %
                       (parent_id, str(code).ljust(int(level), '_')))
        else:
            cr.execute('''select id, code
                          from account_account
                          where code like '%s'
                          order by code''' %
                       (str(code).ljust(int(level), '_')))

        return cr.dictfetchall()

    def order_without_pattern(self, cr, uid, ids, context=None,
                              code='', pid=None):
        if context is None:
            context = {}
        wz_brw = self.browse(cr, uid, ids[0], context)
        pid = pid or wz_brw.account_id.id
        account_obj = self.pool.get('account.account')
        levels = self.get_level(cr, uid, ids, code, context)
        while levels:
            level = levels.pop(0)
            codes = self.get_code(cr, uid, ids, code, level and level[0],
                                  pid, context)
            c_ids = [i.get('id') for i in codes]
            c_ids = list(set(c_ids) - set([pid]))
            account_obj.write(cr, uid, c_ids, {
                              'parent_id': pid}, context=context)
            cr.commit()
            while codes:
                codex = codes.pop(0)
                codex.get(
                    'code') != 0 and self.order_without_pattern(cr, uid, ids,
                                                                context, codex.get('code'), codex.get('id'))

        return True
