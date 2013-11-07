# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
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

import xml.dom.minidom
import xml.etree.cElementTree as ET
import os
from add_node import add_node

data_path = '../data'
source_path = '../source'
file_source = 'l10n_mx_cities.xml'

source_full_path = os.path.join(source_path, file_source)

parser_states_codes = {
    '01': 'ags', '02': 'bc', '03': 'bcs', '04': 'camp', '05': 'coah',
    '06': 'col', '07': 'chis', '08': 'chih', '09': 'df', '10': 'dgo',
    '11': 'gto', '12': 'gro', '13': 'hgo', '14': 'jal', '15': 'mex',
    '16': 'mich', '17': 'mor', '18': 'nay', '19': 'nl', '20': 'oax',
    '21': 'pue', '22': 'qro', '23': 'qr', '24': 'slp', '25': 'sin',
    '26': 'son', '27': 'tab', '28': 'tamps', '29': 'talx', '30': 'ver',
    '31': 'yuc', '32': 'zac'}

tree = ET.ElementTree(file=source_full_path)
root = tree.getroot()

cities = []
xml_doc = xml.dom.minidom.Document()
openerp_node = xml_doc.createElement('openerp')
xml_doc.appendChild(openerp_node)
nodeopenerp = xml_doc.getElementsByTagName('openerp')[0]
main_node = add_node('data', {"noupdate": "True"}, nodeopenerp,
                    xml_doc, attrs_types={"noupdate": "attribute"})

for elem in root[1:]:
    for a in elem:
        if a.tag == '{NewDataSet}c_mnpio':
            city_code = a.text and a.text or ''
        if a.tag == '{NewDataSet}D_mnpio':
            city = a.text and a.text or ''
        if a.tag == '{NewDataSet}d_estado':
            state = a.text and a.text or ''
        if a.tag == '{NewDataSet}c_estado':
            state_code = a.text and a.text or ''
    city_state = city_code+state_code
    if city_state not in cities:
        cities.append(city_state)
        city_id = 'res_country_state_city_mx_'+state_code+'_'+city_code
        node_record = add_node('record', {"id": city_id,
                                "model": "res.country.state.city"}, main_node,
                                xml_doc, attrs_types={"id": "attribute",
                                "model": "attribute"})
        main_node.appendChild(node_record)
        node_record_attrs = {
            "name": "country_id",
            "ref": "base.mx",
        }
        node_record_attrs_types = {
            "name": 'attribute',
            "ref": 'attribute',
        }
        order = ['name', 'ref', ]

        node_field = add_node('field', node_record_attrs, node_record, xml_doc,
                            node_record_attrs_types, order)
        node_record.appendChild(node_field)

        node_city_attrs = {"name": city, }
        node_city_attrs_types = {"name": 'att_text', }
        order = ['name']
        node_field_city = add_node('field', node_city_attrs, node_record,
                            xml_doc, node_city_attrs_types, order)
        node_record.appendChild(node_field_city)

        node_city_code_attrs = {"code": city_code, }
        node_city_code_attrs_types = {"code": 'att_text', }
        order = ['code']
        node_field_city_code = add_node('field', node_city_code_attrs,
                    node_record, xml_doc, node_city_code_attrs_types, order)
        node_record.appendChild(node_field_city_code)

        xml_id_states = 'l10n_mx_states.res_country_state_mx_' + \
            parser_states_codes.get(state_code, '')
        node_states_attrs = {"name": 'state_id', 'ref': xml_id_states}
        node_states_attrs_types = {"name": 'attribute', "ref": "attribute", }
        order = ['name', 'ref']
        node_field_states = add_node('field', node_states_attrs, node_record,
                                    xml_doc, node_states_attrs_types, order)
        node_record.appendChild(node_field_states)

data_full_path = os.path.join(data_path, 'l10n_mx_cities.xml')

f = open(data_full_path, 'wb')
f.write(xml_doc.toxml('UTF-8'))
f.close
