# -*- encoding: utf-8 -*-
{
    "name" : "Crm Profiling Report",
    "version" : "0.1",
    "depends" : ["base","crm_profiling","email_template"],
    "author" : "",
    "description" : """
    What do this module:

    This module prints the report of the accepted partners and send it by mail

    How Install:
    1.- In the menu Tools/Configuration/Email Template/Email Accounts, the accounts are configured to send mail as follows Fill the fields as follows:
          -Description: This stands as the mail sender's description Example: John Doe <john@doe.com>
          -Server: smtp server is placed in the mail provider which is affiliated
                GMAIL: smtp.gmail.com
                HOTMAIL: smtp.live.com
                YAHOO: smtp.yahoo.mail.com
          -Smtp port: port is placed smtp mail provider which is affiliated
                GMAIL: 587
                HOTMAIL: 25
                YAHOO: 587
          -From Email: Put the mail sender. Example: John Doe <john@doe.com>.
          -Password: The password is placed in the mail introduced in the previous field (This is used to test the connection to the SMTP server).
          -User Name: Place the user name if required by the smtp server.
        Click the button Test Outgoing Connection to test the SMTP server connection, otherwise check the above fields.
    2.- In the menu Tools/Configuration/Email Template/Email Templates, the templates are configured as follows Fill the fields as follows:
        2.1- In page Mail Details
          -Name: Write the name that going to have the template  (CRM Profile Report Template).
          -Resource: n this field we select the model from which we send the email  (res.partner).
          -Email Account: Select the account created in the previous step.
          -Recipient (to) write to whom it is addressed mail (${object.email})
          -Subject: write the subject of the mail (CRM Profile Report)
        2.2.- In page Advanced
          -Report to send: Select this report (Print Profile Report)
        2.3.- We create the action with the button Create Action.
        2.4.- Save the configuration.
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [    ],
    "demo_xml" : [    ],
    "update_xml" : [
    "crm_profile_reporting_report.xml",
    "data/crm_profiling_data.xml",
    ],
    "active": False,
    "installable": True,
}
