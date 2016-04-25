# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)
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

from __future__ import absolute_import
import functools
import itertools
import logging
import operator
from ast import literal_eval
import openerp
from openerp.osv import orm, osv
from openerp import fields, models
from openerp.osv.orm import browse_record
from openerp.tools.translate import _

_logger = logging.getLogger('base.product.merge')


def is_integer_list(ids):
    return all(isinstance(i, (int, long)) for i in ids)


class MergeProductLine(models.TransientModel):
    _name = 'base.product.merge.line'
    _order = 'min_id asc'

    wizard_id = fields.Many2one(
        'base.product.merge.automatic.wizard',
        'Wizard')
    min_id = fields.Integer('MinID')
    aggr_ids = fields.Char('Ids', required=True)


class MergeProductAutomatic(models.TransientModel):
    _name = 'base.product.merge.automatic.wizard'

    group_by_name_template = fields.Boolean('Nombre')
    group_by_default_code = fields.Boolean('Referencia')
    group_by_categ_id = fields.Boolean('Categoria')
    group_by_uom_id = fields.Boolean('Unidad de medida')
    state = fields.Selection([('option', 'Option'),
                              ('selection', 'Selection'),
                              ('finished', 'Finished')],
                             'State',
                             readonly=True,
                             default='option',
                             required=True)
    number_group = fields.Integer("Group of Products",
                                  readonly=True)
    current_product_id = fields.Many2one('product.product',
                                         string='Current product')
    product_from = fields.Many2one('product.product',
                                   string='Product from')
    product_to = fields.Many2one('product.product',
                                 string='Product to')
    current_line_id = fields.Many2one('base.product.merge.line',
                                      'Current Line')
    line_ids = fields.One2many('base.product.merge.line',
                               'wizard_id', 'Lines')
    dst_product_id = fields.Many2one('product.product',
                                     string='Destination Contact')
    product_ids = fields.Many2many(
        'product.product', 'product_rel', 'product_merge_id',
        'product_id', string="Products to merge")
    maximum_group = fields.Integer("Maximum of Group of Contacts")

    def get_fk_on(self, cr, table, tables=None):
        tables = tables and tuple(tables) or []
        where = tables and 'AND cli.relname in %s' % (str(tables))
        query = """  SELECT cl1.relname as table,
                        att1.attname as column
                   FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                        pg_attribute as att1, pg_attribute as att2
                  WHERE con.conrelid = cl1.oid
                    AND con.confrelid = cl2.oid
                    AND array_lower(con.conkey, 1) = 1
                    AND con.conkey[1] = att1.attnum
                    AND att1.attrelid = cl1.oid
                    AND cl2.relname = %s
                    AND att2.attname = 'id'
                    AND array_lower(con.confkey, 1) = 1
                    AND con.confkey[1] = att2.attnum
                    AND att2.attrelid = cl2.oid
                    AND con.contype = 'f'
                    %s
        """
        return cr.execute(query, (table, tables and where or '',))

    def _update_foreign_keys(self, cr, uid, src_products, dst_product,
                             model=None, context=None):
        if model:
            return self._update_foreign_keys_modify(
                cr, uid, src_products, dst_product, model=model,
                context=context)
        else:
            # find the many2one relation to a product
            proxy = self.pool.get('product.product')
            uom_ids = self.pool.get('product.uom').\
                search(cr, uid,
                       [('category_id', '=',
                         dst_product.uom_id.category_id.id)],
                       context=context)

            self.get_fk_on(cr, 'product_uom')
            product_bad = []
            record = []
            flag = []
            uos_table = {}
            for table, column in cr.fetchall():
                if table in uos_table:
                    record = uos_table.get(table, [])
                    record.append(column)
                    uos_table.update({table: record})
                else:
                    uos_table.update({table: [column]})
            self.get_fk_on(cr, 'product_product')

            for table, column in cr.fetchall():
                if 'base_product_merge_' in table:
                    continue

                product_ids = tuple([int(i) for i in src_products])

                query = """SELECT column_name FROM information_schema.columns
                           WHERE table_name LIKE '%s'""" % (
                    table)
                cr.execute(query, ())
                columns = []
                for data in cr.fetchall():
                    if data[0] != column:
                        columns.append(data[0])

                query_dic = {
                    'table': table,
                    'column': column,
                    'value': columns[0],
                }
                if len(columns) <= 1:
                    # unique key treated
                    query = """
                        UPDATE "%(table)s" as ___tu
                        SET %(column)s = %%s
                        WHERE
                            %(column)s = %%s AND
                            NOT EXISTS (
                                SELECT 1
                                FROM "%(table)s" as ___tw
                                WHERE
                                    %(column)s = %%s AND
                                    ___tu.%(value)s = ___tw.%(value)s
                            )""" % query_dic
                    for product_id in product_ids:
                        cr.execute(query, (
                            dst_product.id, product_id, dst_product.id))
                else:
                    cr.execute("SAVEPOINT recursive_product_savepoint")

                    if table not in uos_table:
                        query = '''UPDATE "%(table)s" SET %(column)s = %%s
                                   WHERE %(column)s IN %%s''' % query_dic
                        cr.execute(query, (dst_product.id, product_ids,))
                        if column == proxy._parent_name and \
                                table == 'product_product':
                            query = """
                            WITH RECURSIVE cycle(id, product_id) AS (
                                    SELECT id, product_id
                                    FROM product_product
                                UNION
                                    SELECT  cycle.id,
                                            product_product.parent_id
                                    FROM  product_product, cycle
                                    WHERE product_product.id = cycle.parent_id
                                          AND cycle.id != cycle.parent_id
                            )
                            SELECT id FROM cycle
                            WHERE id = parent_id AND id = %s
                            """
                            cr.execute(query, (dst_product.id,))
                            if cr.fetchall():
                                cr.execute(
                                    "ROLLBACK TO SAVEPOINT "
                                    "recursive_product_savepoint")
                    else:
                        query = '''SELECT *
                                   FROM "%(table)s"
                                   WHERE %(column)s IN %%s''' % query_dic
                        cr.execute(query, (product_ids,))
                        # Validation with flag
                        for match in cr.dictfetchall():
                            uos_field = uos_table.get(table)
                            uos_id = [match.get(i)
                                      for i in uos_field
                                      if match.get(i, False)]
                            if all([(i in uom_ids and True or False)
                                    for i in uos_id]):
                                continue
                            else:
                                flag.append(False)
                        # Handle exception for the flag validation
                        if False in flag:
                            raise osv.except_osv(_('Error!'), _(
                                """You must verify the units of measurement in which
                                the products do you wish to merge already have
                                operations.
                                """))
                        else:
                            cr.execute(query, (product_ids,))
                            for match in cr.dictfetchall():
                                uos_field = uos_table.get(table)
                                uos_id = [match.get(i)
                                          for i in uos_field
                                          if match.get(i, False)]
                                if all([(i in uom_ids and True or False)
                                        for i in uos_id]):
                                    query = '''UPDATE "%(table)s"
                                               SET %(column)s = %%s
                                               WHERE id=%%s''' % query_dic
                                    cr.execute(query,
                                               (dst_product.id,
                                                match.get('id'),))
                                    if column == proxy._parent_name and \
                                            table == 'product_product':
                                        query = """
                            WITH RECURSIVE cycle(id, product_id)
                            AS (SELECT id, product_id
                                FROM product_product
                                UNION
                                    SELECT  cycle.id,
                                            product_product.parent_id
                                    FROM product_product, cycle
                                    WHERE product_product.id = cycle.parent_id
                                          AND cycle.id != cycle.parent_id
                            )
                            SELECT id FROM cycle
                            WHERE id = parent_id AND id = %s
                                        """
                                        cr.execute(query, (dst_product.id,))
                                        if cr.fetchall():
                                            cr.execute(
                                                "ROLLBACK TO SAVEPOINT "
                                                "recursive_product_savepoint")
                                else:
                                    product_bad.append(
                                        match.get(query_dic.get('column')))
            return product_bad

    def _update_foreign_keys_modify(self, cr, uid, src_products,
                                    dst_product, model=None,
                                    context=None):
        uos_table = {}
        po_table = {}
        tables = []
        product_ids_validate = []
        product_ids_unvalidate = []

        product_obj = self.pool.get('product.product')
        proxy = self.pool.get(model.replace('_', '.') or 'product.uom')
        dst_product_ids = product_obj.browse(
            cr, uid, context.get('active_ids'), context=context)
        uom_factor_dst = self.pool.get('product.uom').browse(
            cr, uid, dst_product, context=context)[0].factor
        for dst_product_id in dst_product_ids:
            if dst_product_id.uom_id.factor == uom_factor_dst:
                product_ids_validate.append(dst_product_id.id)
            else:
                product_ids_unvalidate.append(dst_product_id.name)
        dst_product = dst_product[0]

        self.get_fk_on(cr, 'product_uom')
        for table, column in cr.fetchall():
            tables.append(table)
            if table in uos_table:
                val = uos_table.get(table, [])
                val.append(column)
                uos_table.update({table: val})
            else:
                uos_table.update({table: [column]})

        self.get_fk_on(cr, 'product_product', tables)
        for table, column in cr.fetchall():
            if table in po_table:
                val = po_table.get(table, [])
                val.append(column)
                po_table.update({table: val})
            else:
                po_table.update({table: [column]})

        if len(product_ids_validate) > 0:
            for table in uos_table:

                if 'base_product_merge_' in table:
                    continue

                product_ids = tuple(product_ids_validate)

                querys = """SELECT column_name FROM information_schema.columns
                           WHERE table_name LIKE '%s'""" % (table)

                columns = []
                for column in po_table.get(table, False) and \
                        uos_table.get(table) or []:
                    cr.execute(querys, ())
                    for data in cr.fetchall():
                        if data[0] != column:
                            columns.append(data[0])

                    query_dic = {
                        'table': table,
                        'column': column,
                        'param': po_table.get(table)[0],
                        'value': columns[0],
                    }

                    if len(columns) <= 1:
                        # unique key treated
                        query = """
                            UPDATE "%(table)s" as ___tu
                            SET %(column)s = %%s
                            WHERE
                                %(param)s IN %%s AND
                                NOT EXISTS (
                                    SELECT 1
                                    FROM "%(table)s" as ___tw
                                    WHERE
                                        %(param)s IN %%s AND
                                        ___tu.%(value)s = ___tw.%(value)s
                                )""" % query_dic
                        cr.execute(query, (
                            dst_product, product_ids, product_ids))
                    else:
                        cr.execute("SAVEPOINT recursive_product_savepoint")

                        query = '''UPDATE "%(table)s" SET %(column)s = %%s
                                   WHERE %(param)s IN %%s''' % query_dic
                        cr.execute(query, (dst_product, product_ids))
                        if column == proxy._parent_name and \
                                table == 'product_uom':

                            query = """
                                WITH RECURSIVE cycle(id, product_id) AS (
                                        SELECT id, product_id FROM %s
                                    UNION
                                       SELECT  cycle.id, %s.parent_id
                                       FROM    %s, cycle
                                       WHERE   %s.id = cycle.parent_id AND
                                                cycle.id != cycle.parent_id
                                )
                                SELECT id FROM cycle
                                WHERE id = parent_id AND id = %%s
                            """ % (model, model, model, model)
                            cr.execute(query, (dst_product,))
                            if cr.fetchall():
                                cr.execute(
                                    "ROLLBACK TO SAVEPOINT "
                                    "recursive_product_savepoint")
        return True

    def _update_reference_fields(self, cr, uid, src_products,
                                 dst_product, context=None):
        product_bad = []

        def update_records(model, src, field_model='model',
                           field_id='res_id', context=None):
            proxy = self.pool.get(model)
            if proxy is None:
                return
            domain = [(field_model, '=', 'product.product'), (
                field_id, '=', src.id)]
            ids = proxy.search(
                cr, openerp.SUPERUSER_ID, domain, context=context)
            return proxy.write(cr, openerp.SUPERUSER_ID, ids,
                               {field_id: dst_product.id},
                               context=context)

        update_records = functools.partial(update_records,
                                           context=context)

        proxy = self.pool['ir.model.fields']
        domain = [('ttype', '=', 'reference')]
        record_ids = proxy.search(
            cr, openerp.SUPERUSER_ID, domain, context=context)

        for record in proxy.browse(cr, openerp.SUPERUSER_ID, record_ids,
                                   context=context):
            proxy_model = self.pool[record.model]

            field_type = proxy_model._fields.get(record.name).type

            if field_type == 'function':
                continue

            for product in src_products:
                domain = [
                    (record.name, '=', 'product.product,%d' % product.id)
                ]
                model_ids = proxy_model.search(
                    cr, openerp.SUPERUSER_ID, domain, context=context)
                values = {
                    record.name: 'product.product,%d' % dst_product.id,
                }
                proxy_model.write(
                    cr, openerp.SUPERUSER_ID, model_ids, values,
                    context=context)
        return product_bad

    def _update_values(self, cr, uid, src_products,
                       dst_product, context=None):
        product_bad = []
        columns = dst_product._fields

        def write_serializer(column, item):
            if isinstance(item, browse_record):
                return item.id
            else:
                return item

        values = dict()
        for column, field in columns.iteritems():
            if field.type not in ('many2many', 'one2many') and not \
                    field.compute:
                for item in itertools.chain(src_products, [dst_product]):
                    if item[column]:
                        values[column] = write_serializer(column, item[column])

        values.pop('id', None)
        parent_id = values.pop('parent_id', None)
        dst_product.write(values)
        if parent_id and parent_id != dst_product.id:
            try:
                dst_product.write({'parent_id': parent_id})
            except (osv.except_osv, orm.except_orm):
                _logger.info(
                    '''Skip recursive product hierarchies
                       for parent_id %s of product: %s''', parent_id,
                    dst_product.id)
        return product_bad

    def close_cb(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def _merge(self, cr, uid, product_ids, dst_product=None, context=None):
        proxy = self.pool.get('product.product')
        product_ids = proxy.exists(
            cr, uid, list(product_ids), context=context)
        if len(product_ids) < 2:
            return True

        if len(product_ids) > 10:
            raise osv.except_osv(_('Error!'), _(
                """
                For safety reasons, you cannot merge more than 10 products
                together. You can re-open the wizard several
                times if needed.
                """))
        if dst_product and dst_product.id in product_ids:
            src_products = proxy.browse(cr, uid, [
                                        i for i in product_ids
                                        if i != dst_product.id],
                                        context=context)
        else:
            ordered_products = self._get_ordered_product(
                cr, uid, product_ids, context)
            dst_product = ordered_products[-1]
            src_products = ordered_products[:-1]
        _logger.info("dst_product: %s", dst_product.id)

        if openerp.SUPERUSER_ID != uid and \
                self._model_is_installed(cr, uid, 'account.move.line',
                                         context=context) and \
                self.pool.get('account.move.line').\
                search(cr, openerp.SUPERUSER_ID,
                       [('product_id', 'in', [product.id for product in
                                              src_products])],
                       context=context):
            raise osv.except_osv(_('Error!'), _(
                """Only the destination product may be linked to existing
                   Journal Items. Please ask the Administrator if you need
                   to merge several products linked to existing Journal
                   Items."""))
        product_bad = []

        product_bad += self._update_foreign_keys(cr, uid, src_products,
                                                 dst_product, context=context)
        product_bad += self._update_reference_fields(cr, uid, src_products,
                                                     dst_product,
                                                     context=context)
        product_bad += self._update_values(cr, uid, src_products, dst_product,
                                           context=context)
        product_bad = set(product_bad)
        for product in src_products:
            if product.id not in product_bad:
                product.unlink()
                proxy.exists(cr, uid, product.id, context=context)
        return True

    def _get_ordered_product(self, cr, uid, product_ids, context=None):
        products = self.pool.get('product.product').browse(
            cr, uid, list(product_ids), context=context)
        ordered_products = sorted(
            sorted(products, key=operator.attrgetter('create_date'),
                   reverse=True),
            key=operator.attrgetter(
                'active'),
            reverse=True)
        return ordered_products

    def _model_is_installed(self, cr, uid, model, context=None):
        proxy = self.pool.get('ir.model')
        domain = [('model', '=', model)]
        return proxy.search_count(cr, uid, domain, context=context) > 0

    def merge_cb(self, cr, uid, ids, context=None):
        assert is_integer_list(ids)

        context = dict(context or {}, active_test=False)
        this = self.browse(cr, uid, ids[0], context=context)
        p_ids = this.product_ids and this.product_ids.ids
        if p_ids:
            p_ids.append(this.product_to)
        product_ids = set([int(i) for i in this.product_from and
                           [this.product_to, this.product_from] or p_ids])
        if not list(product_ids):
            raise osv.except_osv(_('Error!'), _(
                """The product from must be selected for
                    this option."""))
        else:
            self._merge(cr, uid, product_ids, this.product_to,
                        context=context)
        return True

    def _compute_selected_groupby(self, this):
        group_by_str = 'group_by_'
        group_by_len = len(group_by_str)

        lfields = [
            key[group_by_len:]
            for key in self._fields.keys()
            if key.startswith(group_by_str)
        ]

        groups = [
            field
            for field in lfields
            if getattr(this, '%s%s' % (group_by_str, field), False)
        ]

        if not groups:
            raise osv.except_osv(_('Error!'),
                                 _("""You have to specify a filter for your
                                      selection."""))
        return groups

    def _generate_query(self, lfields, maximum_group=100):
        group_fields = ', '.join(lfields)

        filters = []
        for field in lfields:
            if field in ['name_template', 'default_code', ]:
                filters.append((field, 'IS NOT', 'NULL'))

        criteria = ' AND '.join('%s %s %s' % (field, operator, value)
                                for field, operator, value in filters)

        text = [
            "SELECT min(id), array_agg(id)",
            "FROM product_product",
        ]

        if criteria:
            text.append('WHERE %s' % criteria)

        text.extend([
            "GROUP BY %s" % group_fields,
            "HAVING COUNT(*) >= 2",
            "ORDER BY min(id)",
        ])

        if maximum_group:
            text.extend([
                "LIMIT %s" % maximum_group,
            ])

        return ' '.join(text)

    def _process_query(self, cr, uid, ids, query, context=None):
        """Execute the select request and write the result in this wizard
        """
        proxy = self.pool.get('base.product.merge.line')
        this = self.browse(cr, uid, ids[0], context=context)
        cr.execute(query)

        counter = 0
        for min_id, aggr_ids in cr.fetchall():

            values = {
                'wizard_id': this.id,
                'min_id': min_id,
                'aggr_ids': aggr_ids,
            }
            proxy.create(cr, uid, values, context=context)
            counter += 1

        values = {
            'state': 'selection',
            'number_group': counter,
        }

        this.write(values)

        _logger.info("counter: %s", counter)

    def _next_screen(self, cr, uid, this, context=None):
        this.refresh()
        values = {}
        if this.line_ids:
            # in this case, we try to find the next record.
            current_line = this.line_ids[0]
            current_product_ids = literal_eval(current_line.aggr_ids)
            values.update({
                'current_line_id': current_line.id,
                'product_ids': [(6, 0, current_product_ids)],
                'product_to': self.
                _get_ordered_product(cr, uid,
                                     current_product_ids,
                                     context)[-1].id,
                'state': 'selection',
            })
        else:
            values.update({
                'current_line_id': False,
                'product_ids': [],
                'state': 'finished',
            })

        this.write(values)

        return {
            'type': 'ir.actions.act_window',
            'res_model': this._name,
            'res_id': this.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def other_screen(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0], context=context)

        this.refresh()
        values = {}
        if this.line_ids:
            # in this case, we try to find the next record.
            current_line = this.line_ids[0]
            current_product_ids = literal_eval(current_line.aggr_ids)
            values.update({
                'current_line_id': current_line.id,
                'product_ids': [(6, 0, current_product_ids)],
                'product_to': self.
                _get_ordered_product(cr, uid,
                                     current_product_ids,
                                     context)[-1].id,
                'state': 'selection',
            })
        else:
            values.update({
                'current_line_id': False,
                'product_ids': [],
                'state': 'finished',
            })

        this.write(values)
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(
            cr, uid, [('model', '=', 'ir.ui.view'),
                      ('name', '=',
                       'base_product_merge_automatic_wizard_form_two')])
        resource_id = obj_model.read(cr, uid, model_data_ids,
                                     fields=['res_id'])[0]['res_id']

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'base.product.merge.automatic.wizard',
            'res_id': ids[0],
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def start_process_cb(self, cr, uid, ids, context=None):
        """Start the process.
        * Compute the selected groups (with duplication)
        * If the user has selected the 'exclude_XXX' fields, avoid the
        products.
        """
        assert is_integer_list(ids)

        context = dict(context or {}, active_test=False)
        this = self.browse(cr, uid, ids[0], context=context)
        groups = self._compute_selected_groupby(this)
        query = self._generate_query(groups, this.maximum_group)
        self._process_query(cr, uid, ids, query, context=context)
        return self.other_screen(cr, uid, ids, context)

    def next_cb(self, cr, uid, ids, context=None):
        """Don't compute any thing
        """
        context = dict(context or {}, active_test=False)
        this = self.browse(cr, uid, ids[0], context=context)
        if this.current_line_id:
            this.current_line_id.unlink()
        return self.other_screen(cr, uid, ids, context)
