Project Configuration
=====================

**When you install this module:**

* Load two new columns called:
    * Backlog.
    * Testing Leader.


  .. image:: project_conf/static/src/img/columns.png

* Load the templates automatically:
    * Send Task from Email: Email Template to send email by task.
    * Template to Outgoing mail server.
    * Send Server's Credentials Sending Process: After install server, the user should send this email.

**What need you do after install this module:**

- For configurate server go to the Menu: Settings -> Technical -> Email -> Outgoing Mail Servers -> OUT SERVER, set password for username and Test Conection.

  .. image:: project_conf/static/src/img/test_connection.png

- For active any template go to the Menu: Settings -> Technical-> Email-> Templates, select the template and action triggers **Act context action**:

  .. image:: project_conf/static/src/img/add_context_action.png

  And before for see the action, go to any task and press More-> Send Mail (New Task)

  .. image:: project_conf/static/src/img/send_mail.png

- Go to the Users and set the Email.
- Go to the Menu: Settings -> Technical-> Scheduler -> Scheduler Actions. Sign
  in template: **Email Queue Manager**, configurate Interval Number, and
  Interval Unit.
- Configurate for projects required the columns:
    * Backlog.
    * Project Leader.
- For template: **Server's Credentials Sending Process**, you may
  replace words blue colors with real information.
- For template "New Task", you should replace the piece of code:
  http://erp.vauxoo.com to your url.
