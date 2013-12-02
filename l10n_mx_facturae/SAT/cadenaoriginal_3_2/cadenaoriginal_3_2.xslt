<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:ecc="http://www.sat.gob.mx/ecc" xmlns:psgecfd="http://www.sat.gob.mx/psgecfd" xmlns:donat="http://www.sat.gob.mx/donat" xmlns:divisas="http://www.sat.gob.mx/divisas" xmlns:detallista="http://www.sat.gob.mx/detallista" xmlns:ecb="http://www.sat.gob.mx/ecb" xmlns:implocal="http://www.sat.gob.mx/implocal" xmlns:terceros="http://www.sat.gob.mx/terceros" xmlns:iedu="http://www.sat.gob.mx/iedu" xmlns:ventavehiculos="http://www.sat.gob.mx/ventavehiculos" xmlns:pfic="http://www.sat.gob.mx/pfic" xmlns:tpe="http://www.sat.gob.mx/TuristaPasajeroExtranjero" xmlns:leyendasFisc="http://www.sat.gob.mx/leyendasFiscales" xmlns:spei="http://www.sat.gob.mx/spei">
	<!-- Con el siguiente método se establece que la salida deberá ser en texto -->
	<!-- Integración de complemento SPEI 14-08-2012> -->
	<xsl:output method="text" version="1.0" encoding="UTF-8" indent="no"/>
	<!--
		En esta sección se define la inclusión de las plantillas de utilerías para colapsar espacios
	-->
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/2/cadenaoriginal_2_0/utilerias.xslt"/>
	<!-- 
		En esta sección se define la inclusión de las demás plantillas de transformación para 
		la generación de las cadenas originales de los complementos fiscales 
	-->
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/ecc/ecc.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/psgecfd/psgecfd.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/divisas/divisas.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/ecb/ecb.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/implocal/implocal.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/terceros/terceros11.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/iedu/iedu.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/ventavehiculos/ventavehiculos.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/pfic/pfic.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/TuristaPasajeroExtranjero/TuristaPasajeroExtranjero.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/leyendasFiscales/leyendasFisc.xslt"/>
	<xsl:include href="http://www.sat.gob.mx/sitio_internet/cfd/spei/spei.xslt"/>
	<!-- Aquí iniciamos el procesamiento de la cadena original con su | inicial y el terminador || -->
	<xsl:template match="/">|<xsl:apply-templates select="/cfdi:Comprobante"/>||</xsl:template>
	<!--  Aquí iniciamos el procesamiento de los datos incluidos en el comprobante -->
	<xsl:template match="cfdi:Comprobante">
		<!-- Iniciamos el tratamiento de los atributos de comprobante -->
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@version"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@fecha"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@tipoDeComprobante"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@formaDePago"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@condicionesDePago"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@subTotal"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@descuento"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@TipoCambio"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@Moneda"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@total"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@metodoDePago"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@LugarExpedicion"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@NumCtaPago"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@FolioFiscalOrig"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@SerieFolioFiscalOrig"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@FechaFolioFiscalOrig"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@MontoFolioFiscalOrig"/>
		</xsl:call-template>
		<!--
			Llamadas para procesar al los sub nodos del comprobante
		-->
		<xsl:apply-templates select="./cfdi:Emisor"/>
		<xsl:apply-templates select="./cfdi:Receptor"/>
		<xsl:apply-templates select="./cfdi:Conceptos"/>
		<xsl:apply-templates select="./cfdi:Impuestos"/>
		<xsl:apply-templates select="./cfdi:Complemento"/>
	</xsl:template>
	<!-- Manejador de nodos tipo Emisor -->
	<xsl:template match="cfdi:Emisor">
		<!-- Iniciamos el tratamiento de los atributos del Emisor -->
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@rfc"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@nombre"/>
		</xsl:call-template>
		<!--
			Llamadas para procesar al los sub nodos del comprobante
		-->
		<xsl:apply-templates select="./cfdi:DomicilioFiscal"/>
		<xsl:if test="./cfdi:ExpedidoEn">
			<xsl:call-template name="Domicilio">
				<xsl:with-param name="Nodo" select="./cfdi:ExpedidoEn"/>
			</xsl:call-template>
		</xsl:if>
		<xsl:for-each select="./cfdi:RegimenFiscal">
			<xsl:call-template name="Requerido">
				<xsl:with-param name="valor" select="./@Regimen"/>
			</xsl:call-template>
		</xsl:for-each>
	</xsl:template>
	<!-- Manejador de nodos tipo Receptor -->
	<xsl:template match="cfdi:Receptor">
		<!-- Iniciamos el tratamiento de los atributos del Receptor -->
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@rfc"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@nombre"/>
		</xsl:call-template>
		<!--
			Llamadas para procesar al los sub nodos del Receptor
		-->
		<xsl:if test="./cfdi:Domicilio">
			<xsl:call-template name="Domicilio">
				<xsl:with-param name="Nodo" select="./cfdi:Domicilio"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>
	<!-- Manejador de nodos tipo Conceptos -->
	<xsl:template match="cfdi:Conceptos">
		<!-- Llamada para procesar los distintos nodos tipo Concepto -->
		<xsl:for-each select="./cfdi:Concepto">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
	</xsl:template>
	<!-- Manejador de nodos tipo Impuestos -->
	<xsl:template match="cfdi:Impuestos">
		<xsl:for-each select="./cfdi:Retenciones/cfdi:Retencion">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@totalImpuestosRetenidos"/>
		</xsl:call-template>
		<xsl:for-each select="./cfdi:Traslados/cfdi:Traslado">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@totalImpuestosTrasladados"/>
		</xsl:call-template>
	</xsl:template>
	<!-- Manejador de nodos tipo Retencion -->
	<xsl:template match="cfdi:Retencion">
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@impuesto"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@importe"/>
		</xsl:call-template>
	</xsl:template>
	<!-- Manejador de nodos tipo Traslado -->
	<xsl:template match="cfdi:Traslado">
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@impuesto"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@tasa"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@importe"/>
		</xsl:call-template>
	</xsl:template>
	<!-- Manejador de nodos tipo Complemento -->
	<xsl:template match="cfdi:Complemento">
		<xsl:for-each select="./*">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
	</xsl:template>
	<!--
		Manejador de nodos tipo Concepto
	-->
	<xsl:template match="cfdi:Concepto">
		<!-- Iniciamos el tratamiento de los atributos del Concepto -->
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@cantidad"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@unidad"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@noIdentificacion"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@descripcion"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@valorUnitario"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@importe"/>
		</xsl:call-template>
		<!--
			Manejo de los distintos sub nodos de información aduanera de forma indistinta 
			a su grado de dependencia
		-->
		<xsl:for-each select=".//cfdi:InformacionAduanera">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
		<!-- Llamada al manejador de nodos de Cuenta Predial en caso de existir -->
		<xsl:if test="./cfdi:CuentaPredial">
			<xsl:apply-templates select="./cfdi:CuentaPredial"/>
		</xsl:if>
		<!-- Llamada al manejador de nodos de ComplementoConcepto en caso de existir -->
		<xsl:if test="./cfdi:ComplementoConcepto">
			<xsl:apply-templates select="./cfdi:ComplementoConcepto"/>
		</xsl:if>
	</xsl:template>
	<!-- Manejador de nodos tipo Información Aduanera -->
	<xsl:template match="cfdi:InformacionAduanera">
		<!-- Manejo de los atributos de la información aduanera -->
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@numero"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@fecha"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@aduana"/>
		</xsl:call-template>
	</xsl:template>
	<!-- Manejador de nodos tipo Información CuentaPredial -->
	<xsl:template match="cfdi:CuentaPredial">
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@numero"/>
		</xsl:call-template>
	</xsl:template>
	<!-- Manejador de nodos tipo ComplementoConcepto -->
	<xsl:template match="cfdi:ComplementoConcepto">
		<xsl:for-each select="./*">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
	</xsl:template>
	<!-- Manejador de nodos tipo Domicilio fiscal -->
	<xsl:template match="cfdi:DomicilioFiscal">
		<!-- Iniciamos el tratamiento de los atributos del Domicilio Fiscal -->
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@calle"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@noExterior"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@noInterior"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@colonia"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@localidad"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="./@referencia"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@municipio"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@estado"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@pais"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="./@codigoPostal"/>
		</xsl:call-template>
	</xsl:template>
	<!-- Manejador de nodos tipo Domicilio -->
	<xsl:template name="Domicilio">
		<xsl:param name="Nodo"/>
		<!-- Iniciamos el tratamiento de los atributos del Domicilio  -->
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@calle"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@noExterior"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@noInterior"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@colonia"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@localidad"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@referencia"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@municipio"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@estado"/>
		</xsl:call-template>
		<xsl:call-template name="Requerido">
			<xsl:with-param name="valor" select="$Nodo/@pais"/>
		</xsl:call-template>
		<xsl:call-template name="Opcional">
			<xsl:with-param name="valor" select="$Nodo/@codigoPostal"/>
		</xsl:call-template>
	</xsl:template>
</xsl:stylesheet>
