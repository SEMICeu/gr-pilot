# RDF domain model implemented in Python classes
#
# Copyright 2014 PwC EU Services
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

from .rdf import *


@resource(SKOS.ConceptScheme)
class ConceptScheme(Resource):

    name                = Property(RDFS.label, rng=Property.UNIQUETEXT, min=1)
    topConcept          = Property(SKOS.hasTopConcept, rng=URIRef)

    def __init__(self, uri):
        Resource.__init__(self, uri)


ORGANIZATION_TYPES = ConceptScheme("type")
ORGANIZATION_TYPES.name = Literal("Organization types", lang="en")

ORGANIZATION_CATEGORIES = ConceptScheme("category")
ORGANIZATION_CATEGORIES.name = Literal("Organization categories", lang="en")


@resource(SKOS.Concept, "type")
class OrganizationType(Resource):

    label               = Property(RDFS.label, rng=Property.UNIQUETEXT, min=1, max=1)
    scheme              = Property(SKOS.topConceptOf, rng=ConceptScheme, min=1, max=1)

    def __init__(self, uri):
        Resource.__init__(self, uri)
        self.scheme = ORGANIZATION_TYPES


@resource(SKOS.Concept, "category")
class OrganizationCategory(Resource):

    label               = Property(RDFS.label, rng=Property.UNIQUETEXT, min=1, max=1)
    scheme              = Property(SKOS.topConceptOf, rng=ConceptScheme, min=1, max=1)

    def __init__(self, uri):
        Resource.__init__(self, uri)
        self.scheme = ORGANIZATION_CATEGORIES


@resource(LOCN.Address, "address")
class Address(Resource):

    label               = Property(RDFS.label, rng=Property.TEXT)
    fullAddress         = Property(LOCN.fullAddress, rng=Literal)
    poBox               = Property(LOCN.poBox, rng=Literal)
    thoroughfare        = Property(LOCN.thoroughfare, rng=Literal)
    locatorDesignator   = Property(LOCN.locatorDesignator, rng=Literal)
    locatorName         = Property(LOCN.locatorName, rng=Literal)
    addressArea         = Property(LOCN.addressArea, rng=Literal)
    postName            = Property(LOCN.postName, rng=Literal)
    adminUnitL2         = Property(LOCN.adminUnitL2, rng=Literal)
    adminUnitL1         = Property(LOCN.adminUnitL1, rng=Literal)
    postCode            = Property(LOCN.postCode, rng=Literal)
    addressID           = Property(LOCN.addressID, rng=Literal)

    def __init__(self, uri):
        Resource.__init__(self, uri)


@resource(ROV.RegisteredOrganization, "organization")
class Organization(Resource):

    name                = Property(RDFS.label, rng=Property.TEXT, min=1)
    identifier          = Property(ORG.identifier, rng=Literal, min=1)
    type                = Property(ROV.orgType, rng=OrganizationType)
    category            = Property(ORG.classification, rng=OrganizationCategory)
    parent              = Property(ORG.subOrganizationOf)
    address             = Property(LOCN.address, rng=Address)
    phone               = Property(FOAF.phone, rng=URIRef)

    def __init__(self, uri):
        Resource.__init__(self, uri)

Organization.parent.rng = Organization
