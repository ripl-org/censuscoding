"""
Censuscoding: determine the Census blockgroup for a street address

https://github.com/ripl-org/censuscoding
"""

import logging
import numpy as np
import pandas as pd
import usaddress
from importlib import resources

__version__ = resources.read_text(__name__, "VERSION").strip()


class Log(object):
    """
    Extends the built-in logging module to support
    """

    def __init__(self, *names):
        self.name = ":".join(names)
        self.log = logging.getLogger(self.name)

    def debug(self, *message, sep=" "):
        self.log.debug(" {}".format(sep.join(map(str, message))))

    def error(self, *message, sep=" "):
        self.log.error(" {}".format(sep.join(map(str, message))))

    def info(self, *message, sep=" "):
        self.log.info(" {}".format(sep.join(map(str, message))))

    def warn(self, *message, sep=" "):
        self.log.warn(" {}".format(sep.join(map(str, message))))


def split_address(address):
    """
    Run usaddress tag method on full street address field to
    split it into street name and number.
    """
    try:
        return usaddress.tag(address)[0]
    except usaddress.RepeatedLabelError:
        return usaddress.tag("")[0]


def censuscode(
    in_file, out_file,
    lookup_streets, lookup_nums, geo_level="blkgrp",
    record_id="record_id", zip_code="zip_code", address="address", street="street", street_num="street_num"
):
    """
    Determine the Census blockgroup for a street address,
    based on zip code, street name, and street number.
    """

    info = Log(__name__, "censuscode").info
    info("Censuscoding", in_file)

    addresses = pd.read_csv(
        in_file,
        low_memory=False,
        usecols=[record_id, zip_code, address]
    )
    N = [len(addresses)]

    info("Parsing street name and number from address field")
    parsed = pd.DataFrame(addresses[address].str.upper().str.extract("([0-9A-Z ]+)", expand=False).fillna("").apply(split_address).tolist())
    if "StreetNamePreDirectional" in parsed.columns:
        addresses[street] = np.where(parsed.StreetNamePreDirectional.notnull(), parsed.StreetNamePreDirectional + " " + parsed.StreetName, parsed.StreetName)
    else:
        addresses[street] = parsed.StreetName
    addresses[street_num] = np.where(parsed.AddressNumber.str.isdigit(), parsed.AddressNumber, np.nan)

    with open(out_file + ".log", "w") as log:

        info("Loading lookup files")
        streets = lookup_streets.drop_duplicates(["street", "zip"])
        print(len(streets), "distinct street names", file=log)
        nums = lookup_nums.drop_duplicates(["street_num", "street", "zip"])
        print(len(nums), "distinct street name/numbers", file=log)

        info("Building range look-up for street nums")
        num_lookup = {}
        for index, group in nums.groupby(["street", "zip"]):
            group = group.sort_values("street_num")
            num_lookup[index] = (group["street_num"].values, group[geo_level].values)
        print(len(num_lookup), "look-ups for street number ranges", file=log)

        info("Filtering records with non-missing zip codes")
        addresses = addresses[addresses[zip_code].notnull()]
        N.append(len(addresses))
        print(N[-1], "records with non-missing zip codes", file=log)

        info("Filtering records with valid integer zip codes")
        if addresses[zip_code].dtype == "O":
            addresses[zip_code] = addresses[zip_code].str.extract("(\d+)", expand=False)
            addresses = addresses[addresses[zip_code].notnull()]
        addresses[zip_code] = addresses[zip_code].astype(int)
        addresses = addresses[addresses[zip_code].isin(streets.zip.unique())]
        N.append(len(addresses))
        print(N[-1], "records with valid integer zip codes", file=log)

        info("Filtering records with valid street names")
        addresses[street] = addresses[street].str.upper().str.extract("([0-9A-Z ]+)", expand=False)
        addresses = addresses[addresses[street].notnull()]
        N.append(len(addresses))
        print(N[-1], "records with valid street names", file=log)

        info("Merge 1 on distinct street name")
        addresses = addresses.merge(streets,
                                    how="left",
                                    left_on=[street, zip_code],
                                    right_on=["street", "zip"],
                                    validate="many_to_one")
        assert len(addresses) == N[-1]
        merged = addresses[geo_level].notnull()
        addresses.loc[merged, [record_id, zip_code, geo_level]].to_csv(out_file, float_format="%.0f", index=False)
        print("merged", merged.sum(), "records on distinct street name", file=log)

        # Remove merged addresses.
        addresses = addresses[~merged]
        del addresses[geo_level]
        N.append(len(addresses))
        print(N[-1], "records remaining", file=log)

        # Keep records with valid integer street nums.
        if addresses[street_num].dtype == "O":
            addresses[street_num] = addresses[street_num].str.extract("(\d+)", expand=False)
        addresses = addresses[addresses[street_num].notnull()]
        addresses[street_num] = addresses[street_num].astype(int)
        N.append(len(addresses))
        print(N[-1], "records with valid integer street nums", file=log)

        info("Merge 2 on distinct street name/num")
        addresses = addresses.merge(nums,
                                    how="left",
                                    left_on=[street_num, street, zip_code],
                                    right_on=["street_num", "street", "zip"],
                                    validate="many_to_one")
        assert len(addresses) == N[-1]
        merged = addresses[geo_level].notnull()
        addresses.loc[merged, [record_id, zip_code, geo_level]].to_csv(out_file, float_format="%.0f", index=False, mode="a", header=False)
        print("merged", merged.sum(), "records on distinct street name/num", file=log)

        # Remove merged addresses.
        addresses = addresses[~merged]
        del addresses[geo_level]
        N.append(len(addresses))
        print(N[-1], "records remaining", file=log)

        info("Merge 3 with street number range search")
        merged = []
        for _, row in addresses.iterrows():
            l = num_lookup.get((row[street], row[zip_code]))
            if l is not None:
                i = np.searchsorted(l[0], row[street_num], side="right")
                merged.append((row[record_id], row[zip_code], l[1][max(0, i-1)]))
        print("merged", len(merged), "records on nearest street name/num", file=log)
        with open(out_file, "a") as f:
            for row in merged:
                print(*row, sep=",", file=f)
        N.append(N[-1] - len(merged))
        print(N[-1], "records remain unmerged", file=log)
        print("overall match rate: {:.1f}%".format(100.0 * (N[0] - (N[0] - N[2]) - N[-1]) / N[0]), file=log)

    info("Done.")
