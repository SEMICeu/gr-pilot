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

logging.debug("Loading transparency.csv")

COLUMNS_TRANSPARENCY = {"Αναγνωριστικό": 'pk',
                        "ΑΦΜ": 'vat',
                        "ΕΠΩΝΥΜΙΑ": 'name',
                        "ΝΟΜΙΚΗ ΜΟΡΦΗ": 'type',
                        "ΕΠΟΠΤΕΥΩΝ": 'parent_name',
                        "ΑΦΜ ΕΠΟΠΤΕΥΟΝΤΟΣ": 'parent_vat',
                        "ID ΦΟΡΕΑ ΔΙΑΥΓΕΙΑ": 'tid',
                        "ID ΦΟΡΕΑ ΑΠΟΓΡΑΦΗ": 'cid'}

TRANSPARENCY_CIDFIX = {'2565': '7412',  # ΑΝΤΙΚΑΡΚΙΝΙΚΟ ΝΟΣΟΚΟΜΕΙΟ ΘΕΣΣΑΛΟΝΙΚΗΣ "ΘΕΑΓΕΝΕΙΟ"
                       '2567': '7862',  # ΓΕΝΙΚΟ ΑΝΤΙΚΑΡΚΙΝΙΚΟ  ΝΟΣΟΚΟΜΕΙΟ ΑΘΗΝΩΝ " ΑΓΙΟΣ ΣΑΒΒΑΣ"
                       '3115': '7891'}  # ΤΑΜΕΙΟ ΕΘΝΙΚΗΣ ΑΜΥΝΑΣ

def cleanup_transparency(e):
    # Discard rows with empty names
    if not e.name:
        return False
    # Precompute normalized name
    e.norm = utils.namenorm(e.name)
    # Normalize empty VATs
    if e.vat == '-' or re.match(r"^x+$", e.vat):
        e.vat = ''
    # Fix/find cid based on name mapping
    if e.norm in census.cid_by_norm:
        e.cid = census.cid_by_norm[e.norm]
    # Fix some cid
    if e.pk in TRANSPARENCY_CIDFIX:
        e.cid = TRANSPARENCY_CIDFIX[e.pk]
    return True

transparency = dataset.Dataset("transparency.csv", COLUMNS_TRANSPARENCY,
                               'pk', cleanup_transparency)

transparency.by_vat = transparency.create_index('vat')
transparency.by_tid = transparency.create_index('tid')
transparency.by_cid = transparency.create_index('cid')

for vat in [vat for vat in transparency.by_vat if not vat.isdigit()]:
    entries = transparency.by_vat[vat]
    del transparency.by_vat[vat]
    if re.match(r"^\d+-\d+$", vat):
        start, end = vat.split('-')
        vats = [str(i) for i in range(int(start), int(end)+1)]
        del start, end
    else:
        vats = re.findall(r"\d{9}", vat)
    for vat in vats:
        if vat not in transparency.by_vat:
            transparency.by_vat[vat] = set()
        transparency.by_vat[vat].update(entries)
del entries, vat, vats

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
    # Precompute normalized name
    e.norm = utils.namenorm(e.name)
    return True

syzefxis = dataset.Dataset("syzefxis.csv", COLUMNS_SYZEFXIS,
                           'pk', cleanup_syzefxis)

syzefxis.by_vat = syzefxis.create_index('vat')

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
    # Precompute normalized name
    e.norm = utils.namenorm(e.name)
    # Fix column shift in some rows
    if e.invisible not in {'', '0', '1'}:
        e.parent_id = e.type_id
        e.type_id = e.invisible
    # Discard some types
    return e.type_id not in {'8', '9', '10'}

hierarchy = dataset.Dataset("hierarchy.csv", COLUMNS_HIERARCHY,
                            'cid', cleanup_hierarchy)

hierarchy.by_type = hierarchy.create_index('type_id')
hierarchy.by_norm = hierarchy.create_index('norm')

###############################################################################

logging.debug("Loading hierarchy_types.csv")

COLUMNS_HIERARCHY_TYPES = {"Αναγνωριστικό": 'pk',
                           "ID": 'id',
                           "TYPOSNAME": 'name'}

type_name = {e.id:e.name
             for e in dataset.Dataset("hierarchy_types.csv",
                                      COLUMNS_HIERARCHY_TYPES, 'id')}

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
