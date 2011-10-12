<?
	$fname = "/home/horacio/Downloads/ingreso_MARG510123BV4_C0BDABAC-D923-447C-8B16-306F823BFC39_20110128_171752.xml";
	$handle = fopen($fname, "r");
	$sData = '';
	$usuario = "testing@solucionfactible.com";
	$password = "timbrado.SF.16672";

        while(!feof($handle))
            $sData .= fread($handle, filesize($fname));
        fclose($handle);
	$b64 = base64_encode($sData);

	$response = '';
	try {
	    	$client = new SoapClient("http://testing.solucionfactible.com/ws/services/Timbrado?wsdl");
		$params = array('usuario' => $usuario, 'password' => $password, 'cfdiBase64'=>$b64, 'zip'=>False);
		$response = $client->__soapCall('timbrarBase64', array('parameters' => $params));
	} catch (SoapFault $fault) { 
		echo "SOAPFault: ".$fault->faultcode."-".$fault->faultstring."\n";
	}
	$ret = $response->return;
	if($ret->status == 200) {
		print_r($ret->resultados);
	}
?>
