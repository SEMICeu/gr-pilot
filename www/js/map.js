/*
  Javascript functionalities for adding addresses to a map

  Copyright 2014 European Union
  Author: Vianney le Clément de Saint-Marcq (PwC EU Services)

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

$(function() {
  // Get addresses inside #map
  var addresses = $("#map > a").detach();
  // Initialize map
  var map = L.map('map', {
    center: [38.746, 22.396],
    zoom: 7,
    minZoom: 6
  });
  L.tileLayer('http://{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.jpg', {
    subdomains: ['otile1', 'otile2', 'otile3', 'otile4'],
    attribution: 'Map data &copy; <a href="http://openstreetmap.org" target="_blank">OpenStreetMap</a> contributors, Imagery &copy; <a href="http://open.mapquest.co.uk"  target="_blank">MapQuest</a>',
    maxZoom: 18
  }).addTo(map);
  // Lookup addresses
  var bounds = [];
  addresses.each(function() {
    $.getJSON("http://nominatim.openstreetmap.org/search", {
      'q': $(this).attr('nominatim'),
      'format': 'json'
    }, (function(data) {
      if(data.length > 0) {
        var pos = [data[0].lat, data[0].lon];
        bounds.push(pos);
        var marker = L.marker(pos).addTo(map);
        marker.bindPopup(this);
        map.fitBounds(bounds);
      }
    }).bind(this));
  });
});

/* vim:set ts=2 sw=2 et: */
