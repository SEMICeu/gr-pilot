# RDF utilities
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
import rdflib

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, OWL, SKOS, DCTERMS, FOAF

ORG = rdflib.Namespace("http://www.w3.org/ns/org#")
ROV = rdflib.Namespace("http://www.w3.org/ns/regorg#")
LOCN = rdflib.Namespace("http://www.w3.org/ns/locn#")

BASE_URI = "http://data.ydmed.gov.gr/id/"


class Graph(rdflib.Graph):

    '''An RDF graph somewhat specialized.'''

    def __init__(self, data=None):
        rdflib.Graph.__init__(self)
        self.bind('rdf', str(RDF))
        self.bind('rdfs', str(RDFS))
        self.bind('xsd', str(XSD))
        self.bind('owl', str(OWL))
        self.bind('skos', str(SKOS))
        self.bind('dcterms', str(DCTERMS))
        self.bind('foaf', str(FOAF))
        self.bind('org', str(ORG))
        self.bind('rov', str(ROV))
        self.bind('locn', str(LOCN))
        if data is not None:
            self.add(data)

    def add(self, item, memo=None):
        if memo is None:
            memo = set()
        if isinstance(item, tuple):
            super().add(item)
        elif isinstance(item, Resource):
            item._add_to_graph(self, memo)
        else:
            for it in item:
                self.add(it, memo)

    def query(self, *args, **kwargs):
        result = super().query(*args, **kwargs)
        if result.graph is not None:
            g = Graph()
            g += result.graph
            result.graph = g
        return result

    def update(self, query):
        query = "".join("PREFIX " + name + ": <" + str(uri) + ">\n"
                        for name, uri in self.namespaces()) + query
        super().update(query)


class Property:

    '''Property of a domain model class.

    Attributes:
    name -- the name of the property (set by @resource)
    resource_cls -- the containing resource class (set by @resource)
    uri -- the URIRef of the property
    rng -- the range: a namespace, a class, a special value, or None; multiple
           options may be given in a tuple
    min -- the minimum cardinality
    max -- the maximum cardinality or None if infinite
    '''

    # Range of Literals with mandatory language tags
    TEXT = "text"

    # Range of Literals with mandatory unique language tags
    UNIQUETEXT = "unique text"

    def __init__(self, uri, rng=None, min=0, max=None):
        assert isinstance(uri, URIRef)
        self.uri = uri
        self.rng = rng
        self.min = min
        self.max = max

    def __str__(self):
        return self.resource_cls.__name__ + '.' + self.name

    def __repr__(self):
        return '<Property ' + str(self) + '>'

    def __hash__(self):
        return hash(self.resource_cls) | hash(self.name)

    def __eq__(self, obj):
        if obj is None or not isinstance(obj, self.__class__):
            return False
        return self.resource_cls == obj.resource_cls and self.name == obj.name

    def _to_rdf(self, value):
        '''Return the RDF value of value.'''
        if isinstance(value, rdflib.term.Identifier):
            return value
        elif isinstance(value, Resource):
            return value.uri
        else:
            return Literal(value)

    def validate(self, resource, deep=True, result=None):
        '''Validate this property.

        Arguments:
        resource -- the subject (a Resource's subclass instance)
        deep -- if True, validate values recursively
        result -- the ValidationResult object
        '''
        assert isinstance(resource, self.resource_cls)
        if result is None:
            result = ValidationResult()
        values = resource.get_values(self)
        # Check cardinality
        if len(values) < self.min:
            result.add(self, "Missing values", resource, len(values), self.min)
        elif self.max is not None and len(values) > self.max:
            result.add(self, "Too many values", resource, len(values), self.max)
        # Check individual values
        for value in values:
            # Recursive check
            if deep and isinstance(value, Resource):
                value.validate(deep=deep, result=result)
            # Range check
            if self.rng is not None:
                ranges = self.rng
                if not isinstance(ranges, tuple):
                    ranges = (ranges,)
                obj = self._to_rdf(value)
                for rng in ranges:
                    if rng in (Property.TEXT, Property.UNIQUETEXT):
                        if isinstance(obj, Literal) and obj.language is not None:
                            break
                    elif isinstance(rng, rdflib.Namespace):
                        if isinstance(obj, URIRef) and obj.startswith(rng):
                            break
                    elif issubclass(rng, rdflib.term.Identifier):
                        if isinstance(obj, rng):
                            break
                    elif issubclass(rng, Resource):
                        if isinstance(value, rng) or isinstance(obj, URIRef):
                            break
                    elif isinstance(obj, Literal):
                        if isinstance(obj.toPython(), rng):
                            break
                else:
                    result.add(self, "Wrong type", resource,
                               obj.n3(), self.rng)
        # Check for unique language tags
        if self.rng == Property.UNIQUETEXT:
            languages = set()
            reported = False
            for value in values:
                if isinstance(value, Literal) and value.language is not None:
                    if not reported and value.language in languages:
                        result.add(self, "Multiple values for a language",
                                   resource, value.n3())
                        reported = True
                    languages.add(value.language)
            if languages and "en" not in languages:
                result.add(self, "Missing English translation", resource,
                           "/".join(languages))
        return result

    def _add_to_graph(self, resource, g, memo):
        for value in resource.get_values(self):
            if isinstance(value, Resource):
                value._add_to_graph(g, memo)
            g.add((resource.uri, self.uri, self._to_rdf(value)))


