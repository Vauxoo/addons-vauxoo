import xml.dom.minidom
import xml.etree.cElementTree as ET
import os
from add_node import add_node

data_path = '../data'
source_path = '../source'
file_source = 'l10n_mx_cities.xml'

source_full_path = os.path.join(source_path, file_source)

parser_states_codes={'01':'ags', '02':'bc','03':'bcs','04':'camp','05':'coah','06':'col' ,'07':'chis','08':'chih','09':'df','10':'dgo','11':'gto',
'12':'gro','13':'hgo','14':'jal','15':'mex','16':'mich','17':'mor','18':'nay','19':'nl','20':'oax','21':'pue','22':'qro','23':'qr','24':'slp',
'25':'sin','26':'son','27':'tab','28':'tamps','29':'talx','30':'ver','31':'yuc','32':'zac'}


#~ tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/Guanajuato.xml')
#~ tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/CPdescarga.xml')
tree = ET.ElementTree(file=source_full_path)

root = tree.getroot()

city = []
doc2 = xml.dom.minidom.Document()
openerp_node = doc2.createElement( 'openerp' )
doc2.appendChild( openerp_node )
nodeComprobante2 = doc2.getElementsByTagName('openerp')[0]
nodeAddenda = add_node('data', {"noupdate":"True"}, nodeComprobante2, doc2, attrs_types={"noupdate":"attribute"})


for elem in root[1:]: 
    #~ print 'el element sin text',elem[11],'con tag',elem[11].tag,'con text',elem[11].text
    for a in elem:
        if a.tag == '{NewDataSet}c_mnpio':
            city_code = a.text and a.text or ''
        if a.tag == '{NewDataSet}D_mnpio':
            ciudad = a.text and a.text or ''
        if a.tag == '{NewDataSet}d_estado':
            state = a.text and a.text or ''
        if a.tag == '{NewDataSet}c_estado':
            state_code = a.text and a.text or ''
    
    if ciudad not in city:
        city.append(ciudad)
        city_id = 'res_country_state_city_mx_'+state_code+'_'+city_code
        nodeDSCargaRemisionProv = add_node('record', {"id":city_id, "model":"res.country.state.city"}, nodeAddenda, doc2, attrs_types={"id":"attribute","model":"attribute"})
        nodeAddenda.appendChild(nodeDSCargaRemisionProv )
        nodeRemision_attrs = {
            "name": "country_id",
            "ref": "base.mx",
        }
        nodeRemision_attrs_types = {
            "name": 'attribute',
            "ref": 'attribute',
        }
        order = ['name', 'ref', ]

        nodeRemision = add_node('field', nodeRemision_attrs, nodeDSCargaRemisionProv, doc2, nodeRemision_attrs_types,order)
        nodeDSCargaRemisionProv.appendChild( nodeRemision )
                        
        nodeRemision_attrs = { "name": ciudad,}
        nodeRemision_attrs_types = { "name": 'att_text',}
        order = ['name' ]
        nodeRemision = add_node('field', nodeRemision_attrs, nodeDSCargaRemisionProv, doc2, nodeRemision_attrs_types,order)
        nodeDSCargaRemisionProv.appendChild( nodeRemision )

        nodeRemision_attrs = { "code": city_code,}
        nodeRemision_attrs_types = { "code": 'att_text',}
        order = ['code' ]
        nodeRemision = add_node('field', nodeRemision_attrs, nodeDSCargaRemisionProv, doc2, nodeRemision_attrs_types,order)
        nodeDSCargaRemisionProv.appendChild( nodeRemision )
                
                
        xml_id_states = 'l10n_mx_states.res_country_state_mx_'+parser_states_codes.get(state_code,'')
        nodeRemision_attrs = { "name": 'state_id','ref': xml_id_states}
        nodeRemision_attrs_types = { "name": 'attribute', "ref": "attribute",}
        order = ['name','ref' ]
        nodeRemision = add_node('field', nodeRemision_attrs, nodeDSCargaRemisionProv, doc2, nodeRemision_attrs_types,order)
        nodeDSCargaRemisionProv.appendChild( nodeRemision )


print 'doc2 to xml',doc2.toxml('UTF-8')
print 'xml generado con exito'
data_full_path = os.path.join(data_path, 'l10n_mx_cities.xml')

f = open( data_full_path, 'wb' )
f.write(doc2.toxml('UTF-8'))
f.close
