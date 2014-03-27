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

from .model import *

## Extract organization types
logging.info("Processing hierarchy_types")

orgtypes = {}

for id, name in data.type_name.items():
    ot = OrganizationType(id)
    ot.name = Literal(name, lang="el")


## Extract organizations

logging.info("Processing hierarchy")
organizations = {e.cid:Organization(e.cid) for e in data.hierarchy}

for e in data.hierarchy:
    org = organizations[e.cid]
    org.name = {Literal(e.name, lang="el")}
    if e.type_id in orgtypes:
        org.type = orgtypes[e.type_id]
    org.parent = set()
    if e.parent_cid in organizations:
        org.parent.add(organizations[e.parent_cid])

logging.info("Processing census")
for e in data.census:
    if e.cid not in organizations:
        org = Organization(e.cid)
        org.name = set()
        org.parent = set()
        organizations[e.cid] = org
    org = organizations[e.cid]
    org.name.add(Literal(e.name, lang="el"))


## Validate model

logging.info("Validating")

result = ValidationResult()
for t in orgtypes.values():
    t.validate(result=result)
for o in organizations.values():
    o.validate(result=result)
result.log()


## Produce RDF

logging.info("Constructing RDF graph")
g = Graph()
g.add(orgtypes.values())
g.add(organizations.values())
logging.info("Serializing RDF graph")
with open(args.output, 'wb') as f:
    g.serialize(f, format=args.format)
