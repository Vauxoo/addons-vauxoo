#!/usr/bin/python

from suds.client import Client
import logging
import base64

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

# Username and Password, assigned by FINKOK
username = 'username@demo.com'
password = '12345678a'

# Read the xml file and encode it on base64
invoice_path = "invoice.xml"
file = open(invoice_path)
lines = "".join(file.readlines())
xml = base64.encodestring(lines)

# Consuming the stamp service
url = "http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl"
client = Client(url,cache=None)
client.service.stamp(xml,username,password)

# Consuming the cancel service
# Read the x509 certificate file on PEM format and encode it on base64
cer_path = "cer.pem" 
cer_file = open(cer_path).read().encode('base64')

# Read the Encrypted Private Key file on PEM format and encode it on base64
key_path = "key.pem" 
key_file = open(key_path).read().encode('base64')

taxpayer_id = 'CSO050217EA1' # The RFC of the Emisor
invoices = ["6308DF45-0D7F-4060-9121-6C8639FE1C14"] # A list of UUIDs

# The next lines are needed by the python suds library
invoices_list = client.factory.create("UUIDS")
invoices_list.uuids.string = invoices

url = "http://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl"
client = Client(url,cache=None)
result = client.service.cancel(invoices_list, username, password, taxpayer_id, cer_file, key_file)
