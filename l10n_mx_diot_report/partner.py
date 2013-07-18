# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from operator import itemgetter

from osv import fields, osv

class res_partner(osv.osv):

    _inherit = 'res.partner'
    _description = 'Partner'

    _columns = {
        'type_of_third':fields.selection([
            ('04', ' 04 - National Supplier'),
            ('05', ' 05 - Foreign Supplier'),
            ('15', ' 15 - Global Supplier')],
            'Type of Third (DIOT)', help='Type of third for this partner'),
        'type_of_operation':fields.selection([
            ('03', ' 03 - Provision of Professional Services'),
            ('06', ' 06 - Renting of buildings'),
            ('85', ' 85 - Others')],
            'Type of Operation (DIOT)', help='Type of operation realiced for'\
            ' this partner'),
        'diot_country':fields.selection([
            ('AR', 'AR - Argentina'),
            ('AT', 'AT - Austria'),
            ('AU', 'AU - Australia'),
            ('BE', 'BE - Belgica'),
            ('BC', 'BC - Belice'),
            ('BO', 'BO - Bolivia'),
            ('BR', 'BR - Brasil'),
            ('CA', 'CA - Canada'),
            ('CL', 'CL - Chile'),
            ('CM', 'CM - Camerun'),
            ('CN', 'CN - China'),
            ('CO', 'CO - Colombia'),
            ('CR', 'CR - Republica de Costa Rica'),
            ('CU', 'CU - Cuba'),
            ('DM', 'DM - Republica Dominicana'),
            ('DZ', 'DZ - Argelia'),
            ('EC', 'EC - Ecuador'),
            ('EG', 'EG - Egipto'),
            ('EH', 'EH - Sahara del Oeste'),
            ('EO', 'EO - Estado Independiente de Samoa Occidental'),
            ('ES', 'ES - España'),
            ('ET', 'ET - Etiopia'),
            ('GR', 'GR - Grecia'),
            ('GT', 'GT - Guatemala'),
            ('GU', 'GU - Guam'),
            ('GW', 'GW - Guinea Bissau'),
            ('GY', 'GY - Republica de Guyana'),
            ('GZ', 'GZ - Islas de Guernesey, Jersey, Alderney, '\
                'Isla Great Sark, Herm, Little Sark, Berchou, Jethou, '\
                'Lihou (Islas del Canal)'),
            ('HK', 'HK - Hong Kong'),
            ('HM', 'HM - Islas Heard and Mc Donald'),
            ('HN', 'HN - República de Honduras'),
            ('HT', 'HT - Haiti'),
            ('HU', 'HU - Hungaria'),
            ('ID', 'ID - Indonesia'),
            ('IE', 'IE - Irlanda'),
            ('IH', 'IH - Isla del Hombre'),
            ('IL', 'IL - Israel'),
            ('IN', 'IN - India'),
            ('IO', 'IO - Territorio Británico en el Océano Indico'),
            ('IP', 'IP - Islas Pacifico'),
            ('IQ', 'IQ - Iraq'),
            ('IR', 'IR - Iran'),
            ('IS', 'IS - Islandia'),
            ('IT', 'IT - Italia'),
            ('JM', 'JM - Jamaica'),
            ('JO', 'JO - Reino Hachemita de Jordania'),
            ('JP', 'JP - Japon'),
            ('KE', 'KE - Kenia'),
            ('KH', 'KH - Campuchea Democratica'),
            ('KI', 'KI - Kiribati'),
            ('KM', 'KM - Comoros'),
            ('KN', 'KN - San Kitts'),
            ('KP', 'KP - Republica Democratica de Corea'),
            ('KR', 'KR - Republica de Corea'),
            ('KW', 'KW - Estado de Kuwait'),
            ('KY', 'KY - Islas Caiman'),
            ('LA', 'LA - Republica Democratica de Laos'),
            ('LB', 'LB - Libano'),
            ('NL', 'NL - Holanda'),
            ('NO', 'NO - Noruega'),
            ('NP', 'NP - Nepal'),
            ('NR', 'NR - Republica de Nauru'),
            ('NT', 'NT - Zona Neutral'),
            ('NU', 'NU - Niue'),
            ('NV', 'NV - Nevis'),
            ('NZ', 'NZ - Nueva Zelanda'),
            ('OM', 'OM - Sultanía de Omán'),
            ('PA', 'PA - República de Panamá'),
            ('PE', 'PE - Peru'),
            ('PY', 'PY - Paraguay'),
            ('SV', 'SV - El Salvador'),
            ('UA', 'UA - Ucrania'),
            ('UG', 'UG - Uganda'),
            ('UM', 'UM - Islas Menores alejadas de Estados Unidos'),
            ('US', 'US - Estados Unidos de América'),
            ('UY', ' UY- Republica Oriental del Uruguay'),
            ('VA', 'VA - Vaticano'),
            ('VE', 'VE - Venezuela'),
            ('XX', 'XX - Otro'),
            ('YD', 'YD - Yemen Democratica'),
            ('YE', 'YE - Republica del Yemen'),
            ('YU', 'YU - Paises de las EX- Yugoslavia'),
            ('ZA', 'ZA - Sudafrica'),
            ('ZC', 'ZC - Zona Especial Canaria'),
            ('ZM', 'ZM - Zambia'),
            ('ZO', 'ZO - Zona Libre de Ostrava'),
            ('ZR', 'ZR - Zaire'),
            ('ZW', 'ZW - Zimbawe'),
            ], 'Country  (DIOT)', help='Country used to DIOT'),
    'number_fiscal_id_diot' : fields.char('Number Fiscal ID (DIOT)', size=100),
    'nacionality_diot' : fields.char('Nacionality (DIOT)', size=100),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
