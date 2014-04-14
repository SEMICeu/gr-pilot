Greek data pilot
=================

1. Configuration
-----------------

From the root of the repository, run `./configure.sh` to set up the pilot.
You can pass additional arguments to set the base URI and other parameters.
Run `./configure -h` to get a list of options.


2. Exporting the data as CSV
-----------------------------

The Access tables and Excel sheets must be extracted as CSV using the following
parameters:

* Encoding: UTF-8
* Delimiter: Comma (,)
* Quote character: "

The following files shall be put in the `data` directory:

File                    | Origin
------------------------|------------------------------------------------------
census.csv              | Access database › organikos\_work\_reference
hierarchy.csv           | Access database › ierarxia (see note below)
transparency.csv        | Access database › ΜΗΤΡΩΟ ΦΟΡΕΩΝ ΔΙΑΥΓΕΙΑ
syzefxis.csv            | Access database › syzefxis\_address
hierarchy\_types.csv    | Access database › typos\_ierarxia
kep.csv                 | Stoixeia\_KEP spreadsheet › Φύλλο2

*Note:* The `ierarxia` table needs additional processing to remove ASCII control
characters:

    sed -i 's/\x16/;/g; s/\x11/‘/g; s/\x12/’/g; s/\x13/“/g; s/\x14/”/g' hierarchy.csv


3. Converting the data to RDF
------------------------------

The extractor scripts needs a [Python][] 3.3 or later interpreter with the
[rdflib][] 4 module.

To convert the data located in the `data` directory, run the following command
at the root of the repository:

    python -m extractor

By default, the generated RDF data will be written in the `data.ttl` file at
the root of the repository.

[Python]: http://python.org/
[rdflib]: https://pypi.python.org/pypi/rdflib


4. Setting up Virtuoso
-----------------------

The pilot is designed to be hosted by the [Virtuoso Universal Server][].
Follow these steps to set up the pilot:

1. Upload `data.ttl` to the Quad Store, e.g., in the
   `http://data.ydmed.gov.gr/` graph.
2. Copy or move the whole repository to the `gr-pilot` subdirectory of
   Virtuoso's `vsp` directory.
3. Set up a virtual host for `data.ydmed.gov.gr`.
4. Edit the `/` path with the following parameters:
   * Physical path: `/gr-pilot/www/`
   * Default page: `index.vsp`
   * VSP User: `dba`
5. Set up the following rewrite rules for the `/` path. All rules must be set
   as *First matching*.

   Source pattern                             | Destination                                   | Response code
   -------------------------------------------|-----------------------------------------------|---------------
   `^/search(.*)$`                            | `/search.vsp$s1`                              | Internal
   `^/about/([^/]*)/(.*)$`                    | `/description.vsp?format=$U1&uri=$s2`         | Internal
   `^/doc/([^/.]*)(?:/([^/.]*))?(?:\.(.*))?$` | `/description.vsp?type=$U1&id=$U2&format=$U3` | Internal
   `^/id/(.*)$`                               | `/doc/$s1`                                    | 303

*Note:* if you choose another subdirectory or another virtual host, use the
`configure.sh` script with the appropriate arguments.

[Virtuoso Universal Server]: http://virtuoso.openlinksw.com/



Licence
--------

Copyright 2014 European Union
Author: Vianney le Clément de Saint-Marcq (PwC EU Services)

Licensed under the EUPL, Version 1.1 or - as soon they
will be approved by the European Commission - subsequent
versions of the EUPL (the "Licence");
You may not use this work except in compliance with the
Licence.
You may obtain a copy of the Licence at:
<http://ec.europa.eu/idabc/eupl>

Unless required by applicable law or agreed to in
writing, software distributed under the Licence is
distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied.
See the Licence for the specific language governing
permissions and limitations under the Licence.
