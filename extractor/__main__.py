# Entry point
#
# Copyright 2014 European Union
# Author: Vianney le Clément de Saint-Marcq (PwC EU Services)
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
addresses = {}
organizations = utils.AutoDict(model.Organization)


## Extract data

logging.info("Processing organization types")
for i, (norm, labels) in enumerate(sorted(data.transparency.type_by_typenorm.items())):
    # TODO: Have a better identifier for the URI
    orgtypes[norm] = model.OrganizationType(i)
    orgtypes[norm].label = Literal(next(iter(labels)), lang="el")

logging.info("Processing organizations")
for cid, entries in data.census.by_cid.items():
    org = organizations[cid]
    for e in entries:
        org.name.add(Literal(e.name, lang="el"))
        addr_key = (e.street1, e.number1, e.postcode, e.municipality, e.country)
        if addr_key not in addresses:
            addresses[addr_key] = model.Address(e.address_id)
        addr = addresses[addr_key]
        org.address.add(addr)
        full = ""
        if e.street1:
            addr.thoroughfare.add(e.street1)
            full = e.street1
            if e.number1:
                addr.locatorDesignator.add(e.number1)
                full += " " + e.number1
            full += ", "
        addr.adminUnitL2.add(e.municipality)
        full += e.municipality
        if e.postcode:
            addr.postCode.add(e.postcode)
            full += " " + e.postcode
        addr.adminUnitL1.add(e.country)
        full += ", " + e.country
        addr.fullAddress.add(full)
        addr.label.add(Literal(full, lang="el"))
    if cid in data.hierarchy:
        he = data.hierarchy[cid]
        org.name.add(Literal(he.name, lang="el"))
        if he.type_id:
            org.category.add(categories[he.type_id])
        if he.parent_cid != he.cid and he.parent_cid in data.census.by_cid:
            org.parent.add(organizations[he.parent_cid])
    if cid in data.transparency.by_cid:
        for te in data.transparency.by_cid[cid]:
            org.name.add(Literal(te.name, lang="el"))
            org.identifier.add(te.vat)
            if te.type:
                org.type.add(orgtypes[utils.namenorm(te.type)])
            if te.vat in data.syzefxis.by_vat:
                for se in data.syzefxis.by_vat[te.vat]:
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
