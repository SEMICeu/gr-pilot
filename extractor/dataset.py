# Input data model
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

import os.path
import csv
import re


DATA_DIR = "data"


class Entry:

    '''An entry in a Dataset.'''

    def __init__(self, row, propnames):
        '''Initialize an entry.

        Arguments:
        row -- row of data
        propnames -- list of property names
        '''
        self._propnames = propnames
        for name, value in zip(propnames, row):
            value = value.strip()
            value = re.sub(r"^([0-9]+)\.0+$", r"\1", value)  # int as doubles
            if value == "NULL":
                value = ''
            setattr(self, name, value)

    def __eq__(self, o):
        return isinstance(o, Entry) and \
               self._propnames == o._propnames and \
               all(getattr(self, name) == getattr(o, name)
                   for name in self._propnames)

    def __hash__(self):
        return hash(tuple(getattr(self, name) for name in self._propnames))

    def __repr__(self):
        return "<Entry: " + ", ".join(name + "=" + repr(getattr(self, name))
                                      for name in self._propnames) + ">"


class Dataset:

    '''The Dataset class represents an input dataset.'''

    def __init__(self, filename, headermap, pkname, cleanup=None):
        '''Load a dataset from a CSV file.

        Arguments:
        filename -- the name of the CSV file in the data directory
        headermap -- a dictionnary mapping column names to property names
        pkname -- property name of the primary key
        cleanup -- a function taking as single argument an entry to clean;
            the function should return True to accept the entry, and False to
            reject it
        '''
        with open(os.path.join("data", filename), newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            propnames = [headermap[name] for name in header]
            self.entries = []
            for row in reader:
                entry = Entry(row, propnames)
                if cleanup is None or cleanup(entry):
                    self.entries.append(entry)
        self._pk_index = self.create_index(pkname, unique=True)

    def create_index(self, keyname, valuename=None, unique=False):
        '''Return an index dictionary for the property keyname. The values are
        taken from property valuename or the entire entry if valuename is None.
        If unique is False, sets of values are stored in the dictionary.
        Entries with empty keys are ignored.'''
        result = {}
        for e in self.entries:
            key = getattr(e, keyname)
            if not key:
                continue
            value = getattr(e, valuename) if valuename else e
            if unique:
                assert key not in result or result[key] == value, "Not unique"
                result[key] = value
            else:
                if key not in result:
                    result[key] = set()
                result[key].add(e)
        return result

    def __getitem__(self, key):
        return self._pk_index[key]

    def __contains__(self, key):
        return key in self._pk_index

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)
