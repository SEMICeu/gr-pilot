#!/bin/sh
# Configuration script
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

set -e -u

# Default values
BASEURI="http://data.ydmed.gov.gr/"
ROOTURI="file://gr-pilot/"
GOOGLE_ANALYTICS="UA-38243808-1"

GENERATE=true

# Usage notice
usage() {
    cat <<EOF
Usage: $0 [options]

Options:
  -b URI    The base URI (default: ${BASEURI})
  -r URI    The (internal) URI of the root directory
              (default: ${ROOTURI})
  -a KEY    Google Analytics key (default: ${GOOGLE_ANALYTICS})
  -c        Remove generated files
  -h        This help screen
EOF
}

# Parse arguments
while getopts 'b:r:a:ch' opt; do
    case "${opt}" in
    b) BASEURI=${OPTARG%/}/ ;;
    r) ROOTURI=${OPTARG%/}/ ;;
    a) GOOGLE_ANALYTICS=${OPTARG} ;;
    c) GENERATE=false ;;
    h) usage ; exit 0 ;;
    *) usage ; exit 1 ;;
    esac
done

# Construct sed replacement script
sed=""
for var in BASEURI ROOTURI GOOGLE_ANALYTICS; do
    eval "value=\$${var}"
    sed="${sed}s|%${var}%|${value}|g;"
done

# Generate files
find -name '*.in' |
while read -r infile; do
    outfile=${infile%.in}
    if ${GENERATE}; then
        printf 'Writing %s.\n' "${outfile}"
        cat "${infile}" | sed "${sed}" > "${outfile}"
    elif [ -e "${outfile}" ]; then
        printf 'Removing %s.\n' "${outfile}"
        rm "${outfile}"
    fi
done
