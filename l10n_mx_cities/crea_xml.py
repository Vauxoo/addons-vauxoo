import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom
#~ tree.write(sys.stdout)

#~ a = ET.Element('elem')
#~ c = ET.SubElement(a, 'child1')
#~ c.text = "some text"
#~ d = ET.SubElement(a, 'child2')
#~ b = ET.Element('elem_b')
#~ root = ET.Element('root')
#~ root.extend((a, b))
#~ tree = ET.ElementTree(root)
#~ tree.write(sys.stdout)

def add_node(node_name, attrs, parent_node, minidom_xml_obj, attrs_types,order=False):
        if not order:
            order=attrs
        new_node = minidom_xml_obj.createElement(node_name)
        for key in order:
            if attrs_types[key] == 'attribute':
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement( key )
                text_node = minidom_xml_obj.createTextNode( attrs[key] )
                
                key_node.appendChild( text_node )
                new_node.appendChild( key_node )
            elif attrs_types[key] == 'att_text':
                new_node.setAttribute(key, 'name')
                text_node = minidom_xml_obj.createTextNode( attrs[key] )
                
                #~ key_node.appendChild( text_node )
                new_node.appendChild( text_node )
                
        parent_node.appendChild( new_node )
        #~ print 'new_node',new_node
        return new_node

#~ xml_inv=base64.decodestring( '/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/l10n_mx_cities/data/prueba_tree.xml' )
#~ xml_2=xml_inv.replace(codecs.BOM_UTF8,'').replace('\n', '').replace('\r', '').replace('\r\n', '')

doc2 = xml.dom.minidom.Document()
openerp_node = doc2.createElement( 'openerp' )
doc2.appendChild( openerp_node )
print 'doc2',doc2
print 'doc2 to xml',doc2.toxml('UTF-8')
nodeComprobante2 = doc2.getElementsByTagName('openerp')[0]
#~ print 'nodeComprobante2',nodeComprobante2
nodeAddenda = add_node('data', {"noupdate":"True"}, nodeComprobante2, doc2, attrs_types={"noupdate":"attribute"})

nodeDSCargaRemisionProv = add_node('record', {"id":"base.mx", "model":"res.country"}, nodeAddenda, doc2, attrs_types={"id":"attribute","model":"attribute"})
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
                
nodeRemision_attrs = {
    "name": "agruas",
    #~ "name2": "aguas",
}
nodeRemision_attrs_types = {
    "name": 'att_text',
    #~ "name2": 'textNode',
}
order = ['name' ]

nodeRemision = add_node('field', nodeRemision_attrs, nodeDSCargaRemisionProv, doc2, nodeRemision_attrs_types,order)
nodeDSCargaRemisionProv.appendChild( nodeRemision )




print 'doc2 to xml',doc2.toxml('UTF-8')
