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
addresses = utils.AutoDict(model.Address)
organizations = utils.AutoDict(model.Organization)

## Extract organization types

logging.info("Processing hierarchy_types")
for id, name in data.type_name.items():
    ot = orgtypes[id]
    ot.name = Literal(name, lang="el")


## Extract organizations

logging.info("Processing census")
for e in data.census:
    org = organizations[e.cid]
    org.name.add(Literal(e.name, lang="el"))

logging.info("Processing hierarchy")
stack = list(organizations.keys())
while stack:
    cid = stack.pop()
    if cid in data.hierarchy:
        org = organizations[cid]
        e = data.hierarchy[cid]
        org.name.add(Literal(e.name, lang="el"))
        if e.type_id:
            org.type = orgtypes[e.type_id]
        if e.parent_cid:
            if e.parent_cid not in organizations:
                stack.append(e.parent_cid)
            org.parent.add(organizations[e.parent_cid])


## Validate model

logging.info("Validating")
model.validate(orgtypes.values(),
               addresses.values(),
               organizations.values()).log()


## Produce RDF

logging.info("Constructing RDF graph")
g = rdf.Graph()
g.add(orgtypes.values())
g.add(addresses.values())
g.add(organizations.values())
logging.info("Serializing RDF graph")
with open(args.output, 'wb') as f:
    g.serialize(f, format=args.format)
