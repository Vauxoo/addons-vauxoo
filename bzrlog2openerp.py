#!/usr/bin/python
import sys
from oerplib import OERP
import bzrlog2dict as b2dict

def import_element(conn):
    vals = {
            'name': 'Hola Mundo',
            'res_id': 'julio@vauxoo.com-20130415213003-pi19rfwep88u5scs'
            }
    return conn.create('project.task', vals)



if __name__ == '__main__':
    server = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    port = sys.argv[4]
    dbname = sys.argv[5]
    conn = OERP(server, dbname, 'xmlrpc', int(port), 120, '7.0')
    u = conn.login(user, password)
    print import_element(conn) 
