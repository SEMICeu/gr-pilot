# Miscellaneous utilities
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

import re
import unicodedata


# Translation table mapping ASCII characters to their Greek lookalike
# counterpart
GREEK_LOOKALIKE = str.maketrans("ABEZHIKMNOPTYX", "ΑΒΕΖΗΙΚΜΝΟΡΤΥΧ")


def strip_diacritics(s):
    '''Return s without diacritics.'''
    return u"".join(c for c in unicodedata.normalize('NFKD', s)
                      if not unicodedata.combining(c))


def namenorm(name):
    '''Return a normalized version of name.'''
    name = strip_diacritics(name)
    name = name.upper()
    name = name.translate(GREEK_LOOKALIKE)
    name = re.sub(r"\W", "", name)
    return name


def isincluded(s1, s2):
    '''Return True if s1 is fully included in s2.'''
    i = 0
    for c in s2:
        if i == len(s1):
            break
        if c == s1[i]:
            i += 1
    return i == len(s1)


class AutoDict(dict):

    '''A dictionary that automatically creates new entries when requesting an
    unknown key.'''

    def __init__(self, cls):
        '''Automatically create keys of type cls. The constructor of cls shall
        take one argument: the key.'''
        self._newcls = cls

    def __getitem__(self, key):
        if key not in self:
            self[key] = self._newcls(key)
        return super().__getitem__(key)
