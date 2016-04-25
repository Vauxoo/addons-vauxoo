# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2012-TODAY OpenERP S.A. <http://openerp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.mail.tests.common import TestMail


class TestMailMailAuthor(TestMail):
    """These tests validate the cases when partner is allow to receive
        your own emails

    """

    # ----------------------------------------------------------
    # receive_my_emails | notify_email | receive your own email?
    # ----------------------------------------------------------
    #   True                 always                 True
    #   False                always                 False
    #   True                 none                   False
    #   False                none                   False
    # -----------------------------------------------------------

    def test_receive_mail_author(self):
        """This test validate when partner that send email must receive
            your own email, because has this configuration:
                @receive_my_emails: True
                @notify_email: always
        """

        cr, uid = self.cr, self.uid
        context = {}
        context['mail_notify_force_send'] = False

        self.res_partner.write(
            cr, uid, self.partner_raoul_id,
            {'receive_my_emails': True, 'notify_email': 'always'})

        pigs_msg_id = self.mail_group.message_post(
            cr, self.user_raoul.id, self.group_pigs_id, body='Message',
            partner_ids=[self.partner_bert_id], context=context)

        mail_msg_id = self.mail_mail.search(
            cr, uid, [('mail_message_id', '=', pigs_msg_id)])

        mail_id = self.mail_mail.browse(cr, uid, mail_msg_id)[0]
        partner_to_notify = [
            mail_partner.id for mail_partner in mail_id.recipient_ids]

        self.assertEqual(
            partner_to_notify, [self.partner_bert_id, self.partner_raoul_id],
            'Partner to notify incorrect, should be two partners to notify')

    def test_not_receive_mail_author(self):
        """This test validate when partner that send email must not receive
            your own email, because has this configuration:
                @receive_my_emails: False
                @notify_email: always
        """

        cr, uid = self.cr, self.uid
        context = {}
        context['mail_notify_force_send'] = False

        self.res_partner.write(
            cr, uid, self.partner_raoul_id,
            {'receive_my_emails': False, 'notify_email': 'always'})

        pigs_msg_id = self.mail_group.message_post(
            cr, self.user_raoul.id, self.group_pigs_id, body='Message',
            partner_ids=[self.partner_bert_id], context=context)

        mail_msg_id = self.mail_mail.search(
            cr, uid, [('mail_message_id', '=', pigs_msg_id)])

        mail_id = self.mail_mail.browse(cr, uid, mail_msg_id)[0]
        partner_to_notify = [
            mail_partner.id for mail_partner in mail_id.recipient_ids]

        self.assertEqual(
            partner_to_notify, [self.partner_bert_id],
            'Partner to notify incorrect, should be only partner to notify')

    def test_not_receive_mail_author_2(self):
        """This test validate when partner that send email must not receive
            your own email, because has this configuration:
                @receive_my_emails: True
                @notify_email: none
        """

        cr, uid = self.cr, self.uid
        context = {}
        context['mail_notify_force_send'] = False

        self.res_partner.write(
            cr, uid, self.partner_raoul_id,
            {'receive_my_emails': True, 'notify_email': 'none'})

        pigs_msg_id = self.mail_group.message_post(
            cr, self.user_raoul.id, self.group_pigs_id, body='Message',
            partner_ids=[self.partner_bert_id], context=context)

        mail_msg_id = self.mail_mail.search(
            cr, uid, [('mail_message_id', '=', pigs_msg_id)])

        mail_id = self.mail_mail.browse(cr, uid, mail_msg_id)[0]
        partner_to_notify = [
            mail_partner.id for mail_partner in mail_id.recipient_ids]

        self.assertEqual(
            partner_to_notify, [self.partner_bert_id],
            'Partner to notify incorrect, should be only partner to notify')

    def test_not_receive_mail_author3(self):
        """This test validate when partner that send email must not receive
            your own email, because has this configuration:
                @receive_my_emails: False
                @notify_email: none
        """

        cr, uid = self.cr, self.uid
        context = {}
        context['mail_notify_force_send'] = False

        self.res_partner.write(
            cr, uid, self.partner_raoul_id,
            {'receive_my_emails': False, 'notify_email': 'none'})

        pigs_msg_id = self.mail_group.message_post(
            cr, self.user_raoul.id, self.group_pigs_id, body='Message',
            partner_ids=[self.partner_bert_id], context=context)

        mail_msg_id = self.mail_mail.search(
            cr, uid, [('mail_message_id', '=', pigs_msg_id)])

        mail_id = self.mail_mail.browse(cr, uid, mail_msg_id)[0]
        partner_to_notify = [
            mail_partner.id for mail_partner in mail_id.recipient_ids]

        self.assertEqual(
            partner_to_notify, [self.partner_bert_id],
            'Partner to notify incorrect, should be only partner to notify')
