# coding: utf-8
from openerp.osv import fields, osv
import re
import logging

_logger = logging.getLogger(__name__)


class AccountMoveFolioFillGap(osv.TransientModel):
    _name = 'account.move.folio.fill.gap'
    _description = "Fill Gap in Journal Entry Folios"
    _columns = {
        'sure': fields.boolean('Check this box'),
    }

    def data_save(self, cr, uid, ids, context=None):
        """This function fill the Gaps in Journal Entry Folios
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: list of wizard ids
         """
        context = context or {}
        journal_obj = self.pool.get('account.journal')
        ir_seq_obj = self.pool.get('ir.sequence')
        WRONG = 0
        MATCH = 0
        FOLIOS = 0
        GAPS = 0
        folio_obj = self.pool.get('account.move.folio')
        journal_ids = journal_obj.search(cr, uid, [], context=context)
        if not journal_ids:
            _logger.info('NO JOURNALS FOR THIS COMPANY')
            return {'type': 'ir.actions.act_window_close'}

        for j_id in journal_ids:
            journal_brw = journal_obj.browse(cr, uid, j_id, context=context)
            seq_brw = journal_brw.sequence_id
            expr = ''
            if seq_brw.prefix:
                expr = seq_brw.prefix.split('/')
                expr = map(
                    lambda t: t if 'year' not in t else 4 * '[0-9]', expr)
                expr = '^' + '/'.join(expr)
            folio_ids = folio_obj.search(
                cr, uid, [('journal_id', '=', j_id)], context=context)
            if not folio_ids:
                _logger.info('NO FOLIOS FOR THIS JOURNAL %s' % j_id)
                continue

            _logger.info('%s FOLIOS TO PROCESS IN JOURNAL %s' %
                         (len(folio_ids), j_id))
            folio_set = set()
            for f_id in folio_ids:
                folio_brw = folio_obj.browse(cr, uid, f_id, context=context)
                m = re.match(expr, folio_brw.name)
                if m is not None:
                    expr2 = re.compile('^' + m.group())
                    expr2 = expr2.sub('', folio_brw.name)
                    folio_set.add(int(expr2))
                    #_logger.info('%s <= MATCH'%folio_brw.name)
                    MATCH += 1
                else:
                    _logger.info('%s <= WRONG' % folio_brw.name)
                    WRONG += 1
                FOLIOS += 1
            actual_folio_set = set(range(1, seq_brw.number_next))
            gap_folio_set = []
            if folio_set:
                gap_folio_set = actual_folio_set - folio_set
            _logger.info('GAP FOLIO SET %s' % gap_folio_set)
            for gap in gap_folio_set:
                d = ir_seq_obj._interpolation_dict()
                try:
                    interpolated_prefix = ir_seq_obj._interpolate(
                        seq_brw.prefix, d)
                    interpolated_suffix = ir_seq_obj._interpolate(
                        seq_brw.suffix, d)
                except ValueError:
                    _logger.info(
                        "Invalid prefix or suffix for sequence '%s'" % seq_brw.name)
                gap_name = interpolated_prefix + \
                    '%%0%sd' % seq_brw.padding % gap + interpolated_suffix
                _logger.info('GAP NAME %s' % gap_name)
                flag = True
                next_gap = gap
                next_gap_id = False
                while flag:
                    next_gap += 1
                    if next_gap in gap_folio_set:
                        continue
                    else:
                        flag = False
                        if next_gap >= seq_brw.number_next:
                            break
                        else:
                            next_gap_name = interpolated_prefix + \
                                '%%0%sd' % seq_brw.padding % next_gap + interpolated_suffix
                            next_gap_id = folio_obj.search(cr, uid, [(
                                'name', '=', next_gap_name), ('journal_id', '=', j_id)], context=context)
                            next_gap_id = next_gap_id and next_gap_id[
                                0] or False
                period_id = False
                date = False
                if next_gap_id:
                    ngval_brw = folio_obj.browse(
                        cr, uid, next_gap_id, context=context)
                    date = ngval_brw.date or False
                    period_id = ngval_brw.period_id and ngval_brw.period_id.id or False
                folio_obj.create(cr, uid, {
                    'name': gap_name,
                    'journal_id': j_id,
                    'date': date,
                    'period_id': period_id,
                })
            GAPS += len(gap_folio_set)
        _logger.info('MATCHES: %s' % MATCH)
        _logger.info('WRONGS: %s' % WRONG)
        _logger.info('FOLIOS: %s' % FOLIOS)
        _logger.info('GAPS: %s' % GAPS)
        return {'type': 'ir.actions.act_window_close'}
