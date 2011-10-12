/**
 * CFDICancelacion.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package com.solucionfactible.cfdi.ws.timbrado.xsd;

public class CFDICancelacion  implements java.io.Serializable {
    private java.lang.String mensaje;

    private com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCancelacion[] resultados;

    private java.lang.Integer status;

    public CFDICancelacion() {
    }

    public CFDICancelacion(
           java.lang.String mensaje,
           com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCancelacion[] resultados,
           java.lang.Integer status) {
           this.mensaje = mensaje;
           this.resultados = resultados;
           this.status = status;
    }


    /**
     * Gets the mensaje value for this CFDICancelacion.
     * 
     * @return mensaje
     */
    public java.lang.String getMensaje() {
        return mensaje;
    }


    /**
     * Sets the mensaje value for this CFDICancelacion.
     * 
     * @param mensaje
     */
    public void setMensaje(java.lang.String mensaje) {
        this.mensaje = mensaje;
    }


    /**
     * Gets the resultados value for this CFDICancelacion.
     * 
     * @return resultados
     */
    public com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCancelacion[] getResultados() {
        return resultados;
    }


    /**
     * Sets the resultados value for this CFDICancelacion.
     * 
     * @param resultados
     */
    public void setResultados(com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCancelacion[] resultados) {
        this.resultados = resultados;
    }

    public com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCancelacion getResultados(int i) {
        return this.resultados[i];
    }

    public void setResultados(int i, com.solucionfactible.cfdi.ws.timbrado.xsd.CFDIResultadoCancelacion _value) {
        this.resultados[i] = _value;
    }


    /**
     * Gets the status value for this CFDICancelacion.
     * 
     * @return status
     */
    public java.lang.Integer getStatus() {
        return status;
    }


    /**
     * Sets the status value for this CFDICancelacion.
     * 
     * @param status
     */
    public void setStatus(java.lang.Integer status) {
        this.status = status;
    }

    private java.lang.Object __equalsCalc = null;
    public synchronized boolean equals(java.lang.Object obj) {
        if (!(obj instanceof CFDICancelacion)) return false;
        CFDICancelacion other = (CFDICancelacion) obj;
        if (obj == null) return false;
        if (this == obj) return true;
        if (__equalsCalc != null) {
            return (__equalsCalc == obj);
        }
        __equalsCalc = obj;
        boolean _equals;
        _equals = true && 
            ((this.mensaje==null && other.getMensaje()==null) || 
             (this.mensaje!=null &&
              this.mensaje.equals(other.getMensaje()))) &&
            ((this.resultados==null && other.getResultados()==null) || 
             (this.resultados!=null &&
              java.util.Arrays.equals(this.resultados, other.getResultados()))) &&
            ((this.status==null && other.getStatus()==null) || 
             (this.status!=null &&
              this.status.equals(other.getStatus())));
        __equalsCalc = null;
        return _equals;
    }

    private boolean __hashCodeCalc = false;
    public synchronized int hashCode() {
        if (__hashCodeCalc) {
            return 0;
        }
        __hashCodeCalc = true;
        int _hashCode = 1;
        if (getMensaje() != null) {
            _hashCode += getMensaje().hashCode();
        }
        if (getResultados() != null) {
            for (int i=0;
                 i<java.lang.reflect.Array.getLength(getResultados());
                 i++) {
                java.lang.Object obj = java.lang.reflect.Array.get(getResultados(), i);
                if (obj != null &&
                    !obj.getClass().isArray()) {
                    _hashCode += obj.hashCode();
                }
            }
        }
        if (getStatus() != null) {
            _hashCode += getStatus().hashCode();
        }
        __hashCodeCalc = false;
        return _hashCode;
    }

    // Type metadata
    private static org.apache.axis.description.TypeDesc typeDesc =
        new org.apache.axis.description.TypeDesc(CFDICancelacion.class, true);

    static {
        typeDesc.setXmlType(new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com/xsd", "CFDICancelacion"));
        org.apache.axis.description.ElementDesc elemField = new org.apache.axis.description.ElementDesc();
        elemField.setFieldName("mensaje");
        elemField.setXmlName(new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com/xsd", "mensaje"));
        elemField.setXmlType(new javax.xml.namespace.QName("http://www.w3.org/2001/XMLSchema", "string"));
        elemField.setMinOccurs(0);
        elemField.setNillable(true);
        typeDesc.addFieldDesc(elemField);
        elemField = new org.apache.axis.description.ElementDesc();
        elemField.setFieldName("resultados");
        elemField.setXmlName(new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com/xsd", "resultados"));
        elemField.setXmlType(new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com/xsd", "CFDIResultadoCancelacion"));
        elemField.setMinOccurs(0);
        elemField.setNillable(true);
        elemField.setMaxOccursUnbounded(true);
        typeDesc.addFieldDesc(elemField);
        elemField = new org.apache.axis.description.ElementDesc();
        elemField.setFieldName("status");
        elemField.setXmlName(new javax.xml.namespace.QName("http://timbrado.ws.cfdi.solucionfactible.com/xsd", "status"));
        elemField.setXmlType(new javax.xml.namespace.QName("http://www.w3.org/2001/XMLSchema", "int"));
        elemField.setMinOccurs(0);
        elemField.setNillable(false);
        typeDesc.addFieldDesc(elemField);
    }

    /**
     * Return type metadata object
     */
    public static org.apache.axis.description.TypeDesc getTypeDesc() {
        return typeDesc;
    }

    /**
     * Get Custom Serializer
     */
    public static org.apache.axis.encoding.Serializer getSerializer(
           java.lang.String mechType, 
           java.lang.Class _javaType,  
           javax.xml.namespace.QName _xmlType) {
        return 
          new  org.apache.axis.encoding.ser.BeanSerializer(
            _javaType, _xmlType, typeDesc);
    }

    /**
     * Get Custom Deserializer
     */
    public static org.apache.axis.encoding.Deserializer getDeserializer(
           java.lang.String mechType, 
           java.lang.Class _javaType,  
           javax.xml.namespace.QName _xmlType) {
        return 
          new  org.apache.axis.encoding.ser.BeanDeserializer(
            _javaType, _xmlType, typeDesc);
    }

}
