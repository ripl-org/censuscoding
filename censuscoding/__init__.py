"""
Censuscoding: determine the Census blockgroup for a street address

https://github.com/ripl-org/censuscoding
"""

import csv
import os
import pickle
import re
import sys

from .address import tag, normalize_street_num, normalize_street
from .log import log

from bisect import bisect_left
from importlib import resources
from pkg_resources import resource_stream

__version__ = resources.read_text(__name__, "VERSION").strip()
_nondigit = re.compile(r"[^0-9]")
_pobox = re.compile("box|p ?o ?box|p ?o ?bx")
_unsheltered = re.compile("unshelt|no shelt|no perm|npa|homeless|transient")
_digit = re.compile(r"[0-9]")
_lookup_path = os.getenv("CENSUSCODING_DATA")
_lookups = {}


def set_lookup_path(path):
    """
    Set an alternative path to the directory containing the lookup files
    (e.g. for testing or comparing lookups).
    """
    global _lookup_path
    _lookup_path = os.path.abspath(path)


def load_lookup(zip2):
    """
    Lazy loading of lookup files by first 2 digits of zip code.
    """
    global _lookups
    if zip2 not in _lookups:
        log.info(f"loading lookup {zip2}")
        if _lookup_path:
            with open(f"{_lookup_path}/{zip2}", "rb") as f:
                _lookups[zip2] = pickle.load(f)
        else:
            _lookups[zip2] = pickle.load(resource_stream(__name__, f"data/{zip2}"))
    return _lookups[zip2]


def validate_header(header, record_id, zipcode, address):
    """
    Validate that the input file has all required fields in the header.
    """
    if record_id not in header:
        log.error(f"input file is missing record_id field '{record_id}'")
        sys.exit(1)
    if zipcode not in header:
        log.error(f"input file is missing zip_code field '{zipcode}'")
        sys.exit(1)
    if address not in header:
        log.error(f"input file is missing address field '{address}'")
        sys.exit(1)


def normalize_zipcode(record_id, zipcode, stats):
    """
    Ensure that zip code is 5 digits and 0 padded
    """
    if _nondigit.search(zipcode) is not None or len(zipcode) > 5:
        log.debug(f"record {record_id} has invalid zip code '{zipcode}'")
        return ""
    else:
        stats["valid_zipcode"] += 1
        return zipcode.zfill(5)


def match_special_cases(record_id, address, match, stats):
    """
    Match special cases of non-codable addresses,
    such as PO boxes or unsheltered notes.
    """
    address_lower = address.lower()
    if _pobox.match(address_lower) is not None:
        log.debug(f"record {record_id} address '{address}' is PO box")
        match["pobox"] = "1"
        stats["match_pobox"] += 1
        return True
    elif _unsheltered.match(address_lower) is not None and _digit.match(address_lower) is None:
        log.debug(f"record {record_id} address '{address}' is unsheltered")
        match["unsheltered"] = "1"
        stats["match_unsheltered"] += 1
        return True
    else:
        return False


def extract_address(address):
    """
    """
    tags = tag(address)
    return normalize_street_num(tags), normalize_street(tags)


def match_record(record_id, zipcode, address, stats):
    """
    """
    log.set_prefix(f"record {record_id}")
    match = {
        "id": record_id,
        "zipcode": normalize_zipcode(record_id, zipcode, stats)
    }
    if not match["zipcode"]:
        return match # Can't match without zip code
    if match_special_cases(record_id, address, match, stats):
        return match # Special cases cannot be censuscoded to a block group
    streetnum, street = extract_address(address)
    if not street:
        log.debug(f"record {record_id} is missing street name")
        return match # Street name is required
    else:
        stats["valid_street"] += 1
    if not streetnum:
        log.debug(f"record {record_id} is missing street number")
        # Street number is not required, if there is a match on street name
    else:
        stats["valid_streetnum"] += 1
    # Lookup block group
    zip2 = match["zipcode"][:2]
    zip3 = match["zipcode"][2:]
    lookup = load_lookup(zip2)
    if zip3 in lookup:
        if street in lookup[zip3]:
            result = lookup[zip3][street]
            if isinstance(result, str):
                match["blkgrp"] = result
                stats["match_street"] += 1
            elif streetnum:
                try:
                    streetnum = int(streetnum)
                except:
                    log.debug(f"record {record_id} has non-numeric street number")
                    return match
                # Binary search in streetnum range
                nums = result[0]
                blkgrps = result[1]
                i = bisect_left(nums, streetnum)
                if (i > 0 and i < len(blkgrps)) or (i == 0 and nums[0] == streetnum) or (i == len(blkgrps) and nums[-1] == streetnum):
                    match["blkgrp"] = blkgrps[i]
                    stats["match_streetnum"] += 1
    return match


def print_summary(n, stats):
    # Print summary stats
    percent = lambda x: (100.0 * x) / n
    log.info("processed {:,d} records:".format(n))
    log.info("  {:,d} ({:.1f}%) with valid zip code".format(
        stats["valid_zipcode"],
        percent(stats["valid_zipcode"]
    )))
    log.info("  {:,d} ({:.1f}%) with normalized street name".format(
        stats["valid_street"],
        percent(stats["valid_street"]
    )))
    log.info("  {:,d} ({:.1f}%) with normalized street number".format(
        stats["valid_streetnum"],
        percent(stats["valid_streetnum"]
    )))
    log.info("  {:,d} ({:.1f}%) matched on street name".format(
        stats["match_street"],
        percent(stats["match_street"]
    )))
    log.info("  {:,d} ({:.1f}%) matched on street number".format(
        stats["match_streetnum"],
        percent(stats["match_streetnum"]
    )))
    log.info("overall match rate: {:.1f}%".format(
        percent(stats["match_street"] + stats["match_streetnum"]
    )))


def censuscode(
    in_file, 
    out_file,
    record_id="record_id",
    zipcode="zipcode", 
    address="address",
    preserve=False
):
    """
    Determine the Census blockgroup for a street address,
    based on zip code, street name, and street number.
    """
    global _lookup_path

    if _lookup_path:
        _lookup_path = os.path.abspath(_lookup_path)
        log.info(f"using lookup files from", _lookup_path)

    log.info("censuscoding", in_file)

    if not os.path.exists(in_file):
        log.error(f"file {in_file} does not exist!")
        sys.exit(1)

    stats = {
        "valid_zipcode"     : 0,
        "valid_street"      : 0,
        "valid_streetnum"   : 0,
        "match_pobox"       : 0,
        "match_unsheltered" : 0,
        "match_street"      : 0,
        "match_streetnum"   : 0,
    }

    with open(in_file, "r", encoding="utf8") as fin, open(out_file, "w") as fout:

        # CSV reader
        reader = csv.DictReader(fin)
        validate_header(reader.fieldnames, record_id, zipcode, address)

        # CSV writer
        writer = csv.writer(fout)
        header = ["id", "zipcode", "blkgrp", "pobox", "unsheltered"]
        writer.writerow(header)

        # Match records
        for n, record in enumerate(reader, start=1):
            match = match_record(
                record.get(record_id, ""),
                record.get(zipcode, ""),
                record.get(address, ""),
                stats
            )
            if match or preserve:
                writer.writerow([match.get(field, "") for field in header])

    # Print summary
    log.set_prefix("")
    print_summary(n, stats)
    log.info("Done.")
