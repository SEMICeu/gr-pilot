<?xml version="1.0" encoding="utf-8"?>
<!--
  XSLT script to show a detailed view about a particular resource

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

  SELECT DISTINCT * WHERE {
    {
      <$s1> ?p ?o
      OPTIONAL { { SELECT ?p SAMPLE(?label) AS ?plabel
                   WHERE { ?p rdfs:label ?label } GROUP BY ?p } }
      OPTIONAL { { SELECT ?o SAMPLE(?label) AS ?olabel
                   WHERE { ?o rdfs:label ?label } GROUP BY ?o } }
    } UNION {
      ?s ?ip <$s1>
      OPTIONAL { { SELECT ?ip SAMPLE(?label) AS ?iplabel
                   WHERE { ?ip rdfs:label ?label } GROUP BY ?ip } }
      OPTIONAL { { SELECT ?s SAMPLE(?label) AS ?slabel
                   WHERE { ?s rdfs:label ?label } GROUP BY ?s } }
    }
    BIND(<$s1> AS ?target)
  } ORDER BY ?ip ?p

-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:res="http://www.w3.org/2005/sparql-results#"
  xmlns:ns="http://semic.eu/namespaces"
  exclude-result-prefixes="xsl res ns">

  <xsl:output method="html" indent="yes" encoding="UTF-8" />

  <xsl:variable name="namespaces" select="document('http://data.ydmed.gov.gr/namespaces.xml')" />

  <xsl:variable name="target" select="//res:result/res:binding[@name='target'][1]" />

  <!--
    Main templates
  -->

  <!-- Root template -->
  <xsl:template match="res:sparql">
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html></xsl:text>
    <html>
      <head>
        <meta charset="UTF-8" />
        <title>About: <xsl:call-template name="target-label" /></title>
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <link rel="stylesheet" type="text/css" href="/css/normalize.css" />
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Source+Sans+Pro:400,400italic,600,600italic,300" />
        <link rel="stylesheet" type="text/css" href="/css/screen.css" />
        <script type="text/javascript" src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
      </head>
      <body>
      <header>
        <div class="logo">
          <a href="https://www.semic.eu">
            <img src="/images/semic_logo.png" alt="SEMIC logo" width="90" height="90" />
          </a>
        </div>
        <h1>Greek Open Data pilot</h1>
        <p class="subtitle">A hierarchy of public administrations</p>
      </header>

      <xsl:choose>
        <xsl:when test="$target">
          <section>
            <xsl:call-template name="info" />
          </section>

          <section>
            <h2>Properties</h2>
            <xsl:call-template name="properties" />
          </section>

          <section>
            <h2>Referenced by</h2>
            <xsl:call-template name="inverse-properties" />
          </section>
        </xsl:when>
        <xsl:otherwise>
          <section>
            <h2>About</h2>
            <div class="error">The resource you are looking for was not found.</div>
          </section>
        </xsl:otherwise>
      </xsl:choose>

      <footer>
        <p>Work in progress.</p>
      </footer>
      <script type="text/javascript"><xsl:text>
        var _gaq = _gaq || [];
        _gaq.push(['_setAccount', 'UA-38243808-1']);
        _gaq.push(['_trackPageview']);

        (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
        })();
      </xsl:text></script>
      </body>
    </html>
  </xsl:template>

  <!-- Print the information section -->
  <xsl:template name="info">
    <h2><xsl:call-template name="target-label" /></h2>
    <xsl:call-template name="target-description" />
    <dl class="properties">
      <dt>URI</dt>
      <dd><a href="{$target}"><xsl:value-of select="$target" /></a></dd>
      <xsl:variable name="type" select="//res:result[res:binding[@name='p']='http://www.w3.org/1999/02/22-rdf-syntax-ns#type']" />
      <xsl:if test="$type">
        <xsl:variable name="type-uri" select="$type/res:binding[@name='o']" />
        <xsl:variable name="type-label" select="$type/res:binding[@name='olabel']" />
        <dt>Type</dt>
        <dd>
          <xsl:call-template name="label-or-value">
            <xsl:with-param name="value" select="$type-uri" />
            <xsl:with-param name="label" select="$type-label" />
            <xsl:with-param name="strip-uri" select="true()" />
          </xsl:call-template>
        </dd>
      </xsl:if>
      <dt>Raw data</dt>
      <dd><a>
        <xsl:attribute name="href">
          <xsl:call-template name="resolve-uri">
            <xsl:with-param name="uri" select="$target" />
          </xsl:call-template>
          <xsl:text>/rdf</xsl:text>
        </xsl:attribute>
        RDF/XML
      </a></dd>
    </dl>
  </xsl:template>

  <!-- Print the Properties table -->
  <xsl:template name="properties">
    <table><tbody>
      <xsl:for-each select="//res:results/res:result">
        <xsl:if test="res:binding[@name='o']">
          <tr>
            <td>
              <xsl:call-template name="label-or-value">
                <xsl:with-param name="value" select="res:binding[@name='p']" />
                <xsl:with-param name="label" select="res:binding[@name='plabel']" />
                <xsl:with-param name="strip-uri" select="true()" />
              </xsl:call-template>
            </td>
            <td>
              <xsl:call-template name="label-or-value">
                <xsl:with-param name="value" select="res:binding[@name='o']" />
                <xsl:with-param name="label" select="res:binding[@name='olabel']" />
              </xsl:call-template>
            </td>
          </tr>
        </xsl:if>
      </xsl:for-each>
    </tbody></table>
  </xsl:template>

  <!-- Print the Inverse Properties table -->
  <xsl:template name="inverse-properties">
    <table><tbody>
      <xsl:for-each select="//res:results/res:result">
        <xsl:if test="res:binding[@name='s']">
          <tr>
            <td>
              <xsl:call-template name="label-or-value">
                <xsl:with-param name="value" select="res:binding[@name='ip']" />
                <xsl:with-param name="label" select="res:binding[@name='iplabel']" />
                <xsl:with-param name="strip-uri" select="true()" />
              </xsl:call-template>
            </td>
            <td>
              <xsl:call-template name="label-or-value">
                <xsl:with-param name="value" select="res:binding[@name='s']" />
                <xsl:with-param name="label" select="res:binding[@name='slabel']" />
              </xsl:call-template>
            </td>
          </tr>
        </xsl:if>
      </xsl:for-each>
    </tbody></table>
  </xsl:template>

  <!--
    Parts rendering
  -->

  <!-- Print a description of the target -->
  <xsl:template name="target-description">
    <xsl:call-template name="target-description-type">
      <xsl:with-param name="type" select="'http://www.w3.org/2000/01/rdf-schema#comment'" />
    </xsl:call-template>
    <xsl:call-template name="target-description-type">
      <xsl:with-param name="type" select="'http://purl.org/dc/elements/1.1/description'" />
    </xsl:call-template>
    <xsl:call-template name="target-description-type">
      <xsl:with-param name="type" select="'http://purl.org/dc/terms/description'" />
    </xsl:call-template>
    <xsl:call-template name="target-description-type">
      <xsl:with-param name="type" select="'http://www.w3.org/2004/02/skos/core#definition'" />
    </xsl:call-template>
  </xsl:template>
  <xsl:template name="target-description-type">
    <xsl:param name="type" />
    <xsl:for-each select="//res:result[res:binding[@name='p'] = $type]">
      <p>
        <xsl:call-template name="label-or-value">
          <xsl:with-param name="value" select="res:binding[@name='o']" />
          <xsl:with-param name="label" select="res:binding[@name='olabel']" />
        </xsl:call-template>
      </p>
    </xsl:for-each>
  </xsl:template>

  <!-- Print a cell of the table, either its value or, in the case of URIs, its
  label if it exists. -->
  <xsl:template name="label-or-value">
    <xsl:param name="value" /><!-- the res:binding of the value -->
    <xsl:param name="label" /><!-- the res:binding of the label -->
    <xsl:param name="strip-uri" select="false()" />
    <xsl:choose>
      <xsl:when test="$label">
        <a>
          <xsl:attribute name="href">
            <xsl:call-template name="resolve-uri">
              <xsl:with-param name="uri" select="$value" />
            </xsl:call-template>
          </xsl:attribute>
          <xsl:apply-templates select="$label" />
        </a>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="$value">
          <xsl:with-param name="strip-uri" select="$strip-uri" />
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Handle a blank node -->
  <xsl:template match="res:bnode">
    <xsl:text>(</xsl:text>
    <xsl:value-of select="text()" />
    <xsl:text>)</xsl:text>
  </xsl:template>

  <!-- Handle a URI -->
  <xsl:template match="res:uri">
    <xsl:param name="strip-uri" select="false()" />
    <xsl:variable name="uri" select="text()" />
    <a>
      <xsl:attribute name="href">
        <xsl:call-template name="resolve-uri">
          <xsl:with-param name="uri" select="$uri" />
        </xsl:call-template>
      </xsl:attribute>
      <xsl:call-template name="to-curie">
        <xsl:with-param name="uri" select="$uri" />
        <xsl:with-param name="strip" select="$strip-uri" />
      </xsl:call-template>
    </a>
  </xsl:template>

  <!-- Handle a literal -->
  <xsl:template match="res:literal">
    <xsl:value-of select="text()" />
  </xsl:template>

  <!--
    Utilities
  -->

  <!-- Print the label of the target, or its stripped URI if there is no label.
  -->
  <xsl:template name="target-label">
    <xsl:choose>
      <xsl:when test="//res:result/res:binding[@name = 'p'] = 'http://www.w3.org/2000/01/rdf-schema#label'">
        <xsl:variable name="result" select="//res:result[res:binding[@name = 'p'] = 'http://www.w3.org/2000/01/rdf-schema#label']" />
        <xsl:value-of select="$result/res:binding[@name = 'o']" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="strip-uri">
          <xsl:with-param name="uri" select="$target" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Return a resolvable URI -->
  <xsl:template name="resolve-uri">
    <xsl:param name="uri" />
    <xsl:text>/about/</xsl:text>
    <xsl:call-template name="urlencode">
      <xsl:with-param name="value" select="$uri" />
    </xsl:call-template>
  </xsl:template>

  <!-- Print the CURIE version of a URI using the namespaces defined in an
  external document. -->
  <xsl:template name="to-curie">
    <xsl:param name="uri" />
    <xsl:param name="strip" select="false()" /><!-- fallback to strip-uri? -->
    <xsl:choose>
      <xsl:when test="$namespaces//ns:namespace[starts-with($uri, ns:uri)]">
        <xsl:variable name="ns" select="$namespaces//ns:namespace[starts-with($uri, ns:uri)]" />
        <xsl:value-of select="$ns/ns:prefix" />
        <xsl:text>:</xsl:text>
        <xsl:value-of select="substring($uri, string-length($ns/ns:uri) + 1)" />
      </xsl:when>
      <xsl:when test="$strip">
        <xsl:call-template name="strip-uri">
          <xsl:with-param name="uri" select="$uri" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$uri" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Strip a URI to its last component. E.g., http://example.com/id/test/
  would become test, and http://example.com/def#property would become property.
  -->
  <xsl:template name="strip-uri">
    <xsl:param name="uri" />
    <xsl:choose>
      <xsl:when test="contains($uri, '/')">
        <xsl:choose>
          <xsl:when test="substring-after($uri, '/') = ''">
            <xsl:value-of select="substring-before($uri, '/')" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="strip-uri">
              <xsl:with-param name="uri" select="substring-after($uri, '/')" />
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="contains($uri, '#')">
            <xsl:value-of select="substring-after($uri, '#')" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$uri" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- URL-encode a value -->
	<xsl:variable name="url-hex" select="'0123456789ABCDEF'"/>
	<xsl:variable name="url-ascii"> !"#$%&amp;'()*+,-./0123456789:;&lt;=&gt;?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~</xsl:variable>
	<xsl:variable name="url-safe">!'()*-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~</xsl:variable>
  <xsl:template name="urlencode">
    <xsl:param name="value" />
    <xsl:if test="$value">
      <xsl:variable name="char" select="substring($value,1,1)" />
      <xsl:choose>
        <xsl:when test="contains($url-safe, $char)">
          <xsl:value-of select="$char" />
        </xsl:when>
        <xsl:when test="contains($url-ascii, $char)">
          <xsl:variable name="codepoint" select="string-length(substring-before($url-ascii,$char)) + 32" />
          <xsl:variable name="hex-digit1" select="substring($url-hex, floor($codepoint div 16) + 1,1)" />
          <xsl:variable name="hex-digit2" select="substring($url-hex, $codepoint mod 16 + 1,1)" />
          <xsl:value-of select="concat('%', $hex-digit1, $hex-digit2)" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$char" />
        </xsl:otherwise>
      </xsl:choose>
      <xsl:call-template name="urlencode">
        <xsl:with-param name="value" select="substring($value, 2)" />
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
<!-- vim:set ts=2 sw=2 et: -->
