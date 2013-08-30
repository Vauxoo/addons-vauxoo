query_template = "SELECT %s FROM account_account"
columns = range(1, 5)
for i in columns:
    # sum_colums = '0 AS col%s'%(columns)
    # print map(lambda x: x, columns)
    cols_query = ', '.join(map(lambda x: i == x and 'SUM(debit+credit) AS col%s' % (
        x,) or '0 AS col%s' % (x,), columns))
    dates_query = ' '
    dates_query += ' BETWEEN %s AND %s)'
    # query_full = query_template%(sum_colums)
# print query_full

# cfd_data_invoices_str = '\n'.join( map(lambda x: '|'.join(x) + '|',
# cfd_data_invoices) )

for i in range(5)[::-1]:
    print i
