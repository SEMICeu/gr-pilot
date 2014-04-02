# Load input data
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
import logging

from . import dataset
from . import utils

###############################################################################

logging.debug("Loading census.csv")

COLUMNS_CENSUS = {"Αναγνωριστικό": 'pk',
                  "FORGANIKOSFOREAS": 'cid',
                  "FORGNAME": 'name',
                  "WORK_ADDRESS_ID": 'address_id',
                  "STREET_1": 'street1',
                  "NUMBER_1": 'number1',
                  "STREET_2": 'street2',
                  "NUMBER_2": 'number2',
                  "TK": 'postcode',
                  "ADDITIONAL_DESCRIPTION": 'additional_description',
                  "DIMOS_ID": 'municipality_id',
                  "DIMOS": 'municipality',
                  "COUNTRYID": 'country_id',
                  "COUNTRYNAME": 'country'}

def cleanup_census(e):
    # Discard rows with empty names
    if not e.name:
        return False
    # Fix encoding
    e.name = e.name.translate(utils.GREEK_LOOKALIKE)
    # Precompute normalized name
    e.norm = utils.namenorm(e.name)
    return True

census = dataset.Dataset("census.csv", COLUMNS_CENSUS, 'pk', cleanup_census)

census.by_cid = census.create_index('cid')
census.name = census.create_index('cid', 'name', unique=True)
census.cid_by_norm = {utils.namenorm(name):cid
                      for cid, name in census.name.items()}
assert len(census.cid_by_norm) == len(census.name), "Normalized name clash"

###############################################################################

logging.debug("Loading hierarchy.csv")

COLUMNS_HIERARCHY = {"Αναγνωριστικό": 'pk',
                     "ID": 'cid',
                     "EΠIΠEΔΟΞΑΝE": 'name',
                     "FPARENTID": 'parent_cid',
                     "FTYPEID": 'type_id',
                     "INVISIBLE": 'invisible',
                     "Πεδίο6": 'pedio'}

def cleanup_hierarchy(e):
    # Discard rows with empty name or empty cid
    if not e.name or not e.cid:
        return False
    # Fix encoding
    e.name = e.name.translate(utils.GREEK_LOOKALIKE)
    # Precompute normalized name
    e.norm = utils.namenorm(e.name)
    # Fix column shift in some rows
    if e.invisible not in {'', '0', '1'}:
        e.parent_cid = e.type_id
        e.type_id = e.invisible
    # Normalize empty parent
    if e.parent_cid == '0':
        e.parent_cid = ''
    # Discard some types
    return e.type_id not in {'4', '8', '9', '10', '20'}

hierarchy = dataset.Dataset("hierarchy.csv", COLUMNS_HIERARCHY,
                            'cid', cleanup_hierarchy)

hierarchy.by_type = hierarchy.create_index('type_id')
hierarchy.by_norm = hierarchy.create_index('norm')

###############################################################################

logging.debug("Loading hierarchy_types.csv")

COLUMNS_HIERARCHY_TYPES = {"Αναγνωριστικό": 'pk',
                           "ID": 'id',
                           "TYPOSNAME": 'name'}

def cleanup_hierarchy_types(e):
    # Fix encoding
    e.name = e.name.translate(utils.GREEK_LOOKALIKE)
    return True

type_name = {e.id:e.name
             for e in dataset.Dataset("hierarchy_types.csv",
                                      COLUMNS_HIERARCHY_TYPES, 'id',
                                      cleanup_hierarchy_types)}

###############################################################################

logging.debug("Loading transparency.csv")

COLUMNS_TRANSPARENCY = {"Αναγνωριστικό": 'pk',
                        "ΑΦΜ": 'vat',
                        "ΕΠΩΝΥΜΙΑ": 'name',
                        "ΝΟΜΙΚΗ ΜΟΡΦΗ": 'type',
                        "ΕΠΟΠΤΕΥΩΝ": 'parent_name',
                        "ΑΦΜ ΕΠΟΠΤΕΥΟΝΤΟΣ": 'parent_vat',
                        "ID ΦΟΡΕΑ ΔΙΑΥΓΕΙΑ": 'tid',
                        "ID ΦΟΡΕΑ ΑΠΟΓΡΑΦΗ": 'cid'}

def cleanup_transparency(e):
    # Discard rows with empty names
    if not e.name:
        return False
    # Discard rows with empty/invalid VATs
    if not re.match(r"^\d{9}$", e.vat):
        return False
    # Fix encoding
    e.name = e.name.translate(utils.GREEK_LOOKALIKE)
    e.parent_name = e.parent_name.translate(utils.GREEK_LOOKALIKE)
    # Precompute normalized names
    e.norm = utils.namenorm(e.name)
    e.type_norm = utils.namenorm(e.type)
    e.parent_norm = utils.namenorm(e.parent_name)
    # Find additional cid based on name mapping
    if not e.cid and e.norm in census.cid_by_norm:
        e.cid = census.cid_by_norm[e.norm]
    if not e.cid and e.norm in hierarchy:
        e.cid = next(iter(hierarchy.by_norm[e.norm])).cid
    # Discard any entry unknown in census
    return e.cid in census.by_cid

transparency = dataset.Dataset("transparency.csv", COLUMNS_TRANSPARENCY,
                               'pk', cleanup_transparency)

transparency.by_vat = transparency.create_index('vat')
transparency.by_tid = transparency.create_index('tid')
transparency.by_cid = transparency.create_index('cid')
transparency.by_norm = transparency.create_index('norm')

transparency.type_by_typenorm = transparency.create_index('type_norm', 'type')

# Find VAT of parent if only name is given
for e in transparency:
    if not e.parent_vat and e.parent_norm in transparency.by_norm:
        e.parent_vat = next(iter(transparency.by_norm[e.parent_norm])).vat

###############################################################################

logging.debug("Loading syzefxis.csv")

COLUMNS_SYZEFXIS = {"Αναγνωριστικό": 'pk',
                    "AFM": 'vat',
                    "CUSTOMER_NAME": 'name',
                    "EVENT_SOURCE": 'source',
                    "SERVICE_ADDRESS": 'address',
                    "SERVICE_CITY": 'city',
                    "SERVICE_ZIP_CODE": 'zip'}

def cleanup_syzefxis(e):
    # Discard rows with empty names
    if not e.name:
        return False
    # Fix encoding
    e.name = e.name.translate(utils.GREEK_LOOKALIKE)
    # Precompute normalized name
    e.norm = utils.namenorm(e.name)
    return True

syzefxis = dataset.Dataset("syzefxis.csv", COLUMNS_SYZEFXIS,
                           'pk', cleanup_syzefxis)

syzefxis.by_vat = syzefxis.create_index('vat')

###############################################################################

logging.debug("Loading kep.csv")

COLUMNS_KEP = {"kepCode": 'code',
               "name": 'name',
               "apok_dioik": 'administration',
               "perifereia": 'region',
               "perif_enotita": 'prefecture',
               "old_name": 'old_name',
               "adress": 'address',
               "tk": 'postcode',
               "tel": 'phone',
               "fax": 'fax',
               "email": 'email'}

kep = dataset.Dataset("kep.csv", COLUMNS_KEP, 'code')
