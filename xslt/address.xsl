<?xml version="1.0" encoding="utf-8"?>
<!--
  XSLT script to show a detailed view of a locn:Address

  Copyright 2014 European Union

  Licensed under the EUPL, Version 1.1 or - as soon they
  will be approved by the European Commission - subsequent
  versions of the EUPL (the "Licence");
  You may not use this work except in compliance with the
  Licence.
  You may obtain a copy of the Licence at:
  http://ec.europa.eu/idabc/eupl

  Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
  See the Licence for the specific language governing
  permissions and limitations under the Licence.


  This script is meant to be applied to the results of the following SPARQL
  query (in application/sparql-results+xml format), where <$s1> is the target
  resource URI.

  CONSTRUCT {
    <$s1> a locn:Address ;
      rdfs:label ?label ;
      locn:thoroughfare ?street ;
      locn:locatorDesignator ?number ;
      locn:postCode ?postcode ;
      locn:adminUnitL2 ?municipality ;
      locn:adminUnitL1 ?country .
    ?org locn:address <$s1> ;
      rdfs:label ?orglabel .
  } WHERE {
    <$s1> a locn:Address ;
      rdfs:label ?label .
    OPTIONAL { <$s1> locn:thoroughfare ?street }
    OPTIONAL { <$s1> locn:locatorDesignator ?number }
    OPTIONAL { <$s1> locn:postCode ?postcode }
    OPTIONAL { <$s1> locn:adminUnitL2 ?municipality }
    OPTIONAL { <$s1> locn:adminUnitL1 ?country }
    ?org locn:address <$s1> ;
      rdfs:label ?orglabel .
  }

-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:locn="http://www.w3.org/ns/locn#"
  exclude-result-prefixes="xsl rdf rdfs locn">

  <xsl:include href="file://gr-pilot/xslt/include.xsl" />

  <xsl:output method="html" indent="yes" encoding="UTF-8" />

  <xsl:variable name="subject" select="//rdf:Description[rdf:type[@rdf:resource = 'http://www.w3.org/ns/locn#Address']]" />

  <!-- Root template -->
  <xsl:template match="rdf:RDF">
    <xsl:call-template name="html">
      <xsl:with-param name="title">
        About: <xsl:value-of select="$subject/rdfs:label" />
      </xsl:with-param>
      <xsl:with-param name="leaflet" select="true()" />
      <xsl:with-param name="body">
        <xsl:choose>
          <xsl:when test="$subject">
            <xsl:call-template name="content" />
          </xsl:when>
          <xsl:otherwise>
            <section>
              <h2>About</h2>
              <div class="error">The address you are looking for was not found.</div>
            </section>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:with-param>
    </xsl:call-template>
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html></xsl:text>
  </xsl:template>

  <!-- Real content -->
  <xsl:template name="content">
    <section>
      <h2><xsl:value-of select="$subject/rdfs:label" /></h2>
      <dl class="properties">
        <xsl:if test="$subject/locn:thoroughfare">
          <dt>Street</dt>
          <dd><xsl:value-of select="$subject/locn:thoroughfare" /></dd>
        </xsl:if>
        <xsl:if test="$subject/locn:locatorDesignator">
          <dt>Number</dt>
          <dd><xsl:value-of select="$subject/locn:locatorDesignator" /></dd>
        </xsl:if>
        <xsl:if test="$subject/locn:postCode">
          <dt>Postal code</dt>
          <dd><xsl:value-of select="$subject/locn:postCode" /></dd>
        </xsl:if>
        <xsl:if test="$subject/locn:adminUnitL2">
          <dt>Municipality</dt>
          <dd><xsl:value-of select="$subject/locn:adminUnitL2" /></dd>
        </xsl:if>
        <xsl:if test="$subject/locn:adminUnitL1">
          <dt>Country</dt>
          <dd><xsl:value-of select="$subject/locn:adminUnitL1" /></dd>
        </xsl:if>
      </dl>
    </section>
    <section>
      <h2>Map</h2>
      <div id="map">
        <xsl:call-template name="map-address">
          <xsl:with-param name="address" select="$subject" />
        </xsl:call-template>
      </div>
    </section>
    <section>
      <h2>Located at this address</h2>
      <ul>
        <xsl:for-each select="//rdf:Description[locn:address]">
          <li>
            <a href="{@rdf:about}">
              <xsl:value-of select="rdfs:label" />
            </a>
          </li>
        </xsl:for-each>
      </ul>
    </section>
  </xsl:template>

</xsl:stylesheet>
<!-- vim:set ts=2 sw=2 et: -->
