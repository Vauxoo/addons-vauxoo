##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Maria Gabriela Quilarque)
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
##############################################################################
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
{
    "name": "Project Configuration", 
    "version": "0.1", 
    "author": [
        "Vauxoo"
    ], 
    "category": "Generic Modules", 
    "description": """
Project Configuration
=====================

**When you install this module:**
   * Load  two new columns called:
        * Backlog.
        * Project Leader.

.. image:: project_conf/static/src/img/columns.png
.
   * Load the templates automatically:
       * Envio de Tarea por Email: Email Template to send email by task.
       * Template to Outgoing mail server.
       * Envio de Reporte de Credenciales del Server: After install server, the user should send this email.

**What need you do after install this module:**

    - For configurate server go to the Menu: Setting->Technical->Email->Outgoing Mail Servers->OUT SERVER, set password for username and Test Conecction.

.. image:: project_conf/static/src/img/test_connection.png
.
    - For active any template go to the Menu: Setting->Technical->Email->Templates, select the template and action triggers **Act context action**:

.. image:: project_conf/static/src/img/add_context_action.png
.
      And before for see the action, go to any task and press More-> Send Mail (New Task)

.. image:: project_conf/static/src/img/send_mail.png
.

    - Go to the Users and set the Email.
    - Go to the Menu: Settings-> Technical-> Scheduler -> Scheduler Actions. Sign in template: **Email Queue Manager**, configurate Interval Number,
      and Interval Unit.
    - Configurate for projects required the columns:
          * Backlog.
          * Project Leader.
    - For template: **Envio de Reporte de Credenciales del Server**, you may replace words blue colors with real information.
    - For template "New Task", you should replace the piece of codigo: http://erp.vauxoo.com to your url.
""", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "project", 
        "email_template"
    ], 
    "demo": [], 
    "data": [
        "data/project_conf.xml", 
        "view/project_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}