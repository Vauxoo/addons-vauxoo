#!/usr/bin/python
import sys
from oerplib import OERP
from pprint import pprint
import bzrlog2dict as b2dict

def import_element(conn):
    '''
    TODO: Verify just one import per res_id.
    TODO: Send a message, how do i test it
    '''
    commit = b2dict.parse_metadata(section)
    DateCommit = commit['timestamp'].split(' ')
    vals = {
            'name': commit['message'][:60],
            'res_id': commit['revision-id'],
            'url_branch': 'https://launchpad.net/xmind-openerp',
            'description': commit['message'],
            'date_end': DateCommit[1]+' '+DateCommit[2],
            }
    return conn.create('project.task', vals)

if __name__ == '__main__':
    section = '''
revno: 52 [merge]
revision-id: nhomae@gmail.com-20130416014106-o3n23he96s1pvaec
parent: nhomae@gmail.com-20130415213525-m1flejc57jr1op60
parent: julio@vauxoo.com-20130416010149-oex0miuij9t35a72
committer: Nhomar Hernandez <nhomae@gmail.com>
branch nick: xmind-openerp
timestamp: Mon 2013-04-15 21:11:06 -0530
message:

  [MERGE] Added given kanban wbs_codefield and off the field wbs
'''
    server = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    port = sys.argv[4]
    dbname = sys.argv[5]
    conn = OERP(server, dbname, 'xmlrpc', int(port), 120, '7.0')
    u = conn.login(user, password)
    print import_element(conn) 
