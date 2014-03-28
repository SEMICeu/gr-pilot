<?xml version="1.0" encoding="utf-8"?>
<!--
  XSLT script to format the list of organization types.

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


  This script is meant to be applied to the results of the following
  SPARQL queries (in application/sparql-results+xml format).

  SELECT DISTINCT * WHERE {
    ?type a skos:Concept ;
          skos:topConceptOf <http://data.ydmed.gov.gr/id/type> ;
          rdfs:label ?label .
  } ORDER BY ?label

-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:res="http://www.w3.org/2005/sparql-results#"
  exclude-result-prefixes="xsl res">

  <xsl:output method="html" indent="yes" encoding="UTF-8" />

  <xsl:template match="res:sparql">
    <ul>
      <xsl:for-each select="//res:result">
        <li>
          <a href="{res:binding[@name='type']}">
            <xsl:value-of select="res:binding[@name='label']" />
          </a>
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

</xsl:stylesheet>
<!-- vim:set ts=2 sw=2 et: -->
