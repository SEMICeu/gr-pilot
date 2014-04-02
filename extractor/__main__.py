# Entry point
#
# Copyright 2014 European Union
#
# Licensed under the EUPL, Version 1.1 or - as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

import logging
import argparse

from . import utils


## CLI

parser = argparse.ArgumentParser(prog="extractor")
parser.add_argument('-o', '--output', default='data.ttl',
                    help="output filename (default: %(default)s)")
parser.add_argument('-f', '--format', default='turtle',
                    help="output format (default: %(default)s)")
parser.add_argument('-v', '--verbose', action='store_true',
                    help="be verbose")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                    format="[%(asctime)s] %(levelname)s %(message)s")


## Initialize data

logging.info("Loading data")
from . import data

from . import model
from . import rdf
from .rdf import URIRef, Literal

orgtypes = utils.AutoDict(model.OrganizationType)
categories = utils.AutoDict(model.OrganizationCategory)
addresses = utils.AutoDict(model.Address)
organizations = utils.AutoDict(model.Organization)


## Extract data

logging.info("Processing  organization types")
for i, (norm, labels) in enumerate(sorted(data.transparency.type_by_typenorm.items())):
    # TODO: Have a better identifier for the URI
    orgtypes[norm] = model.OrganizationType(i)
    orgtypes[norm].label = Literal(next(iter(labels)), lang="el")

logging.info("Processing organizations")
for vat, entries in data.transparency.by_vat.items():
    org = organizations[vat]
    org.identifier = vat
    for e in entries:
        org.name.add(Literal(e.name, lang="el"))
        if e.type:
            org.type.add(orgtypes[utils.namenorm(e.type)])
        if e.cid in data.census.by_cid:
            for ce in data.census.by_cid[e.cid]:
                org.name.add(Literal(ce.name, lang="el"))
                addr = addresses[ce.address_id]
                org.address.add(addr)
                full = ""
                if ce.street1:
                    addr.thoroughfare.add(ce.street1)
                    full = ce.street1
                    if ce.number1:
                        addr.locatorDesignator.add(ce.number1)
                        full += " " + ce.number1
                    full += ", "
                addr.adminUnitL2.add(ce.municipality)
                full += ce.municipality
                if ce.postcode:
                    addr.postCode.add(ce.postcode)
                    full += " " + ce.postcode
                addr.adminUnitL1.add(ce.country)
                full += ", " + ce.country
                addr.fullAddress.add(full)
                addr.label.add(Literal(full, lang="el"))
        if e.cid in data.hierarchy:
            he = data.hierarchy[e.cid]
            org.name.add(Literal(he.name, lang="el"))
            if he.type_id:
                org.category.add(categories[he.type_id])
            if he.parent_cid != he.cid and he.parent_cid in data.transparency.by_cid:
                for p in data.transparency.by_cid[he.parent_cid]:
                    org.parent.add(organizations[p.vat])
    if vat in data.syzefxis.by_vat:
        for se in data.syzefxis.by_vat[vat]:
            if se.source.startswith('00'):
                org.phone.add(URIRef("tel:+" + se.source[2:]))

logging.info("Processing categories")
for id, cat in categories.items():
    cat.label = Literal(data.type_name[id], lang="el")


## Validate model

logging.info("Validating")
model.validate(orgtypes.values(),
               addresses.values(),
               organizations.values()).log()


## Produce RDF

logging.info("Constructing RDF graph")
g = rdf.Graph()
g.add(model.ORGANIZATION_TYPES)
g.add(orgtypes.values())
g.add(addresses.values())
g.add(organizations.values())
logging.info("Serializing RDF graph")
with open(args.output, 'wb') as f:
    g.serialize(f, format=args.format)

logging.info("Done")
