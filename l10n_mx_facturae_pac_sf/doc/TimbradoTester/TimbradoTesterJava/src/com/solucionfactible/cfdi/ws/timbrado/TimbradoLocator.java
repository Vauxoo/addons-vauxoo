/**
 * TimbradoLocator.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package com.solucionfactible.cfdi.ws.timbrado;

public class TimbradoLocator extends org.apache.axis.client.Service implements com.solucionfactible.cfdi.ws.timbrado.Timbrado {

    public TimbradoLocator() {
    }


    public TimbradoLocator(org.apache.axis.EngineConfiguration config) {
        super(config);
    }

    public TimbradoLocator(java.lang.String wsdlLoc, javax.xml.namespace.QName sName) throws javax.xml.rpc.ServiceException {
        super(wsdlLoc, sName);
    }

    // Use to get a proxy class for TimbradoHttpSoap11Endpoint
    private java.lang.String TimbradoHttpSoap11Endpoint_address = "http://testing.solucionfactible.com:8080/ws/services/Timbrado.TimbradoHttpSoap11Endpoint/";

    public java.lang.String getTimbradoHttpSoap11EndpointAddress() {
        return TimbradoHttpSoap11Endpoint_address;
    }

    // The WSDD service name defaults to the port name.
    private java.lang.String TimbradoHttpSoap11EndpointWSDDServiceName = "TimbradoHttpSoap11Endpoint";

    public java.lang.String getTimbradoHttpSoap11EndpointWSDDServiceName() {
        return TimbradoHttpSoap11EndpointWSDDServiceName;
    }

    public void setTimbradoHttpSoap11EndpointWSDDServiceName(java.lang.String name) {
        TimbradoHttpSoap11EndpointWSDDServiceName = name;
    }

    public com.solucionfactible.cfdi.ws.timbrado.TimbradoPortType getTimbradoHttpSoap11Endpoint() throws javax.xml.rpc.ServiceException {
       java.net.URL endpoint;
        try {
            endpoint = new java.net.URL(TimbradoHttpSoap11Endpoint_address);
        }
        catch (java.net.MalformedURLException e) {
            throw new javax.xml.rpc.ServiceException(e);
        }
        return getTimbradoHttpSoap11Endpoint(endpoint);
    }

    public com.solucionfactible.cfdi.ws.timbrado.TimbradoPortType getTimbradoHttpSoap11Endpoint(java.net.URL portAddress) throws javax.xml.rpc.ServiceException {
        try {
            com.solucionfactible.cfdi.ws.timbrado.TimbradoSoap11BindingStub _stub = new com.solucionfactible.cfdi.ws.timbrado.TimbradoSoap11BindingStub(portAddress, this);
            _stub.setPortName(getTimbradoHttpSoap11EndpointWSDDServiceName());
            return _stub;
        }
        catch (org.apache.axis.AxisFault e) {
            return null;
        }
    }

    public void setTimbradoHttpSoap11EndpointEndpointAddress(java.lang.String address) {
        TimbradoHttpSoap11Endpoint_address = address;
    }

    /**
     * For the given interface, get the stub implementation.
     * If this service has no port for the given interface,
     * then ServiceException is thrown.
     */
    public java.rmi.Remote getPort(Class serviceEndpointInterface) throws javax.xml.rpc.ServiceException {
        try {
            if (com.solucionfactible.cfdi.ws.timbrado.TimbradoPortType.class.isAssignableFrom(serviceEndpointInterface)) {
                com.solucionfactible.cfdi.ws.timbrado.TimbradoSoap11BindingStub _stub = new com.solucionfactible.cfdi.ws.timbrado.TimbradoSoap11BindingStub(new java.net.URL(TimbradoHttpSoap11Endpoint_address), this);
                _stub.setPortName(getTimbradoHttpSoap11EndpointWSDDServiceName());
                return _stub;
            }
        }
        catch (java.lang.Throwable t) {
            throw new javax.xml.rpc.ServiceException(t);
        }
        throw new javax.xml.rpc.ServiceException("There is no stub implementation for the interface:  " + (serviceEndpointInterface == null ? "null" : serviceEndpointInterface.getName()));
    }

    /**
     * For the given interface, get the stub implementation.
     * If this service has no port for the given interface,
     * then ServiceException is thrown.
     */
    public java.rmi.Remote getPort(javax.xml.namespace.QName portName, Class serviceEndpointInterface) throws javax.xml.rpc.ServiceException {
        if (portName == null) {
            return getPort(serviceEndpointInterface);
        }
        java.lang.String inputPortName = portName.getLocalPart();
        if ("TimbradoHttpSoap11Endpoint".equals(inputPortName)) {
            return getTimbradoHttpSoap11Endpoint();
        }
        else  {
            java.rmi.Remote _stub = getPort(serviceEndpointInterface);
            ((org.apache.axis.client.Stub) _stub).setPortName(portName);
            return _stub;
        }
    }

    public javax.xml.namespace.QName getServiceName() {
        return new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com", "Timbrado");
    }

    private java.util.HashSet ports = null;

    public java.util.Iterator getPorts() {
        if (ports == null) {
            ports = new java.util.HashSet();
            ports.add(new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com", "TimbradoHttpSoap11Endpoint"));
        }
        return ports.iterator();
    }

    /**
    * Set the endpoint address for the specified port name.
    */
    public void setEndpointAddress(java.lang.String portName, java.lang.String address) throws javax.xml.rpc.ServiceException {
        
if ("TimbradoHttpSoap11Endpoint".equals(portName)) {
            setTimbradoHttpSoap11EndpointEndpointAddress(address);
        }
        else 
{ // Unknown Port Name
            throw new javax.xml.rpc.ServiceException(" Cannot set Endpoint Address for Unknown Port" + portName);
        }
    }

    /**
    * Set the endpoint address for the specified port name.
    */
    public void setEndpointAddress(javax.xml.namespace.QName portName, java.lang.String address) throws javax.xml.rpc.ServiceException {
        setEndpointAddress(portName.getLocalPart(), address);
    }

}
