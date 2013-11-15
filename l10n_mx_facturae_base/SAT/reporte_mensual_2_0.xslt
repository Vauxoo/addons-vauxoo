<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:cfd="http://www.sat.gob.mx/cfd/2" xmlns:ecc="http://www.sat.gob.mx/ecc" xmlns:psgecfd="http://www.sat.gob.mx/psgecfd" xmlns:divisas="http://www.sat.gob.mx/divisas" xmlns:detallista="http://www.sat.gob.mx/detallista" xmlns:ecb="http://www.sat.gob.mx/ecb" xmlns:implocal="http://www.sat.gob.mx/implocal" xmlns:terceros="http://www.sat.gob.mx/terceros">
  <!-- Con el siguiente método se establece que la salida deberá ser en texto -->
  <!-- <xsl:output method="text" version="1.0" encoding="UTF-8" indent="no"/> -->
  <xsl:output method="text" version="1.0" encoding="UTF-8" indent="no" />
  <!--
		En esta sección se define la inclusión de las plantillas de utilería
	-->
  <xsl:include href="utilerias.xslt" />
  <!-- 
		En esta sección se define la inclusión de las demás plantillas de transformación para 
		la generación de las cadenas originales de los complementos fiscales 
	-->
  <!--xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/ecc/ecc.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/psgecfd/psgecfd.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/donat/donat.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/divisas/divisas.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/ecb/ecb.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/implocal/implocal.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/terceros/terceros.xslt"/-->
  <!-- Aquí iniciamos el procesamiento para el reporte mensual con su | inicial y el terminador | -->
  <xsl:template match="/"><xsl:apply-templates select="/cfd:Comprobante" />|</xsl:template>
  <!--  Aquí iniciamos el procesamiento de los datos incluidos en el comprobante -->
  <xsl:template match="cfd:Comprobante">
    <!-- Iniciamos la formacion del cfd para el resumen mensual-->
    <xsl:apply-templates select="./cfd:Receptor" />
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@serie" />
    </xsl:call-template>
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@folio" />
    </xsl:call-template>
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@noAprobacion" />
    </xsl:call-template>
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="translate(string(./@fecha),'T',' ')" />
    </xsl:call-template>
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@total" />
    </xsl:call-template>
    <xsl:apply-templates select="./cfd:Impuestos" />
    <xsl:call-template name="edoComprobante" />
    <xsl:call-template name="efectoComprobante">
      <xsl:with-param name="valor" select="./@tipoDeComprobante" />
    </xsl:call-template>
    <xsl:choose>
      <xsl:when test="./cfd:Complemento">
        <xsl:apply-templates select="./cfd:Complemento" />
      </xsl:when>
      <xsl:otherwise>|||</xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- Manejador de nodos tipo Receptor-->
  <xsl:template match="cfd:Receptor">
    <!-- Iniciamos el tratamiento de los atributos del Receptor-->
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@rfc" />
    </xsl:call-template>
  </xsl:template>
  <!-- Manejador de nodos tipo Impuestos -->
  <xsl:template match="cfd:Impuestos">
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@totalImpuestosTrasladados" />
    </xsl:call-template>
  </xsl:template>
  <!-- Manejador de nodos tipo Complemento -->
  <xsl:template match="cfd:Complemento">
    <xsl:for-each select="./*">
      <xsl:if test="'.' = 'InformacionAduanera'">
        <xsl:apply-templates select="." />
      </xsl:if>
    </xsl:for-each>
  </xsl:template>
  <!-- Manejador de nodos tipo Información Aduanera -->
  <xsl:template match="cfd:InformacionAduanera">
    <!-- Manejo de los atributos de la información aduanera -->
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@numero" />
    </xsl:call-template>
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@fecha" />
    </xsl:call-template>
    <xsl:call-template name="Requerido">
      <xsl:with-param name="valor" select="./@aduana" />
    </xsl:call-template>
  </xsl:template>
  <!--Manejador del efecto de Comprobante-->
  <xsl:template name="efectoComprobante">
    <!-- Manejo del efecto de Comprobante -->
    <xsl:param name="valor"/><xsl:if test="$valor = 'ingreso'">|I</xsl:if><xsl:if test="$valor = 'egreso'">|E</xsl:if><xsl:if test="$valor = 'traslado'">|T</xsl:if>
  </xsl:template>
  <!--Manejador del tipo de Comprobante-->
  <xsl:template name="edoComprobante">|1</xsl:template>
</xsl:stylesheet>