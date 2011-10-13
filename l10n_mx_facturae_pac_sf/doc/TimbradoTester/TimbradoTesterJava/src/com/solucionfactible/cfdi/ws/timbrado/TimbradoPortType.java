/**
 * TimbradoPortType.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package com.solucionfactible.cfdi.ws.timbrado;

public interface TimbradoPortType extends java.rmi.Remote {
    public com.solucionfactible.cfdi.ws.timbrado.xsd.CFDICancelacion cancelar(java.lang.String usuario, java.lang.String password, java.lang.String[] uuids, byte[] derCertCSD, byte[] derKeyCSD, java.lang.String contrasenaCSD) throws java.rmi.RemoteException;
    public com.solucionfactible.cfdi.ws.timbrado.xsd.CFDICertificacion timbrarBase64(java.lang.String usuario, java.lang.String password, java.lang.String cfdiBase64, java.lang.Boolean zip) throws java.rmi.RemoteException;
    public com.solucionfactible.cfdi.ws.timbrado.xsd.CFDICertificacion timbrar(java.lang.String usuario, java.lang.String password, byte[] cfdi, java.lang.Boolean zip) throws java.rmi.RemoteException;
    public com.solucionfactible.cfdi.ws.timbrado.xsd.CFDICancelacion cancelarBase64(java.lang.String usuario, java.lang.String password, java.lang.String[] uuids, java.lang.String derCertCSDBase64, java.lang.String derKeyCSDBase64, java.lang.String contrasenaCSD) throws java.rmi.RemoteException;
}
