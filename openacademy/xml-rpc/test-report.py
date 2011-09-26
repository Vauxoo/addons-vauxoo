# -*- encoding: utf-8 -*-
import time
import base64
import xmlrpclib
HOST='localhost'
PORT=8069
DB='security2'
USER='admin'
PASS='admin'
url ='http://%s:%d/xmlrpc/' % (HOST,PORT)


sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
uid = sock.login(DB,USER,PASS)
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
printsock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/report')
model = 'account.invoice'
ids = sock.execute(DB, uid, PASS, 'account.invoice', 'search', [('type', '=', 'out_invoice')])
id_report = printsock.report(DB, uid, PASS, model, ids, {'model': model, 'id': ids[0], 'report_type':'pdf'})
time.sleep(5)
state = False
attempt = 0
while not state:
    report = printsock.report_get(DB, uid, PASS, id_report)
    state = report['state']
    if not state:
        time.sleep(1)
        attempt += 1
    if attempt>200:
        print 'Printing aborted, too long delay !'

    string_pdf = base64.decodestring(report['result'])
    file_pdf = open('file.pdf','w')
    file_pdf.write(string_pdf)
    file_pdf.close()
