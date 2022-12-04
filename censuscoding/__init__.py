"""
Censuscoding, a privacy-preserving alternative to geocoding

https://github.com/ripl-org/censuscoding
"""

import csv
import os
import re
import sys
from bisect import bisect_left
from importlib import resources

from censuscoding.address import tag, normalize_street_num, normalize_street
from censuscoding.log import log
from censuscoding.data import set_lookup_path, load_lookup


__version__ = resources.read_text(__name__, "VERSION").strip()

_nondigit = re.compile(r"[^0-9]")
_pobox = re.compile("box|p ?o ?box|p ?o ?bx")
_unsheltered = re.compile("unshelt|no shelt|no perm|npa|homeless|transient")
_digit = re.compile(r"[0-9]")
_streetnum = re.compile(r"^([1-9][0-9]*)")


def validate_header(header, record_id, zipcode, address):
    """
    Validate that the input file has all required fields in the header.
    """
    if record_id not in header:
        log.error(f"input file is missing record ID field '{record_id}'")
        sys.exit(1)
    if zipcode not in header:
        log.error(f"input file is missing zip code field '{zipcode}'")
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
        log.debug(f"is missing street name")
        return match # Street name is required
    else:
        stats["valid_street"] += 1
    # Extract integer street number
    streetnum = _streetnum.match(streetnum)
    if streetnum is not None:
        streetnum = int(streetnum.group(1))
    if not streetnum:
        log.debug(f"is missing street number")
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
    preserve_rows=False,
    preserve_cols=[]
):
    """
    Determine the Census blockgroup for a street address,
    based on zip code, street name, and street number.
    """
    set_lookup_path()

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
        if preserve_cols:
            header += preserve_cols
        writer.writerow(header)

        # Match records
        for n, record in enumerate(reader, start=1):
            record.update(match_record(
                record.get(record_id, ""),
                record.get(zipcode, ""),
                record.get(address, ""),
                stats
            ))
            if record.get("blkgrp") or preserve_rows:
                writer.writerow([record.get(field, "") for field in header])

    # Print summary
    print_summary(n, stats)
    log.info("Done.")
