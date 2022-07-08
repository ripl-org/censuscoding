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


def validate(record, n, record_id, zip_code, address, stats):
    """
    Validate that the record has all required fields and that
    the zip code is numeric.
    """
    if record_id not in record:
        log.error(f"is missing record_id field '{record_id}'")
        sys.exit(-1)
    if zip_code not in record:
        log.error(f"is missing zip_code field '{zip_code}'")
        sys.exit(-1)
    if address not in record:
        log.error(f"{n} is missing address field '{address}'")
        sys.exit(-1)


def normalize_zip_code(record_id, zip_code, stats):
    """
    Ensure that zip code is 5 digits and 0 padded
    """
    if _nondigit.search(zip_code) is not None or len(zip_code) > 5:
        log.debug(f"record {record_id} as invalid zip code '{zip_code}'")
        return False
    else:
        stats["valid_zip"] += 1
    return zip_code.zfill(5)


def match_special_cases(address, writer, record_id, zip_code, stats):
    """
    Match special cases of non-codable addresses,
    such as PO boxes or unsheltered notes.
    """
    address_lower = address.lower()
    if _pobox.match(address_lower) is not None:
        log.debug(f"record {record_id} address '{address}' is PO box")
        writer.writerow((record_id, zip_code, "", "1", "0"))
        stats["match_pobox"] += 1
        return True
    elif _unsheltered.match(address_lower) is not None and _digit.match(address_lower) is None:
        log.debug(f"record {record_id} address '{address}' is unsheltered")
        writer.writerow((record_id, zip_code, "", "0", "1"))
        stats["match_unsheltered"] += 1
        return True
    else:
        return False


def extract_address(address):
    """
    """
    tags = tag(address)
    return normalize_street_num(tags), normalize_street(tags)


def censuscode(
    in_file, 
    out_file,
    record_id="record_id",
    zip_code="zip_code", 
    address="address"
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
        sys.exit(-1)

    stats = {
        "valid_zip": 0,
        "valid_street": 0,
        "valid_street_num": 0,
        "match_pobox": 0,
        "match_unsheltered": 0,
        "match_street": 0,
        "match_street_num": 0
    }

    with open(in_file, "r", encoding="utf8") as fin, open(out_file, "w") as fout:

        # CSV reader/writer
        reader = csv.DictReader(fin)
        writer = csv.writer(fout)
        writer.writerow((record_id, "zip_code", "blkgrp", "pobox", "unsheltered"))

        # Parse records
        for n, record in enumerate(reader, start=1):
            # Prefix log entries for this record
            log.set_prefix(f"record {record_id}")
            validate(record, n, record_id, zip_code, address, stats)
            zip5 = normalize_zip_code(record_id, record[zip_code], stats)
            if not zip5:
                continue # Can't match without zip code
            if match_special_cases(record[address], writer, record[record_id], zip5, stats):
                continue # Special cases cannot be censuscoded to a block group
            street_num, street = extract_address(record[address])
            if not street:
                log.debug(f"record {record_id} is missing street name")
                continue # Street name is required
            else:
                stats["valid_street"] += 1
            if not street_num:
                log.debug(f"record {record_id} is missing street number")
                # Street number is not required, if there is a match on street name
            else:
                stats["valid_street_num"] += 1
            # Lookup block group
            zip2 = zip5[:2]
            zip3 = zip5[2:]
            lookup = load_lookup(zip2)
            if zip3 in lookup:
                if street in lookup[zip3]:
                    result = lookup[zip3][street]
                    if isinstance(result, str):
                        # Match on street name
                        writer.writerow((record[record_id], zip5, result, "0", "0"))
                        stats["match_street"] += 1
                    elif street_num:
                        try:
                            street_num = int(street_num)
                        except:
                            log.debug(f"record {record_id} has lookup but street_num is non-numeric")
                            continue
                        # Binary search in street_num range
                        nums = result[0]
                        blkgrps = result[1]
                        i = bisect_left(nums, street_num)
                        if (i > 0 and i < len(blkgrps)) or (i == 0 and nums[0] == street_num) or (i == len(blkgrps) and nums[-1] == street_num):
                            writer.writerow((record[record_id], zip5, blkgrps[i], "0", "0"))
                            stats["match_street_num"] += 1
                    else:
                        log.debug(f"record {record_id} has lookup but is missing street_num")

    # Print summary stats
    log.set_prefix("")
    percent = lambda x: (100.0 * x) / n
    log.info("processed {:d} records:".format(n))
    log.info("  {:,d} ({:.1f}%) with valid zip code".format(stats["valid_zip"], percent(stats["valid_zip"])))
    log.info("  {:,d} ({:.1f}%) with normalized street name".format(stats["valid_street"], percent(stats["valid_street"])))
    log.info("  {:,d} ({:.1f}%) with normalized street number".format(stats["valid_street_num"], percent(stats["valid_street_num"])))
    log.info("  {:,d} ({:.1f}%) matched on street name".format(stats["match_street"], percent(stats["match_street"])))
    log.info("  {:,d} ({:.1f}%) matched on street number".format(stats["match_street_num"], percent(stats["match_street_num"])))
    log.info("overall match rate: {:.1f}%".format(percent(stats["match_street"] + stats["match_street_num"])))
    log.info("Done.")
