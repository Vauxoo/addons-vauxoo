import xml.dom.minidom
import xml.etree.cElementTree as ET
#~ tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/prueba_tree.xml')
#~ tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/Guanajuato.xml')
tree = ET.ElementTree(file='/home/yzaack/instancias/7/addons_all/addons-mx-7-dev-julio-data-city/wizard_xml_invoice/wizard/data/CPdescarga.xml')

print '--------tree.getroot()',tree.getroot()
root = tree.getroot()
print 'root.tag, root.attrib',root.tag, root.attrib

#sin subhijos
#~ for child_of_root in root:
    #~ print child_of_root.tag, child_of_root.attrib
print 'antes del for'
#directo a 

#~ print 'root[1][3]',a.tag,'a.attrib',a.attrib,'a.text',a.text
#~ for elem in tree.iterfind('table/D_mnpio'):
#~ for elem in tree.iterfind('branch/sub-branch'):
#    print 'dentro del for'
 #   print elem.tag, elem.attrib, elem.text
city = []
for elem in root[1:]:
    ciudad = elem[3].text and elem[3].text or ''
    if ciudad not in city:
        print 'element',elem[3].text
        city.append(ciudad)
        print 'despues de insertar en lista'
        
print 'listado de ciudades',city
