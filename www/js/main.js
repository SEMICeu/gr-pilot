/*
  Javascript functionalities for index.html

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
*/

$.fn.filterfind = function(selector) {
  return this.filter(selector).add(this.find(selector));
};

function doSearch() {
  var query = $("#query").val();
  var sparql = 'SELECT DISTINCT * WHERE { ?id a rov:RegisteredOrganization ; ' +
               'rdfs:label ?label . ';
  if(query) {
    query = query.replace('\\', '\\\\')
                 .replace('"', '\\"')
                 .replace('\n', '\\n')
                 .replace('\r', '\\r')
                 .toLowerCase();
    sparql += 'FILTER(CONTAINS(LCASE(STR(?label)), "' + query + '"))';
  }
  sparql += '}';
  $("#results")
    .empty()
    .append('<p class="more"><a href="/sparql?' +
            $.param({
              'query': sparql,
              'format': "application/sparql-results+xml",
              'xslt-uri': "file://gr-pilot/xslt/sparql-table.xsl"
            }) +
            '">See all results &raquo;</a></p>');
  var sparql_limited = sparql + ' LIMIT 10';
  console.log("Executing query: " + sparql_limited);
  $.get("/sparql", {
    'query': sparql_limited,
    'format': "application/sparql-results+xml",
    'xslt-uri': "file://gr-pilot/xslt/sparql-table.xsl"
  }, function(data) {
    $("#results").prepend($(data).filterfind("#results").contents());
  });
}

function initCategories() {
  var sparql = 'SELECT DISTINCT * WHERE { ?uri a skos:Concept ; ' +
               'skos:topConceptOf <http://data.ydmed.gov.gr/id/category> ; ' +
               'rdfs:label ?label . ' +
               '} ORDER BY ?label';
  console.log("Executing query: " + sparql);
  $.get("/sparql", {
    'query': sparql,
    'format': "application/sparql-results+xml",
    'xslt-uri': "file://gr-pilot/xslt/uri-list.xsl"
  }, function(data) {
    $("#categories").prepend(data);
  });
}

$(function() {
  $("#searchform").submit(function(event) {
    doSearch();
    event.preventDefault();
  });
  initCategories();
});

/* vim:set ts=2 sw=2 et: */
