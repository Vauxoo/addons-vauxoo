<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:psgcfdsp="http://www.sat.gob.mx/psgcfdsp">
	<!-- Manejador de nodos tipo psgcfdsp:PrestadoresDeServiciosDeCFDSP -->
	<xsl:template match="psgcfdsp:PrestadoresDeServiciosDeCFDSP">
		<!-- Iniciamos el tratamiento de los atributos de psgcfdsp:PrestadoresDeServiciosDeCFDSP -->
		<xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@version"/></xsl:call-template>		
		<xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@nombre"/></xsl:call-template>
		<xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@rfc"/></xsl:call-template>
		<xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@noCertificado"/></xsl:call-template>
		<xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@fechaPublicacion"/></xsl:call-template>
		<xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@noAutorizacion"/></xsl:call-template>
	</xsl:template>
</xsl:stylesheet>