class Resource:

    '''Super-class for domain model classes.
    All subclasses shall have the @resource(uri) decorator.

    Values for properties may be None, a single value, or a set of values.
    '''

    def __init__(self, uri):
        if not isinstance(uri, URIRef):
            if self.CONCEPT_NAME:
                uri = self.CONCEPT_NAME + "/" + str(uri)
            uri = URIRef(BASE_URI + str(uri))
        self.uri = uri
        for name, prop in self.properties():
            setattr(self, name, set())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' ' + str(self.uri) + '>'

    def __hash__(self):
        return hash(self.uri)

    def __eq__(self, obj):
        if obj is None or not isinstance(obj, self.__class__):
            return False
        return self.uri == obj.uri

    @classmethod
    def properties(cls):
        '''Yield all (name, properties) tuples of this resource.'''
        for name, prop in cls.__dict__.items():
            if isinstance(prop, Property):
                yield (name, prop)

    def get_values(self, prop):
        '''Return the set of values for property prop (a string or Property
        instance).'''
        if isinstance(prop, Property):
            prop = prop.name
        values = getattr(self, prop)
        if values is None:
            values = set()
        elif not isinstance(values, set):
            values = {values}
        else:
            values = values.copy()
        return values

    def validate(self, deep=True, result=None):
        '''Validate this resource and all its values recursively.

        Arguments:
        deep -- if True, validate values recursively
        result -- the ValidationResult object
        '''
        if result is None:
            result = ValidationResult()
        if self in result.checked:
            return result
        result.checked.add(self)
        for name, prop in self.properties():
            prop.validate(self, deep=deep, result=result)
        if hasattr(self, '_validate'):
            self._validate(result)
        return result

    def _add_to_graph(self, g, memo):
        '''Add this resource and all depending ones to the graph g.'''
        if self.uri in memo:
            return
        memo.add(self.uri)
        g.add((self.uri, RDF.type, self.TYPE_URI))
        for name, prop in self.properties():
            prop._add_to_graph(self, g, memo)


def resource(uri, concept=None):
    '''Decorator for Resource.

    Arguments:
    uri -- the type URIs of the resource
    concept -- the abbreviated concept name to be used in URIs
    '''
    assert isinstance(uri, URIRef)
    def f(cls):
        cls.TYPE_URI = uri
        cls.CONCEPT_NAME = concept
        for name, prop in cls.properties():
            prop.name = name
            prop.resource_cls = cls
        return cls
    return f


class ValidationResult:

    '''The result of a validation.'''

    def __init__(self):
        self.errors = {}
        self.checked = set()  # set of checked resources

    def __bool__(self):
        return not self.errors

    def add(self, prop, message, resource, actual, expected=None):
        '''Add a validation error.'''
        key = (prop, message)
        value = (resource, actual, expected)
        if key not in self.errors:
            self.errors[key] = []
        self.errors[key].append(value)

    def log(self):
        '''Write the validation errors to the log.'''
        for (prop, message), instances in self.errors.items():
            instances = ["(" + str(resource.uri) + " has " + str(actual) +
                         (", expected " + str(expected) if expected else "") +
                         ")"
                         for resource, actual, expected in instances]
            line = str(prop) + ": " + message + " " + ", ".join(instances[:3])
            if len(instances) > 3:
                line += ", and %d more" % (len(instances) - 3)
            logging.warning(line)
            logging.debug("All errors: " + ", ".join(instances))


def validate(*resourceslist):
    '''Validate collections of resources.'''
    result = ValidationResult()
    for resources in resourceslist:
        if isinstance(resources, Resource):
            resources.validate(result=result)
        else:
            for resource in resources:
                resource.validate(result=result)
    return result
