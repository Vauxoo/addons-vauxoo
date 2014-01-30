# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
############################################################################
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
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
from openerp import tools
from openerp import netsvc
from openerp.tools.misc import ustr
import wizard
import base64
import xml.dom.minidom
import time
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from xml.dom import minidom
import urllib
import pooler
from tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
from datetime import datetime, timedelta
import time


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def add_node(self, node_name=None, attrs=None, parent_node=None,
                 minidom_xml_obj=None, attrs_types=None, order=False):
        """
            @params node_name : Name node to added
            @params attrs : Attributes to add in node
            @params parent_node : Node parent where was add new node children
            @params minidom_xml_obj : File XML where add nodes
            @params attrs_types : Type of attributes added in the node
            @params order : If need add the params in order in the XML, add a
                    list with order to params
        """
        if not order:
            order = attrs
        new_node = minidom_xml_obj.createElement(node_name)
        for key in order:
            if attrs_types[key] == 'attribute':
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement(key)
                text_node = minidom_xml_obj.createTextNode(attrs[key])

                key_node.appendChild(text_node)
                new_node.appendChild(key_node)
        parent_node.appendChild(new_node)
        return new_node

    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context=None):
        """
         @params xml_res_str : File XML
         @params comprobante : Name to the Node that contain the information the XML
        """
        if context is None:
            context = {}
        if xml_res_str:
            node_Addenda = xml_res_str.getElementsByTagName('cfdi:Addenda')
            if len(node_Addenda) == 0:
                nodeComprobante = xml_res_str.getElementsByTagName(
                    comprobante)[0]
                node_Addenda = self.add_node(
                    'cfdi:Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
            else:
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
        return xml_res_str