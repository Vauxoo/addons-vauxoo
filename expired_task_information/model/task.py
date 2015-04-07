#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#
#
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
#

from openerp.osv import fields, osv
from datetime import *


class task_expired_config(osv.Model):

    """
    """
    _name = 'task.expired.config'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(task_expired_config, self).default_get(cr, uid, fields,
                                                           context=context)
        model_ids = self.search(cr, uid, [], context=context)
        if model_ids:
            return self.read(cr, uid, model_ids[0], [], context=context)
        return res

    _columns = {

        'without_change': fields.integer('Without Changes Days',
                                         help='Days number that tasks may '
                                         'have without changes.\n'
                                         'When these days finish an '
                                         'email information is sent'),
        'before_expiry': fields.integer('Before Expiry',
                                        help='Number days before to the '
                                        'expiry day to send an alert '
                                        'for email'),
    }

    def create_config(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        model_ids = self.search(cr, uid, [], context=context)
        dict_read = self.read(cr, uid, ids[0], [], context=context)
        if model_ids:
            self.write(cr, uid, model_ids, dict_read, context=context)
            return {'type': 'ir.actions.act_window_close'}

        return {'type': 'ir.actions.act_window_close'}

    def send_expiration_message(self, cr, uid, context=None):
        context = context or {}

        mail_mail = self.pool.get('mail.mail')
        message = self.pool.get('mail.message')
        task_obj = self.pool.get('project.task')
        work_obj = self.pool.get('project.task.work')
        config_ids = self.search(cr, uid, [], context=context)
        if config_ids:
            config_brw = self.browse(cr, uid, config_ids[0], context=context)
            today = date.today()
            before_expiry = today + timedelta(days=config_brw.before_expiry)
            last_change = today - timedelta(days=config_brw.without_change)
            today = today.strftime('%Y-%m-%d')
            before_expiry = before_expiry.strftime('%Y-%m-%d')
            last_change = last_change.strftime('%Y-%m-%d')
            task_ids = task_obj.search(cr, uid,
                                       [('state', 'not in', ('done', 'cancelled')),
                                        ('user_id', '!=', False)],
                                       context=context)
            for task in task_ids and task_obj.browse(cr, uid, task_ids):
                msg_expired = ''
                msg_expiredp = ''
                last_message_ids = message.search(cr, uid,
                                   [('res_id', '=', task.id),
                                   ('model', '=', 'project.task')],
                    context, order='date desc')
                last_fecha = last_message_ids and message.browse(cr, uid, last_message_ids[0]).date
                #~ Para cuando la tarea se vencio a la fecha de hoy.
                #~ if task.date_deadline and task.date_deadline <= today:
                #~ msg_expired = ('<p>Esta tarea ha expirado el dia %s \
                #~ </p>', task.date_deadline)
                #~ msg_expiredp = 'ACTIVIDAD VENCIDA'
                if work_obj.search(cr, uid,
                                   [('date', '<=', last_change),
                                    ('task_id', '=', task.id)],
                                   context) or \
                        last_fecha and last_fecha <= last_change:
                    msg_expiredp = 'ACTIVIDAD SIN CAMBIOS'
                    msg_expired = ('<p>La Tarea tiene mas de %s dia(s) sin \
                                                      cambios</p>'
                                   % config_brw.without_change)
                #~ Para cuando la tarea tiene x cantidad de dias vencida.
                #~ if task.date_deadline and task.date_deadline == before_expiry:
                    #~ msg_expired = ('<p>La Tarea expirara en %s \
                    #~ dias</p>' % config_brw.before_expiry)
                    #~ msg_expiredp = 'ACTIVIDAD VENCIDA'
                if msg_expired:
                    html = r"""<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>*|MC:SUBJECT|*</title>
        <style type="text/css">
            /* Client-specific Styles */
            #outlook a{padding:0;} /* Force Outlook to provide a "view in browser" button. */
            body{width:100% !important;} .ReadMsgBody{width:100%;} .ExternalClass{width:100%;} /* Force Hotmail to display emails at full width */
            body{-webkit-text-size-adjust:none;} /* Prevent Webkit platforms from changing default text sizes. */

            /* Reset Styles */
            body{margin:0; padding:0;}
            img{border:0; height:auto; line-height:100%; outline:none; text-decoration:none;}
            table td{border-collapse:collapse;}
            #backgroundTable{height:100% !important; margin:0; padding:0; width:100% !important;}

            /* Template Styles */

            /* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: COMMON PAGE ELEMENTS /\/\/\/\/\/\/\/\/\/\ */

            /**
            * @tab Page
            * @section background color
            * @tip Set the background color for your email. You may want to choose one that matches your company's branding.
            * @theme page
            */
            body, #backgroundTable{
                /*@editable*/ background-color:#FAFAFA;
            }

            /**
            * @tab Page
            * @section email border
            * @tip Set the border for your email.
            */
            #templateContainer{
                /*@editable*/ border:0;
            }

            /**
            * @tab Page
            * @section heading 1
            * @tip Set the styling for all first-level headings in your emails. These should be the largest of your headings.
            * @style heading 1
            */
            h1, .h1{
                /*@editable*/ color:#202020;
                display:block;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:40px;
                /*@editable*/ font-weight:bold;
                /*@editable*/ line-height:100%;
                margin-top:2%;
                margin-right:0;
                margin-bottom:1%;
                margin-left:0;
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Page
            * @section heading 2
            * @tip Set the styling for all second-level headings in your emails.
            * @style heading 2
            */
            h2, .h2{
                /*@editable*/ color:#404040;
                display:block;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:18px;
                /*@editable*/ font-weight:bold;
                /*@editable*/ line-height:100%;
                margin-top:2%;
                margin-right:0;
                margin-bottom:1%;
                margin-left:0;
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Page
            * @section heading 3
            * @tip Set the styling for all third-level headings in your emails.
            * @style heading 3
            */
            h3, .h3{
                /*@editable*/ color:#606060;
                display:block;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:16px;
                /*@editable*/ font-weight:bold;
                /*@editable*/ line-height:100%;
                margin-top:2%;
                margin-right:0;
                margin-bottom:1%;
                margin-left:0;
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Page
            * @section heading 4
            * @tip Set the styling for all fourth-level headings in your emails. These should be the smallest of your headings.
            * @style heading 4
            */
            h4, .h4{
                /*@editable*/ color:#808080;
                display:block;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:14px;
                /*@editable*/ font-weight:bold;
                /*@editable*/ line-height:100%;
                margin-top:2%;
                margin-right:0;
                margin-bottom:1%;
                margin-left:0;
                /*@editable*/ text-align:left;
            }

            /* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: PREHEADER /\/\/\/\/\/\/\/\/\/\ */

            /**
            * @tab Header
            * @section preheader style
            * @tip Set the background color for your email's preheader area.
            * @theme page
            */
            #templatePreheader{
                /*@editable*/ background-color:#FAFAFA;
            }

            /**
            * @tab Header
            * @section preheader text
            * @tip Set the styling for your email's preheader text. Choose a size and color that is easy to read.
            */
            .preheaderContent div{
                /*@editable*/ color:#707070;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:10px;
                /*@editable*/ line-height:100%;
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Header
            * @section preheader link
            * @tip Set the styling for your email's preheader links. Choose a color that helps them stand out from your text.
            */
            .preheaderContent div a:link, .preheaderContent div a:visited, /* Yahoo! Mail Override */ .preheaderContent div a .yshortcuts /* Yahoo! Mail Override */{
                /*@editable*/ color:#336699;
                /*@editable*/ font-weight:normal;
                /*@editable*/ text-decoration:underline;
            }

            /**
            * @tab Header
            * @section social bar style
            * @tip Set the background color and border for your email's footer social bar.
            */
            #social div{
                /*@editable*/ text-align:right;
            }

            /* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: HEADER /\/\/\/\/\/\/\/\/\/\ */

            /**
            * @tab Header
            * @section header style
            * @tip Set the background color and border for your email's header area.
            * @theme header
            */
            #templateHeader{
                /*@editable*/ background-color:#FFFFFF;
                /*@editable*/ border-bottom:5px solid #505050;
            }

            /**
            * @tab Header
            * @section header text
            * @tip Set the styling for your email's header text. Choose a size and color that is easy to read.
            */
            .headerContent{
                /*@editable*/ color:#202020;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:34px;
                /*@editable*/ font-weight:bold;
                /*@editable*/ line-height:100%;
                /*@editable*/ padding:10px;
                /*@editable*/ text-align:right;
                /*@editable*/ vertical-align:middle;
            }

            /**
            * @tab Header
            * @section header link
            * @tip Set the styling for your email's header links. Choose a color that helps them stand out from your text.
            */
            .headerContent a:link, .headerContent a:visited, /* Yahoo! Mail Override */ .headerContent a .yshortcuts /* Yahoo! Mail Override */{
                /*@editable*/ color:#336699;
                /*@editable*/ font-weight:normal;
                /*@editable*/ text-decoration:underline;
            }

            #headerImage{
                height:auto;
                max-width:600px !important;
            }

            /* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: MAIN BODY /\/\/\/\/\/\/\/\/\/\ */

            /**
            * @tab Body
            * @section body style
            * @tip Set the background color for your email's body area.
            */
            #templateContainer, .bodyContent{
                /*@editable*/ background-color:#FDFDFD;
            }

            /**
            * @tab Body
            * @section body text
            * @tip Set the styling for your email's main content text. Choose a size and color that is easy to read.
            * @theme main
            */
            .bodyContent div{
                /*@editable*/ color:#505050;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:14px;
                /*@editable*/ line-height:150%;
                /*@editable*/ text-align:justify;
            }

            /**
            * @tab Body
            * @section body link
            * @tip Set the styling for your email's main content links. Choose a color that helps them stand out from your text.
            */
            .bodyContent div a:link, .bodyContent div a:visited, /* Yahoo! Mail Override */ .bodyContent div a .yshortcuts /* Yahoo! Mail Override */{
                /*@editable*/ color:#336699;
                /*@editable*/ font-weight:normal;
                /*@editable*/ text-decoration:underline;
            }

            .bodyContent img{
                display:inline;
                height:auto;
            }

            /* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: SIDEBAR /\/\/\/\/\/\/\/\/\/\ */

            /**
            * @tab Sidebar
            * @section sidebar style
            * @tip Set the background color and border for your email's sidebar area.
            */
            #templateSidebar{
                /*@editable*/ background-color:#FDFDFD;
            }

            /**
            * @tab Sidebar
            * @section sidebar style
            * @tip Set the background color and border for your email's sidebar area.
            */
            .sidebarContent{
                /*@editable*/ border-right:1px solid #DDDDDD;
            }

            /**
            * @tab Sidebar
            * @section sidebar text
            * @tip Set the styling for your email's sidebar text. Choose a size and color that is easy to read.
            */
            .sidebarContent div{
                /*@editable*/ color:#505050;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:10px;
                /*@editable*/ line-height:150%;
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Sidebar
            * @section sidebar link
            * @tip Set the styling for your email's sidebar links. Choose a color that helps them stand out from your text.
            */
            .sidebarContent div a:link, .sidebarContent div a:visited, /* Yahoo! Mail Override */ .sidebarContent div a .yshortcuts /* Yahoo! Mail Override */{
                /*@editable*/ color:#336699;
                /*@editable*/ font-weight:normal;
                /*@editable*/ text-decoration:underline;
            }

            .sidebarContent img{
                display:inline;
                height:auto;
            }

            /* /\/\/\/\/\/\/\/\/\/\ STANDARD STYLING: FOOTER /\/\/\/\/\/\/\/\/\/\ */

            /**
            * @tab Footer
            * @section footer style
            * @tip Set the background color and top border for your email's footer area.
            * @theme footer
            */
            #templateFooter{
                /*@editable*/ background-color:#FAFAFA;
                /*@editable*/ border-top:3px solid #909090;
            }

            /**
            * @tab Footer
            * @section footer text
            * @tip Set the styling for your email's footer text. Choose a size and color that is easy to read.
            * @theme footer
            */
            .footerContent div{
                /*@editable*/ color:#707070;
                /*@editable*/ font-family:Arial;
                /*@editable*/ font-size:11px;
                /*@editable*/ line-height:125%;
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Footer
            * @section footer link
            * @tip Set the styling for your email's footer links. Choose a color that helps them stand out from your text.
            */
            .footerContent div a:link, .footerContent div a:visited, /* Yahoo! Mail Override */ .footerContent div a .yshortcuts /* Yahoo! Mail Override */{
                /*@editable*/ color:#336699;
                /*@editable*/ font-weight:normal;
                /*@editable*/ text-decoration:underline;
            }

            .footerContent img{
                display:inline;
            }

            /**
            * @tab Footer
            * @section social bar style
            * @tip Set the background color and border for your email's footer social bar.
            * @theme footer
            */
            #social{
                /*@editable*/ background-color:#FFFFFF;
                /*@editable*/ border:0;
            }

            /**
            * @tab Footer
            * @section social bar style
            * @tip Set the background color and border for your email's footer social bar.
            */
            #social div{
                /*@editable*/ text-align:left;
            }

            /**
            * @tab Footer
            * @section utility bar style
            * @tip Set the background color and border for your email's footer utility bar.
            * @theme footer
            */
            #utility{
                /*@editable*/ background-color:#FAFAFA;
                /*@editable*/ border-top:0;
            }

            /**
            * @tab Footer
            * @section utility bar style
            * @tip Set the background color and border for your email's footer utility bar.
            */
            #utility div{
                /*@editable*/ text-align:left;
            }

            #monkeyRewards img{
                max-width:170px !important;
            }
        </style>
    </head>
    <body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0">
        <center>
            <table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" id="backgroundTable">
                <tr>
                    <td align="center" valign="top">
                        <table border="0" cellpadding="0" cellspacing="0" width="600" id="templateContainer">
                            <tr style="margin: 0px; padding: 0px; background-color: rgb(247, 247, 247);">
                                <td align="center" valign="top">
                                    <!-- // Begin Template Header \\ -->
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 0px; padding: 0px;  background-color: rgb(253, 253, 253);">
                                        <tr>
                                            <td class="headerContent">
                                                <img src="http://drive.google.com/uc?export=view&id=0B0ktFgMTDB8KV2FGWWhOaEMwbm8" style="max-width:60px; padding: 2px 2px 2px;" id="headerImage campaign-icon" mc:label="header_image" mc:edit="header_image" mc:allowtext />
                                            </td>

                                            <td class="headerContent" width="100%" style="padding-left:10px; padding-right:20px;">
                                                <div mc:edit="Header_content">
                                                    <h2>"""
                    html += task.name
                    html += """</h2>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                    <!-- // End Template Header \\ -->
                                </td>
                            </tr>
                            <tr>
                            <td align="center" style="margin: 0px; padding: 0px; width: 600px; background-color: #E8C808">
                                <div style="font-size:1.3em; font-family:Arial"><b>"""
                    html += msg_expiredp
                    html += """</b></div>
                            </td>
                            </tr>
                            <tr>
                                <td align="center" valign="top">
                                    <!-- // Begin Template Body \\ -->
                                    <table border="0" cellpadding="10" cellspacing="0" width="600" style="margin: 0px; padding: 0px; width: 600px; background-color: rgb(247, 247, 247);">
                                        <tr>
                                            <!-- // Begin Sidebar \\  -->
                                            <td valign="top" width="180" id="templateSidebar">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                    <tr>
                                                        <td valign="top">
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <!-- // End Sidebar \\ -->
                                            <td valign="top" class="bodyContent">

                                                <!-- // Begin Module: Standard Content \\ -->
                                                <table border="0" cellpadding="10" cellspacing="0" width="600">
                                                    <tr>
                                                        <td valign="top" style="padding-left:0;">
                                                            <div mc:edit="std_content00">
                                                                <h2 class="h2">Hola @"""
                    html += task.user_id.name
                    html += """</h2>
                    <h3 class="h3">"""
                    html += msg_expired
                    html += """</h3>
<pre style="font-size:1.1em; font-family:Arial">Podrias ser tan amable de comentarnos el estatus de la misma por este medio.

Si es por alguna de las 3 siguientes razones, o alguna ajena a estos puntos justificalo por favor:

<b>1.- Aun no cargas tus labores en la instancia. </b>
(Recuerda que gran parte del trabajo que realizas esta en cargar las horas, asi demuestras en que te ocupas realmente).

<b>2.- Se te pidio la postergaras.</b>
(Si fue asi espero nos comentes por esta via las razones que se te dieron, y por favor actualices la fecha correcta).

<b>3.- No la habias visto, o tienes alguna duda con el contenido, si es asi puedes colocar aqui cuales son tus dudas.</b>
(La comunicacion es importante para un mejor desarrollo de tus actividades).</pre>
                                                                <br />
                                                        </div>
                                                    </td>
                                                    </tr>
                                                </table>
                                                <!-- // End Module: Standard Content \\ -->

                                            </td>
                                        </tr>
                                    </table>
                                    <!-- // End Template Body \\ -->
                                </td>
                        </table>
                        <br />
                    </td>
                </tr>
            </table>
        </center>
    </body>
</html>"""
                    mail_id = mail_mail.create(cr, uid,
                                               {
                                                   'model': 'project.task',
                                                   'res_id': task.id,
                                                   'subject': ('#' + str(task.id) + ' - ' + task.name),
                                                   'body_html': html,
                                                   'auto_delete': True,
                                               }, context=context)
                    task.user_id and mail_mail.send(cr, uid, [mail_id],
                                   recipient_ids=[task.user_id.partner_id.id],
                                   context=context)
        return True
