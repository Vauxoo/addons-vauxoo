<?php

# Username and Password, assigned by FINKOK
$username = 'username@demo.com';
$password = '12345678a';

# Read the xml file and encode it on base64
$invoice_path = "invoice.xml";
$xml_file = fopen($invoice_path, "rb");
$xml_content = fread($xml_file, filesize($invoice_path));
fclose($xml_file);

# In newer PHP versions the SoapLib class automatically converts FILE parameters to base64, so the next line is not needed, otherwise uncomment it
#$xml_content = base64_encode($xml_content);

# Consuming the stamp service
$url = "http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl";
$client = new SoapClient($url);

$params = array(
  "xml" => $xml_content,
  "username" => $username,
  "password" => $password
);
$response = $client->__soapCall("stamp", array($params));
print_r($response);

# Consuming the cancel service
# Read the x509 certificate file on PEM format and encode it on base64
$cer_path = "cer.pem"; 
$cer_file = fopen($cer_path, "r");
$cer_content = fread($cer_file, filesize($cer_path));
fclose($cer_file);
# In newer PHP versions the SoapLib class automatically converts FILE parameters to base64, so the next line is not needed, otherwise uncomment it
#$cer_content = base64_encode($cer_content);

# Read the Encrypted Private Key (des3) file on PEM format and encode it on base64
$key_path = "key.pem";
$key_file = fopen($key_path, "r");
$key_content = fread($key_file,filesize($key_path));
fclose($key_file);
# In newer PHP versions the SoapLib class automatically converts FILE parameters to base64, so the next line is not needed, otherwise uncomment it
#$key_content = base64_encode($key_content);

$taxpayer_id = 'CSO050217EA1'; # The RFC of the Emisor
$invoices = array("6308DF45-0D7F-4060-9121-6C8639FE1C14"); # A list of UUIDs

$url = "http://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl";
$client = new SoapClient($url);
$params = array(  
  "UUIDS" => array('uuids' => $invoices),
  "username" => $username,
  "password" => $password,
  "taxpayer_id" => $taxpayer_id,
  "cer" => $cer_content,
  "key" => $key_content
);
$response = $client->__soapCall("cancel", array($params));
print_r($response);
?>
