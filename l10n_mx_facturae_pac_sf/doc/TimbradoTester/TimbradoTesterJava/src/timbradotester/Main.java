/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package timbradotester;

import com.solucionfactible.cfdi.ws.timbrado.TimbradoLocator;
import com.solucionfactible.cfdi.ws.timbrado.TimbradoPortType;
import com.solucionfactible.cfdi.ws.timbrado.xsd.CFDICertificacion;
import com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCertificacion;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.Locale;

/**
 *
 * @author horacio
 */
public class Main {

    private static String user = "testing@solucionfactible.com";
    private static String password = "timbrado.SF.16672";

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        String fPath = null;
        if (args.length == 0) {
            System.err.println();
            String msg = "CFDI o ZIP de CFDI's a timbrar: ";
            System.err.print(msg);
            Reader input = new InputStreamReader(System.in);
            BufferedReader r = new BufferedReader(input);
            while ((fPath = r.readLine()).trim().length() == 0) {
                System.err.print(msg);
            }
            
        } else {
            fPath = args[0];
        }
        File f = new File(fPath);
        if (!f.isFile() || !f.exists()) {
            System.err.println("No se encuentra el archivo " + fPath + " o no es un archivo regular.");
            return;
        }
        FileInputStream fis = new FileInputStream(f);
        byte[] cfdi = new byte[fis.available()];
        fis.read(cfdi);
        fis.close();
        TimbradoLocator l = new TimbradoLocator();
        TimbradoPortType s = l.getTimbradoHttpSoap11Endpoint();

        CFDICertificacion cert = s.timbrar(user, password, cfdi, Boolean.valueOf(f.getAbsolutePath().endsWith(".zip")));
        System.out.println("Status:  " + cert.getStatus());
        System.out.println("Mensaje: " + cert.getMensaje());
        CFDIResultadoCertificacion[] resultados = cert.getResultados();
        Locale esMX = new Locale("es", "MX");
        if (resultados != null) {
            for (CFDIResultadoCertificacion r : resultados) {
                System.out.println(String.format("[%d] %s", r.getStatus(), r.getMensaje()));
                if (r.getUuid() != null) {
                    System.out.println(String.format("CFDI timbrado con folio: %s", r.getUuid()));
                    System.out.println(String.format("Certificado SAT: %s", r.getSelloSAT()));
                    System.out.println(String.format(esMX, "Fecha de certificación: %1$te de %1$tB de %1$tY", r.getFechaTimbrado()));
                    System.out.println("Cadena original del Timbre Fiscal digital: " + r.getCadenaOriginal());
                    
                    System.out.println("XML de CFDI con Timbre Fiscal Digital:");
                    System.out.println(new String(r.getCfdiTimbrado()));
                }
                System.out.println();
            }
        }
    }
}
