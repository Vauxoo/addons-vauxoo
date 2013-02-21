import xml.dom.minidom
import xml.etree.cElementTree as ET
import os
from crea_xml import add_node

path = 'xml'

#~ tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/prueba_tree.xml')
#~ tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/Guanajuato.xml')
tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/CPdescarga.xml')


print '--------tree.getroot()',tree.getroot()
root = tree.getroot()
print 'root.tag, root.attrib',root.tag, root.attrib

#sin subhijos
#~ for child_of_root in root:
    #~ print child_of_root.tag, child_of_root.attrib
#~ print 'antes del for'
#directo a 
#~ print 'root[1][3]',a.tag,'a.attrib',a.attrib,'a.text',a.text
#~ for elem in tree2.iterfind('NewDataSet'):
#~ for elem in tree.iterfind('branch/sub-branch'):
    #~ print 'dentro del for'
    #~ print 'isbn:', book.attrib['isbn']
    #~ print elem.tag, elem.attrib, elem.text
city = []
print '-------------------------'
doc2 = xml.dom.minidom.Document()
openerp_node = doc2.createElement( 'openerp' )
doc2.appendChild( openerp_node )
print 'doc2',doc2
print 'doc2 to xml',doc2.toxml('UTF-8')
nodeComprobante2 = doc2.getElementsByTagName('openerp')[0]
#~ print 'nodeComprobante2',nodeComprobante2
nodeAddenda = add_node('data', {"noupdate":"True"}, nodeComprobante2, doc2, attrs_types={"noupdate":"attribute"})

for elem in root[1:]: 
    print 'el element sin text',elem[11],'con tag',elem[11].tag,'con text',elem[11].text
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
        #~ print 'element',elem[3].text
        city.append(ciudad)
        #~ print 'despues de insertar en lista'
        
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
        
        nodeRemision_attrs = { "state_id": state,}
        nodeRemision_attrs_types = { "state_id": 'att_text',}
        order = ['state_id' ]
        nodeRemision = add_node('field', nodeRemision_attrs, nodeDSCargaRemisionProv, doc2, nodeRemision_attrs_types,order)
        nodeDSCargaRemisionProv.appendChild( nodeRemision )

        
        
        
        
        
        
        
        
        
        
        
print 'doc2 to xml',doc2.toxml('UTF-8')
full_path = os.path.join(path, 'l10n_mx_cities.xml')

f = open( full_path, 'wb' )
f.write(doc2.toxml('UTF-8'))
f.close
