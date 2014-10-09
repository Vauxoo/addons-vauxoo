# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 09:56:42 2012

@author: truiz
"""
import xlrd
import xmlrpclib
from datetime import datetime
from ustr_test import ustr


def loadProjectsTasks(fileName, HOST, PORT, DB, USER, PASS):
    ISSUES_PAGE = 0
    TASKS_PAGE = 1
    WORKS_PAGE = 2

    ''' Objects needed for rpc calls '''
    url = 'http://%s:%d/xmlrpc/' % (HOST, PORT)
    common_proxy = xmlrpclib.ServerProxy(url + 'common')
    object_proxy = xmlrpclib.ServerProxy(url + 'object')
    uid = common_proxy.login(DB, USER, PASS)

    ID_ADDR = 1

    def clean(cadena):
        if isinstance(cadena, str):
            return cadena and ustr(cadena).strip() or None
        return cadena

    def cleanDict(d):
        res = {}
        for k in d:
            if not d[k] is None:
                res.update({k: d[k]})
        return res

    def readSheet(fileName, nSheet):
        # Open workbook
        book = xlrd.open_workbook(fileName, formatting_info=True)
        sheet = book.sheet_by_index(nSheet)
        values = []
        for T in range(sheet.nrows):
            values.append([clean(v) for v in sheet.row_values(T)])

        return values

    def searchTasks(project_id, tasks):
        res = []
        for t in tasks:
            if t[0] != 'ID':
                if int(t[1]) == project_id:
                    res.append(t)
        return res

    def searchWorks(task_id, works):
        res = []
        for w in works:
            if w[0] != 'ID TASK':
                if int(w[0]) == task_id:
                    res.append(w)
        return res
    # Read project issue sheet
    issues = readSheet(fileName, ISSUES_PAGE)
    # Read project tasks sheet
    tasks = readSheet(fileName, TASKS_PAGE)
    # Read project work sheet
    works = readSheet(fileName, WORKS_PAGE)
    for issue in issues:
        if issue[0] != 'ID':
            if issue[4]:
                user_mail = object_proxy.execute(
                    DB, uid, PASS, 'res.users', 'read', int(issue[4]),
                    ['user_email'])
            else:
                user_mail['user_email'] = None
            addr = issue[7] and (int(issue[
                                 7]) == 3 and ID_ADDR or int(issue[7])) or None
            values_issue = {
                'name': ustr(issue[1]),
                'categ_id': int(issue[3]),
                'project_id': int(issue[2]),
                'assigned_to': issue[4] and int(issue[4]) or None,
                'type_id': int(issue[5]),
                'partner_id': int(issue[6]),
                'partner_address_id': addr,
                'state': 'open',
                'description': ustr(issue[8]),
                'email_from': issue[4] and user_mail['user_email'] or None,
                'active': True,
            }
            values_issue = cleanDict(values_issue)
            project_id = object_proxy.execute(
                DB, uid, PASS, 'project.issue', 'create', values_issue)
            if project_id:
                if issue[4]:
                    object_proxy.execute(DB, uid, PASS, 'project.issue',
                                        'write', [
                                         project_id],
                                         {'assigned_to': int(issue[4]),
                                         'user_id': int(issue[4])})
                project_tasks = searchTasks(int(issue[0]), tasks)
                if project_tasks:
                    for task in project_tasks:
                        values_tasks = {
                            'name': values_issue['name'],
                            'project_id': values_issue['project_id'],
                            'assigned_to': values_issue['assigned_to'],
                            'user_id': values_issue['assigned_to'],
                            'planned_hours': task[2],
                            'remaining_hours': task[3],
                            'type_id': values_issue['type_id'],
                            'partner_id': values_issue['partner_id'],
                            'state': 'open',
                            'date_start': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                            'date_end': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                            'description': values_issue['description'],
                        }
                        values_tasks = cleanDict(values_tasks)
                        task_id = object_proxy.execute(
                            DB, uid, PASS, 'project.task', 'create', values_tasks)
                        if task_id:
                            object_proxy.execute(DB, uid, PASS,
                                                 'project.issue', 'write', [
                                                     project_id],
                                                 {'task_id': task_id})
                            task_works = searchWorks(int(task[0]), works)
                            if task_works:
                                for work in task_works:
                                    values_works = {
                                        'name': ustr(work[1]),
                                        'hours': work[2],
                                        'date': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                                        'user_id': values_issue['assigned_to'],
                                        'task_id': task_id,
                                    }
                                    work_id = object_proxy.execute(
                                        DB, uid, PASS, 'project.task.work',
                                        'create', values_works)
                                    if work_id:
                                        object_proxy.execute(DB, uid, PASS,
                                                'project.task', 'write', [
                                                    task_id], {'state': task[4]})
                object_proxy.execute(DB, uid, PASS, 'project.issue', 'write', [
                                     project_id], {'state': issue[9]})
